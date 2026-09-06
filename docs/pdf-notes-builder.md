# PdfNotesBuilderApp Technical Notes

Implementation: [pdf_notes_builder_app.py](../pdf-notes-builder/pdf_notes_builder_app.py)

Class: `PdfNotesBuilderApp`

## Responsibilities

`PdfNotesBuilderApp` loads the nested PDF configuration, applies shared overrides, resolves application-relative directories, recreates output and log directories, and delegates extraction to `PdfTextExtractor`.

The underlying extractor discovers PDFs, extracts page text with `pypdf`, applies retry behavior, joins documents with configured separators, and writes a timestamped UTF-8 text file.

## Shared Parameter Mapping

| Shared parameter | PDF setting |
|---|---|
| `input_dir` | `config.dir.input` |
| `output_dir` | `config.dir.output` and `config.dir.output_html` |
| `output_filename` | `config.extraction.output_filename_prefix` |

For this timestamped application, `output_filename` is interpreted as the filename stem or prefix. The generated file keeps the configured timestamp suffix.

## Configuration

Application-specific settings are in `pdf-notes-builder/config.json`:

- input, output, and log directories
- output filename prefix and timestamp format
- PDF extension and page/document separators
- text encoding
- retry attempts, delay, and backoff multiplier

The output and logs directories are wiped and recreated for each run.

## Direct API

```python
app = PdfNotesBuilderApp(
    input_dir="input",
    output_dir="output",
    output_filename="class_notes",
)
output_path = app.run()
```
