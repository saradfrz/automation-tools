# generate-dir-tree

Generates a pretty-printed directory tree of folders and files, similar to the Unix `tree` command. The tool uses `config.json` for default settings and writes the generated tree to a text file.

## Requirements

- Python 3.9+
- No external dependencies; Python standard library only

## Files

```
generate-dir-tree/
├── config.json       # Default runtime configuration
├── generate_tree.py  # Command-line entry point and tree generator
├── output/           # Optional location for generated files
└── README.md
```

## Configuration

The default `config.json` looks like this:

```json
{
  "root_dir": "C:\\projects\\supply-chain-capstone",
  "max_depth": null,
  "show_hidden": false,
  "ignore_dirs": [".git", "__pycache__", ".venv", "venv", "node_modules", ".idea", ".mypy_cache"],
  "ignore_files": [".DS_Store"],
  "output_file": "rag_file_tree.txt",
  "log_level": "INFO"
}
```

| Key | Description |
|---|---|
| `root_dir` | Directory to scan. It may be absolute or relative to the current working directory. |
| `max_depth` | Maximum traversal depth. Use `null` for no depth limit. |
| `show_hidden` | Whether entries whose names start with `.` are included. |
| `ignore_dirs` | Directory names to exclude wherever they occur. |
| `ignore_files` | File names to exclude wherever they occur. |
| `output_file` | Path for the generated tree. Relative paths are resolved from the current working directory, not from `root_dir`. Parent directories are created automatically. |
| `log_level` | Logging level, such as `INFO`, `WARNING`, or `DEBUG`. |

Directories are listed before files, and both are sorted alphabetically without regard to case.

## Usage

Run with the default configuration:

```bash
python generate_tree.py
```

Use another configuration file:

```bash
python generate_tree.py --config path/to/custom_config.json
```

Override selected configuration values for one run:

```bash
python generate_tree.py --root ./src --max-depth 3 --output ./output/src-tree.txt
```

| Option | Description |
|---|---|
| `--config` | Path to the JSON configuration file. Defaults to `config.json`. |
| `--root` | Overrides `root_dir`. |
| `--max-depth` | Overrides `max_depth` with an integer. |
| `--output` | Overrides `output_file`. |

CLI overrides do not modify the configuration file.

## Example output

```text
my-project/
├── app/
│   ├── main.py
│   └── utils.py
├── README.md
└── config.json
```

## Behavior and errors

- The root directory must exist; otherwise the script raises `FileNotFoundError`.
- A missing configuration file raises `FileNotFoundError`.
- Hidden entries are excluded by default.
- Permission-denied directories are skipped with a warning.
- The generated tree is saved as UTF-8 text.
- The script logs progress and the number of generated entries according to `log_level`.
