"""
generate_tree.py

Generates a pretty-printed directory tree (folders and files), similar to
the Unix `tree` command, using parametrized config (config.json) and
logging instead of print statements.

Usage:
    python generate_tree.py
    python generate_tree.py --config custom_config.json
    python generate_tree.py --root /path/to/dir --max-depth 3
"""

import argparse
import json
import logging
from pathlib import Path
from types import SimpleNamespace


class ConfigLoader:
    """Loads configuration from a JSON file into a dot-notation namespace."""

    def __init__(self, config_path: str) -> None:
        self.config_path = Path(config_path)

    def load(self) -> SimpleNamespace:
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        with open(self.config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return SimpleNamespace(**data)


class TreeGenerator:
    """Builds and renders a pretty-printed directory tree."""

    BRANCH = "├── "
    LAST_BRANCH = "└── "
    VERTICAL = "│   "
    SPACE = "    "

    def __init__(self, config: SimpleNamespace, logger: logging.Logger) -> None:
        self.root_dir = Path(config.root_dir).resolve()
        self.max_depth = config.max_depth
        self.show_hidden = config.show_hidden
        self.ignore_dirs = set(config.ignore_dirs)
        self.ignore_files = set(config.ignore_files)
        self.output_file = config.output_file
        self.logger = logger
        self._lines = []

    def _is_ignored(self, path: Path) -> bool:
        if not self.show_hidden and path.name.startswith("."):
            return True
        if path.is_dir() and path.name in self.ignore_dirs:
            return True
        if path.is_file() and path.name in self.ignore_files:
            return True
        return False

    def _sorted_children(self, directory: Path):
        try:
            children = [p for p in directory.iterdir() if not self._is_ignored(p)]
        except PermissionError:
            self.logger.warning("Permission denied: %s", directory)
            return []
        # Directories first, then files, both alphabetically
        return sorted(children, key=lambda p: (p.is_file(), p.name.lower()))

    def _walk(self, directory: Path, prefix: str = "", depth: int = 0) -> None:
        if self.max_depth is not None and depth >= self.max_depth:
            return

        children = self._sorted_children(directory)
        count = len(children)

        for index, path in enumerate(children):
            is_last = index == count - 1
            connector = self.LAST_BRANCH if is_last else self.BRANCH
            self._lines.append(f"{prefix}{connector}{path.name}")

            if path.is_dir():
                extension = self.SPACE if is_last else self.VERTICAL
                self._walk(path, prefix + extension, depth + 1)

    def generate(self) -> str:
        if not self.root_dir.exists():
            raise FileNotFoundError(f"Root directory not found: {self.root_dir}")

        self.logger.info("Generating tree for: %s", self.root_dir)
        self._lines = [str(self.root_dir.name) + "/"]
        self._walk(self.root_dir)
        tree_str = "\n".join(self._lines)
        self.logger.info("Tree generated with %d entries", len(self._lines) - 1)
        return tree_str

    def save(self, tree_str: str) -> Path:
        # output_file is independent of root_dir: absolute path, or relative
        # to the current working directory (not the scanned root).
        output_path = Path(self.output_file).expanduser().resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(tree_str, encoding="utf-8")
        self.logger.info("Tree saved to: %s", output_path)
        return output_path


def setup_logging(level_name: str) -> logging.Logger:
    level = getattr(logging, level_name.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )
    return logging.getLogger("TreeGenerator")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a pretty-printed directory tree.")
    parser.add_argument("--config", default="config.json", help="Path to config.json")
    parser.add_argument("--root", default=None, help="Override root_dir from config")
    parser.add_argument("--max-depth", type=int, default=None, help="Override max_depth from config")
    parser.add_argument("--output", default=None, help="Override output_file from config")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    config = ConfigLoader(args.config).load()

    # CLI args override config values when provided
    if args.root is not None:
        config.root_dir = args.root
    if args.max_depth is not None:
        config.max_depth = args.max_depth
    if args.output is not None:
        config.output_file = args.output

    logger = setup_logging(getattr(config, "log_level", "INFO"))

    generator = TreeGenerator(config, logger)
    tree_str = generator.generate()

    # print(tree_str)  # Only user-facing output; not a debug/log statement
    generator.save(tree_str)


if __name__ == "__main__":
    main()
