# join_files.py — Instructions

Joins the text content of all files inside an input folder into a single output file. Built around a `FileJoiner` class with a `run()` orchestrator method. Configuration is driven by `config.json`, loaded into a `SimpleNamespace` for dot-notation access; CLI flags are optional and only override individual values when supplied.

## Requirements

- Python 3.9+ (no external dependencies — standard library only)

## Location

Place `join_files.py` and `config.json` at the **root of your repository**. All commands below assume you run them from there.

## config.json

```json
{
  "input_dir": "input",
  "output_dir": "output",
  "output_filename": "joined.txt",
  "recursive": false,
  "extensions": null,
  "encoding": "utf-8",
  "separator": "\n\n",
  "include_filename_header": true
}
```

| Key | Required | Description |
|---|---|---|
| `input_dir` | yes | Folder to read files from. |
| `output_dir` | yes | Folder the output file will be written into (created if missing). |
| `output_filename` | yes | Name of the joined output file, e.g. `joined.txt`. |
| `recursive` | no (default `false`) | Also read files inside subfolders, at any depth. |
| `extensions` | no (default `null`) | List of extensions to include, e.g. `[".py", ".md"]`. `null` joins every file type. |
| `encoding` | no (default `"utf-8"`) | Encoding used to read input files and write the output file. |
| `separator` | no (default `"\n\n"`) | String inserted between each file's content in the output. |
| `include_filename_header` | no (default `true`) | Whether to prefix each file's content with a `--- relative/path ---` header. |

`input_dir` and `output_dir` are joined as `output_dir / output_filename` to build the final output path.

## Basic usage

```bash
python join_files.py
```

Reads all settings from `./config.json`.

Use a different config file:

```bash
python join_files.py --config path/to/other_config.json
```

## Overriding config.json from the CLI

Any of the following flags, if passed, overrides the matching `config.json` value for that run only (the file itself is not modified):

| Flag | Overrides |
|---|---|
| `--input-dir` | `input_dir` |
| `--output-dir` | `output_dir` |
| `--output-filename` | `output_filename` |
| `--recursive` | `recursive` (sets to `true`) |
| `--extensions .py .md` | `extensions` |
| `--encoding` | `encoding` |
| `--separator` | `separator` |
| `--no-filename-header` | `include_filename_header` (sets to `false`) |

Example — same config, but recursive and restricted to `.py`/`.md`:

```bash
python join_files.py --recursive --extensions .py .md
```

## Behavior notes

- Files that fail to decode with the given `encoding` (e.g. binary files) are skipped with a warning logged to the console — they don't stop the run.
- File order is alphabetical (`sorted()` over discovered paths) for deterministic output.
- If `extensions` is `null`/omitted, every file is included regardless of type.
- If `input_dir` does not exist, the script raises `FileNotFoundError` and exits.
- If `config.json` is missing, or missing one of `input_dir` / `output_dir` / `output_filename`, the script raises an error and exits before doing any work.
- If no files match the given criteria, an empty output file is still created, with a warning logged.

## Code structure

- **`ConfigLoader`** — reads `config.json`, validates required keys, fills in defaults for optional ones, and returns a `SimpleNamespace`.
- **`FileJoinerConfig`** — dataclass holding all run parameters. Built via `FileJoinerConfig.from_namespace(ns)` from the loaded (and possibly CLI-overridden) config. Normalizes extensions (adds leading dot, lowercases) in `__post_init__`.
- **`FileJoiner`** — does the work:
  - `discover_files()` — globs `input_dir` (recursive or not) and filters by extension.
  - `read_file()` — reads a single file's text, skipping unreadable ones.
  - `build_joined_text()` — concatenates all file contents with the configured separator and optional headers.
  - `write_output()` — writes the final text to `output_file`, creating parent directories.
  - `run()` — **orchestrator method**: calls the above steps in order and returns the output path.
- CLI parsing (`argparse`) lives in `parse_args()`; `apply_overrides()` layers CLI flags onto the loaded config; both are wired up in `main()`.
