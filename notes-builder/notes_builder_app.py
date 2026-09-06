import os
import shutil
from pathlib import Path

from dotenv import load_dotenv

from app.utils.config import load_config
from app.utils.logger import setup_logger
from app.ocr.notes_builder import NotesBuilder


class NotesBuilderApp:
    """Application wrapper for the screenshot OCR pipeline."""

    def __init__(self, config_path=None, input_dir=None, output_dir=None, output_filename=None):
        self.base_dir = Path(__file__).resolve().parent
        self.config_path = Path(config_path or self.base_dir / "config.json")
        self.overrides = {
            "input_dir": input_dir,
            "output_dir": output_dir,
            "output_filename": output_filename,
        }

    def run(self):
        config = load_config(self.config_path)
        self._apply_overrides(config)
        self._resolve_paths(config)

        for directory in (config.dir.output_html, config.dir.logs):
            if os.path.exists(directory):
                shutil.rmtree(directory)
            os.makedirs(directory, exist_ok=True)

        logger = setup_logger()
        logger.info("Application started.")

        try:
            load_dotenv(self.base_dir / ".env")
            notes_builder = NotesBuilder(config=config, logger=logger)
            output_path = notes_builder.build_notes()
            logger.info("Notes file ready at: %s", output_path)
            return output_path
        except Exception:
            logger.exception("Unhandled exception occurred.")
            raise

    def _apply_overrides(self, config):
        if self.overrides["input_dir"] is not None:
            config.dir.input = Path(self.overrides["input_dir"]).resolve()
        if self.overrides["output_dir"] is not None:
            config.dir.output_html = Path(self.overrides["output_dir"]).resolve()
        if self.overrides["output_filename"] is not None:
            config.output.filename_prefix = Path(self.overrides["output_filename"]).stem

    def _resolve_paths(self, config):
        for field in ("input", "output_html", "logs", "models"):
            value = Path(getattr(config.dir, field))
            if not value.is_absolute():
                value = self.base_dir / value
            setattr(config.dir, field, value)


if __name__ == "__main__":
    NotesBuilderApp().run()