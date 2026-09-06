# Automation Tools

This repository contains several small automation applications with one root command-line entry point: `main.py`.

## Requirements

- Python 3.9 or newer
- Install shared dependencies from `requirements.txt`:

```powershell
pip install -r requirements.txt
```

Some applications have additional runtime dependencies. For example, `notes-builder` requires EasyOCR and `pdf-notes-builder` requires `pypdf`.

## Root Usage

Run commands from the repository root:

```powershell
python main.py --help
```

Exactly one application selector is required per run:

| Selector | Application | Default configuration |
|---|---|---|
| `--generate-tree` | Generate a text directory tree | `generate-dir-tree/config.json` |
| `--join-files` | Join text files into one output file | `join-files/config.json` |
| `--notes-builder` | OCR image slides into class notes | `notes-builder/config.json` |
| `--pdf-notes-builder` | Extract and combine PDF text | `pdf-notes-builder/config.json` |

Examples:

```powershell
python main.py --generate-tree
python main.py --join-files
python main.py --notes-builder
python main.py --pdf-notes-builder
```

## Shared Overrides

The root launcher supports these overrides for every application:

```powershell
python main.py --join-files `
  --input-dir "C:\projects\supply-chain-capstone" `
  --output-dir output `
  --output-filename rag_project.txt
```

Both hyphenated and underscored spellings are accepted:

- `--input-dir` or `--input_dir`
- `--output-dir` or `--output_dir`
- `--output-filename` or `--output_filename`

Use a different configuration file with `--config`:

```powershell
python main.py --generate-tree --config path\to\custom-config.json
```

Relative paths supplied as command-line overrides are resolved from the current working directory. Relative paths in an application's default configuration are resolved from that application's directory.

## Application Details

- [GenerateTreeApp technical documentation](docs/generate-tree.md)
- [JoinFilesApp technical documentation](docs/join-files.md)
- [NotesBuilderApp technical documentation](docs/notes-builder.md)
- [PdfNotesBuilderApp technical documentation](docs/pdf-notes-builder.md)
- [Root dispatcher technical documentation](docs/main.md)

Each application directory also contains a README describing its domain-specific configuration and processing behavior.

## Repository Layout

```text
main.py                         Root dispatcher
README.md                       This guide
docs/                           Technical application documentation
generate-dir-tree/               Directory tree generator
join-files/                     File joining application
notes-builder/                  OCR notes application
pdf-notes-builder/              PDF notes application
presentation-builder/           Presentation-related assets
prompts/                        Reusable prompts
```
