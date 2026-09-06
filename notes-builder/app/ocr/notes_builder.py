import logging
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

import easyocr

from app.utils.directory import DirectoryManager
from app.utils.file import FileManager
from app.utils.retry import retry
from app.utils.string import StringUtils


class NotesBuilder:
    """
    Runs OCR over a folder of screen-printed presentation slides (images)
    and compiles the extracted text into a single timestamped notes file.

    All tunables (languages, retry behavior, file locations, output
    naming) are pulled from config.json - nothing here is hardcoded.
    """

    def __init__(self, config: SimpleNamespace, logger: logging.Logger):
        self.config = config
        self.logger = logger

        self.directory_manager = DirectoryManager()

        self.input_dir = Path(config.dir.input)
        self.output_dir = Path(config.dir.output_html)
        self.models_dir = Path(config.dir.models)
        self.models_dir.mkdir(parents=True, exist_ok=True)

        self.supported_extensions = tuple(config.supported_extensions)
        self.filename_prefix = config.output.filename_prefix

        self.reader = self._build_reader()

        # Wrap the OCR call with retry behavior parametrized from config.
        self._extract_text_with_retry = retry(
            max_attempts=self.config.retry.max_attempts,
            delay_seconds=self.config.retry.delay_seconds,
        )(self._extract_text_from_image)

    def _build_reader(self) -> easyocr.Reader:
        """
        Load the OCR model(s). Weights are cached under config.dir.models
        so subsequent runs don't re-download them.
        """
        languages = list(self.config.ocr.languages)
        self.logger.info("Loading OCR model(s) for languages: %s", languages)
        return easyocr.Reader(
            languages,
            gpu=self.config.ocr.gpu,
            model_storage_directory=str(self.models_dir),
            download_enabled=True,
            verbose=False,
        )

    def _get_image_files(self) -> list[str]:
        """
        List every supported image in the input folder, deduplicated
        and sorted for deterministic output ordering.
        """
        found = set()
        for extension in self.supported_extensions:
            found.update(self.directory_manager.list_files(self.input_dir, extension=extension))
        return sorted(found)

    def _extract_text_from_image(self, image_path: Path) -> str:
        """
        Run OCR on a single image and return cleaned text.
        """
        self.logger.info("Extracting text from %s", image_path.name)
        raw_result = self.reader.readtext(
            str(image_path),
            detail=self.config.ocr.detail,
            paragraph=self.config.ocr.paragraph,
        )

        if self.config.ocr.detail == 0:
            lines = raw_result
        else:
            lines = [entry[1] for entry in raw_result]

        text = "\n".join(lines)
        return StringUtils.replace_multiple_spaces(text)

    def build_notes(self) -> Path:
        """
        Process every image in the input folder and append the extracted
        text into a single timestamped output file.
        """
        image_names = self._get_image_files()
        if not image_names:
            self.logger.warning("No supported images found in %s", self.input_dir)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = self.output_dir / f"{self.filename_prefix}_{timestamp}.txt"

        processed_count = 0
        for name in image_names:
            image_path = self.input_dir / name
            try:
                text = self._extract_text_with_retry(image_path)
            except Exception:
                self.logger.exception("Giving up on %s after retries", name)
                continue

            # section = f"\n{'=' * 80}\n{name}\n{'=' * 80}\n{text}\n"

            section = f"\n{text}\n{'=' * 84}\n"
            # append_to_file is not decorated as @staticmethod in FileManager,
            # so it must be called on the class, not an instance, to avoid
            # 'self' being bound to the file_path argument.
            FileManager.append_to_file(output_path, section)
            processed_count += 1
            self.logger.info("Appended notes from %s (%d/%d)", name, processed_count, len(image_names))

        self.logger.info("Notes file generated at %s (%d image(s) processed)", output_path, processed_count)
        return output_path
