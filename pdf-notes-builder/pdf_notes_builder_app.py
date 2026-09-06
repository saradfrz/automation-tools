import os
import shutil
from pathlib import Path

from app.utils.config import load_config
from app.utils.logger import setup_logger
from app.pdf_text_extractor import PdfTextExtractor


class PdfNotesBuilderApp:
    """Application wrapper for the PDF text extraction pipeline."""

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

        for directory in (config.dir.output, config.dir.logs):
            if os.path.exists(directory):
                shutil.rmtree(directory)
            os.makedirs(directory, exist_ok=True)

        logger = setup_logger()
        logger.info("Application started.")

        try:
            extractor = PdfTextExtractor(config, logger)
            result_path = extractor.run()
            if result_path:
                logger.info("Application finished successfully. Output: %s", result_path)
            else:
                logger.info("Application finished. No output was generated.")
            return result_path
        except Exception:
            logger.exception("Unhandled exception occurred.")
            raise

    def _apply_overrides(self, config):
        if self.overrides["input_dir"] is not None:
            config.dir.input = Path(self.overrides["input_dir"]).resolve()
        if self.overrides["output_dir"] is not None:
            output_dir = Path(self.overrides["output_dir"]).resolve()
            config.dir.output = output_dir
            config.dir.output_html = output_dir
        if self.overrides["output_filename"] is not None:
            config.extraction.output_filename_prefix = Path(
                self.overrides["output_filename"]
            ).stem

    def _resolve_paths(self, config):
        for field in ("input", "output", "output_html", "logs"):
            if not hasattr(config.dir, field):
                continue
            value = Path(getattr(config.dir, field))
            if not value.is_absolute():
                value = self.base_dir / value
            setattr(config.dir, field, value)


if __name__ == "__main__":
    PdfNotesBuilderApp().run()