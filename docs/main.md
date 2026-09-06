# Root Dispatcher Technical Notes

The root [main.py](../main.py) is the command-line dispatcher for all automation applications.

## Dispatch Model

`APP_SPECS` maps a public selector to a Python module path and class name:

```python
"join-files": ("join-files/join_files_app.py", "JoinFilesApp")
```

`parse_args()` creates a mutually exclusive required group, so exactly one application flag must be provided. The root parser also accepts `--config`, `--input-dir`, `--output-dir`, and `--output-filename`.

`load_app()` dynamically loads only the selected module with `importlib.util`. The selected application's directory is temporarily added to `sys.path`; this is required because the application packages use local imports such as `from app...`.

`main()` selects the class, constructs it with the shared arguments, and calls `run()`. The return value from `run()` is returned by `main()` but is not printed by the script.

## Class Contract

Each registered application class follows this constructor shape:

```python
AppClass(
    config_path=None,
    input_dir=None,
    output_dir=None,
    output_filename=None,
)
```

Each class exposes:

```python
run() -> Path | None
```

The exact output behavior depends on the application. The shared parameter names are normalized by each class to its own configuration model.

## Adding an Application

1. Create a class-based runner with the shared constructor and `run()` method.
2. Place it in an application directory.
3. Add a selector, module path, and class name to `APP_SPECS`.
4. Add the selector and class documentation to the root README and `docs/`.
5. Compile and smoke-test the root command:

```powershell
python -m py_compile main.py path\to\app_runner.py
python main.py --help
```
