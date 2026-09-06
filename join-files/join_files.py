#!/usr/bin/env python3
"""
join_files.py

Joins the text content of all files inside an input folder into a single
output file. Supports recursive traversal and extension filtering.

Configuration is loaded from config.json (input_dir, output_dir, output_filename,
recursive, extensions, encoding, separator, include_filename_header). CLI flags
are optional and override the corresponding config.json value when supplied.

Usage examples (run from the repository root):

    # Use everything from config.json as-is
    python join_files.py

    # Point to a different config file
    python join_files.py --config my_config.json

    # Override individual config.json values from the CLI
    python join_files.py --input-dir other_input --recursive
"""

from __future__ import annotations

import argparse
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

DEFAULT_CONFIG_PATH = Path("config.json")


class ConfigLoader:
    """Loads config.json into a SimpleNamespace for dot-notation access."""

    REQUIRED_KEYS = ("input_dir", "output_dir", "output_filename")

    def __init__(self, config_path: Path = DEFAULT_CONFIG_PATH):
        self.config_path = Path(config_path)

    def load(self) -> SimpleNamespace:
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Config file not found: {self.config_path}. "
                "Create one (see config.json in the repo) before running."
            )

        with self.config_path.open(encoding="utf-8") as fh:
            raw = json.load(fh)

        missing = [key for key in self.REQUIRED_KEYS if key not in raw]
        if missing:
            raise ValueError(f"config.json is missing required key(s): {missing}")

        # sensible defaults for optional keys
        raw.setdefault("recursive", False)
        raw.setdefault("extensions", None)
        raw.setdefault("encoding", "utf-8")
        raw.setdefault("encoding_fallbacks", ["utf-8-sig", "utf-16", "cp1252", "latin-1"])
        raw.setdefault(
            "exclude_dirs",
            [".git", "__pycache__", ".venv", "venv", "node_modules",
             ".mypy_cache", ".pytest_cache", ".idea", ".vscode"],
        )
        raw.setdefault("separator", "\n\n")
        raw.setdefault("include_filename_header", True)

        logger.info("Loaded config from %s", self.config_path)
        return SimpleNamespace(**raw)


@dataclass
class FileJoinerConfig:
    """Configuration for a FileJoiner run."""

    input_dir: Path
    output_file: Path
    recursive: bool = False
    extensions: Optional[list[str]] = None  # e.g. [".py", ".md"]
    encoding: str = "utf-8"
    encoding_fallbacks: Optional[list[str]] = None  # tried in order if `encoding` fails
    exclude_dirs: Optional[list[str]] = None  # directory names to prune during recursive walk
    separator: str = "\n\n"  # inserted between joined file contents
    include_filename_header: bool = True

    def __post_init__(self) -> None:
        self.input_dir = Path(self.input_dir)
        self.output_file = Path(self.output_file)
        if self.extensions:
            # normalize to lowercase, ensure leading dot
            self.extensions = [
                ext.lower() if ext.startswith(".") else f".{ext.lower()}"
                for ext in self.extensions
            ]
        self.exclude_dirs = set(self.exclude_dirs or [])

    @classmethod
    def from_namespace(cls, ns: SimpleNamespace) -> "FileJoinerConfig":
        output_file = Path(ns.output_dir) / ns.output_filename
        return cls(
            input_dir=ns.input_dir,
            output_file=output_file,
            recursive=ns.recursive,
            extensions=ns.extensions,
            encoding=ns.encoding,
            encoding_fallbacks=getattr(ns, "encoding_fallbacks", None),
            exclude_dirs=getattr(ns, "exclude_dirs", None),
            separator=ns.separator,
            include_filename_header=ns.include_filename_header,
        )


