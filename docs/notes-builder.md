# NotesBuilderApp Technical Notes

Implementation: [notes_builder_app.py](../notes-builder/notes_builder_app.py)

Class: `NotesBuilderApp`

## Responsibilities

`NotesBuilderApp` is the orchestration layer for screenshot OCR. It loads the nested configuration, applies shared overrides, resolves application-relative directories, recreates the configured output and log directories, loads `.env`, and delegates OCR to `NotesBuilder`.

The underlying `NotesBuilder` loads EasyOCR models, scans supported image extensions, extracts text with retry behavior, and writes timestamped notes files.

## Shared Parameter Mapping

| Shared parameter | Notes-builder setting |
|---|---|
| `input_dir` | `config.dir.input` |
| `output_dir` | `config.dir.output_html` |
| `output_filename` | `config.output.filename_prefix` |

For this timestamped application, `output_filename` is interpreted as the filename stem or prefix. The generated file keeps the configured timestamp suffix.

## Configuration

Application-specific settings are in `notes-builder/config.json`:

- `dir.input`, `dir.output_html`, `dir.logs`, `dir.models`
- OCR languages, GPU mode, detail, and paragraph behavior
- output filename prefix
- retry settings
- supported image extensions

The output and logs directories are wiped and recreated for each run. Input files and OCR models are preserved.

## Direct API

```python
app = NotesBuilderApp(
    input_dir="input",
    output_dir="output",
    output_filename="class_notes",
)
output_path = app.run()
```
