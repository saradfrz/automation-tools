# JoinFilesApp Technical Notes

Implementation: [join_files_app.py](../join-files/join_files_app.py)

Class: `JoinFilesApp`

## Responsibilities

`JoinFilesApp` loads the join-files configuration, applies shared overrides, builds a `FileJoinerConfig`, and delegates execution to `FileJoiner.run()`.

The underlying pipeline discovers files, filters extensions and excluded directories, decodes text using the configured encoding and fallbacks, joins content with separators and optional filename headers, and writes the result.

## Shared Parameter Mapping

| Shared parameter | Join-files setting |
|---|---|
| `input_dir` | `input_dir` |
| `output_dir` | `output_dir` |
| `output_filename` | `output_filename` |

Relative override paths are resolved from the current working directory. Relative paths from the default config are resolved from `join-files/`.

## Configuration

Additional behavior remains in `join-files/config.json`:

- `recursive`
- `extensions`
- `encoding` and `encoding_fallbacks`
- `separator`
- `include_filename_header`
- `exclude_dirs`

The root dispatcher intentionally exposes the common path and filename options only. Application-specific options should be changed in the configuration file.

## Direct API

```python
app = JoinFilesApp(
    input_dir="input",
    output_dir="output",
    output_filename="joined.txt",
)
output_path = app.run()
```