class FileJoiner:
    """Collects files from a folder and joins their text content."""

    def __init__(self, config: FileJoinerConfig):
        self.config = config
        self.failed_files: list[Path] = []

    # ---------- discovery ----------

    def discover_files(self) -> list[Path]:
        """Find candidate files according to recursive/extension settings."""
        if not self.config.input_dir.exists():
            raise FileNotFoundError(f"Input dir not found: {self.config.input_dir}")

        pattern = "**/*" if self.config.recursive else "*"
        candidates = [p for p in self.config.input_dir.glob(pattern) if p.is_file()]

        if self.config.exclude_dirs:
            before = len(candidates)
            candidates = [
                p for p in candidates
                if not (set(p.relative_to(self.config.input_dir).parts[:-1])
                        & self.config.exclude_dirs)
            ]
            pruned = before - len(candidates)
            if pruned:
                logger.info("Excluded %d file(s) under %s", pruned, sorted(self.config.exclude_dirs))

        if self.config.extensions:
            candidates = [
                p for p in candidates if p.suffix.lower() in self.config.extensions
            ]

        candidates.sort()
        logger.info("Discovered %d file(s) to join", len(candidates))
        return candidates

    # ---------- reading ----------

    def read_file(self, path: Path) -> str:
        """Try the configured encoding first, then fall back through
        `encoding_fallbacks` before giving up. This matters a lot for files
        saved on Windows with non-ASCII text (e.g. Portuguese accents),
        which are frequently cp1252/latin-1, not UTF-8."""
        # Order matters: cp1252/latin-1 are single-byte encodings that map
        # every possible byte, so they NEVER raise UnicodeDecodeError — they
        # must stay last or they'll silently swallow files of other encodings
        # (e.g. utf-16) and "succeed" with garbage instead of falling through.
        candidates = [self.config.encoding, *(self.config.encoding_fallbacks or [])]
        seen: set[str] = set()
        last_exc: Optional[Exception] = None

        for enc in candidates:
            if not enc or enc in seen:
                continue
            seen.add(enc)
            try:
                text = path.read_text(encoding=enc)
                if enc != self.config.encoding:
                    logger.info("Read %s using fallback encoding '%s'", path, enc)
                return text
            except (UnicodeError, OSError) as exc:
                # UnicodeError also covers UnicodeDecodeError and the
                # "stream does not start with BOM" error utf-16 raises
                # on non-utf-16 input.
                last_exc = exc
                continue

        logger.error(
            "Could not decode %s with any of %s: %s", path, list(seen), last_exc
        )
        self.failed_files.append(path)
        return ""

    # ---------- joining ----------

    def build_joined_text(self, files: list[Path]) -> str:
        parts: list[str] = []
        for path in files:
            content = self.read_file(path)
            if not content:
                continue
            if self.config.include_filename_header:
                rel = path.relative_to(self.config.input_dir)
                parts.append(f"--- {rel} ---\n{content}")
            else:
                parts.append(content)
        return self.config.separator.join(parts)

    # ---------- writing ----------

    def write_output(self, text: str) -> None:
        self.config.output_file.parent.mkdir(parents=True, exist_ok=True)
        self.config.output_file.write_text(text, encoding=self.config.encoding)
        logger.info("Wrote joined output to %s", self.config.output_file)

    # ---------- orchestrator ----------

    def run(self) -> Path:
        """Orchestrates discovery -> read/join -> write. Returns output path."""
        files = self.discover_files()
        if not files:
            logger.warning("No files matched the given criteria; nothing to write.")

        joined_text = self.build_joined_text(files)

        if files and not joined_text:
            logger.error(
                "%d file(s) were discovered but none could be decoded (%d failed) — "
                "output will be EMPTY. Add the file(s)' real encoding to "
                "'encoding_fallbacks' in config.json. Failed files: %s",
                len(files),
                len(self.failed_files),
                [str(p) for p in self.failed_files],
            )
        elif self.failed_files:
            logger.warning(
                "%d of %d file(s) could not be decoded and were skipped: %s",
                len(self.failed_files),
                len(files),
                [str(p) for p in self.failed_files],
            )

        self.write_output(joined_text)
        return self.config.output_file


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Join text content from all files in a folder into one file. "
        "Reads input_dir/output_dir/output_filename and other options from "
        "config.json; any CLI flag supplied here overrides the config.json value."
    )
    parser.add_argument(
        "--config",
        default=str(DEFAULT_CONFIG_PATH),
        help=f"Path to the config.json file (default: {DEFAULT_CONFIG_PATH}).",
    )
    parser.add_argument("--input-dir", default=None, help="Overrides config.json input_dir.")
    parser.add_argument("--output-dir", default=None, help="Overrides config.json output_dir.")
    parser.add_argument(
        "--output-filename", default=None, help="Overrides config.json output_filename."
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        default=None,
        help="Overrides config.json recursive (sets it to true).",
    )
    parser.add_argument(
        "--extensions",
        nargs="+",
        default=None,
        help="Overrides config.json extensions, e.g. --extensions .py .md",
    )
    parser.add_argument("--encoding", default=None, help="Overrides config.json encoding.")
    parser.add_argument("--separator", default=None, help="Overrides config.json separator.")
    parser.add_argument(
        "--no-filename-header",
        action="store_true",
        default=None,
        help="Overrides config.json include_filename_header (sets it to false).",
    )
    return parser.parse_args()


def apply_overrides(ns: SimpleNamespace, args: argparse.Namespace) -> SimpleNamespace:
    """Applies any explicitly-supplied CLI flags on top of the loaded config."""
    if args.input_dir is not None:
        ns.input_dir = args.input_dir
    if args.output_dir is not None:
        ns.output_dir = args.output_dir
    if args.output_filename is not None:
        ns.output_filename = args.output_filename
    if args.recursive is not None:
        ns.recursive = args.recursive
    if args.extensions is not None:
        ns.extensions = args.extensions
    if args.encoding is not None:
        ns.encoding = args.encoding
    if args.separator is not None:
        ns.separator = args.separator
    if args.no_filename_header is not None:
        ns.include_filename_header = not args.no_filename_header
    return ns


def main() -> None:
    args = parse_args()
    loader = ConfigLoader(Path(args.config))
    ns = loader.load()
    ns = apply_overrides(ns, args)

    config = FileJoinerConfig.from_namespace(ns)
    joiner = FileJoiner(config)
    joiner.run()


if __name__ == "__main__":
    main()
