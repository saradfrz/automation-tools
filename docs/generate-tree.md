# GenerateTreeApp Technical Notes

Implementation: [generate_tree_app.py](../generate-dir-tree/generate_tree_app.py)

Class: `GenerateTreeApp`

## Responsibilities

`GenerateTreeApp` adapts the directory-tree generator to the root dispatcher. It loads `generate-dir-tree/config.json`, applies shared command-line overrides, creates a `TreeGenerator`, generates the tree, and saves it.

The underlying `TreeGenerator` performs the traversal:

- directories are listed before files;
- entries are sorted case-insensitively;
- hidden entries and configured names are filtered;
- `max_depth` limits recursion;
- the result is written as UTF-8 text.

## Shared Parameter Mapping

| Shared parameter | Generate-tree setting |
|---|---|
| `input_dir` | `root_dir` |
| `output_dir` | Parent directory of `output_file` |
| `output_filename` | Filename of `output_file` |

If `output_file` is empty, the wrapper uses `directory_tree.txt` as the default filename.

## Configuration

The application configuration supports `root_dir`, `max_depth`, `show_hidden`, `ignore_dirs`, `ignore_files`, `output_file`, and `log_level`. The root dispatcher exposes only the shared path and filename overrides; configure `max_depth` and filtering options in JSON.

## Direct API

```python
app = GenerateTreeApp(
    config_path="generate-dir-tree/config.json",
    input_dir=".",
    output_dir="output",
    output_filename="tree.txt",
)
output_path = app.run()
```
