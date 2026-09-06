import argparse
import importlib.util
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent

APP_SPECS = {
    "generate-tree": ("generate-dir-tree/generate_tree_app.py", "GenerateTreeApp"),
    "join-files": ("join-files/join_files_app.py", "JoinFilesApp"),
    "notes-builder": ("notes-builder/notes_builder_app.py", "NotesBuilderApp"),
    "pdf-notes-builder": (
        "pdf-notes-builder/pdf_notes_builder_app.py",
        "PdfNotesBuilderApp",
    ),
}


def parse_args():
    parser = argparse.ArgumentParser(description="Run one of the automation tools.")
    app_group = parser.add_mutually_exclusive_group(required=True)
    for app_name in APP_SPECS:
        app_group.add_argument(
            f"--{app_name}",
            action="store_true",
            help=f"Run the {app_name} application.",
        )

    parser.add_argument("--config", help="Override the selected app's config file.")
    parser.add_argument(
        "--input-dir",
        "--input_dir",
        dest="input_dir",
        help="Override input_dir for this run.",
    )
    parser.add_argument(
        "--output-dir",
        "--output_dir",
        dest="output_dir",
        help="Override output_dir for this run.",
    )
    parser.add_argument(
        "--output-filename",
        "--output_filename",
        dest="output_filename",
        help="Override output_filename for this run.",
    )
    return parser.parse_args()


def load_app(app_name):
    relative_path, class_name = APP_SPECS[app_name]
    module_path = ROOT_DIR / relative_path
    module_name = f"automation_tools_{app_name.replace('-', '_')}"

    app_dir = str(module_path.parent)
    sys.path.insert(0, app_dir)
    try:
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Unable to load application module: {module_path}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
    finally:
        sys.path.remove(app_dir)

    return getattr(module, class_name)


def main():
    args = parse_args()
    app_name = next(name for name in APP_SPECS if getattr(args, name.replace("-", "_")))
    app_class = load_app(app_name)
    app = app_class(
        config_path=args.config,
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        output_filename=args.output_filename,
    )
    return app.run()


if __name__ == "__main__":
    main()