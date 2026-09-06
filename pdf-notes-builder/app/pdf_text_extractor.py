import logging
from datetime import datetime
from pathlib import Path

from pypdf import PdfReader

from app.utils.directory import DirectoryManager
from app.utils.file import FileManager
from app.utils.retry import Retry
from app.utils.string import StringUtils


class PdfTextExtractor:
    """
    Extracts text from every PDF found in the configured input directory
    and joins the result into a single output .txt file.

    All behavior is driven by the loaded config (SimpleNamespace):
      - config.dir.input / config.dir.output
      - config.extraction.* (naming, separators, encoding, timestamp format)
      - config.retry.* (retry attempts/backoff around per-file extraction)
    """

    def __init__(self, config, logger: logging.Logger = None):
        self.config = config
        self.logger = logger or logging.getLogger("invoice_pipeline")
        self.dir_manager = DirectoryManager()
        self.file_manager = FileManager()

        retry_cfg = config.retry
        self._extract_with_retry = Retry(
            max_attempts=retry_cfg.max_attempts,
            delay_seconds=retry_cfg.delay_seconds,
            backoff_multiplier=retry_cfg.backoff_multiplier,
            logger=self.logger,
        )(self._extract_pdf_text)

    def run(self):
        """
        Orchestrates the full pipeline: discover PDFs, extract text from
        each, join them, and persist the combined result to output/.
        Returns the Path to the generated output file, or None if no
        PDF files were found.
        """
        input_dir = Path(self.config.dir.input)
        pdf_files = self.dir_manager.get_pdf_files(
            input_dir, extension=self.config.extraction.file_extension
        )

        if not pdf_files:
            self.logger.info("No PDF files found in '%s'. Nothing to do.", input_dir)
            return None

        self.logger.info("Found %d PDF file(s) to process.", len(pdf_files))

        combined_text = self._build_combined_text(pdf_files)
        output_path = self._write_output(combined_text)

        self.logger.info("Combined text written to '%s'.", output_path)
        return output_path

    def _build_combined_text(self, pdf_files):
        chunks = []
        for pdf_path in pdf_files:
            self.logger.info("Processing '%s'.", pdf_path.name)
            try:
                text = self._extract_with_retry(pdf_path)
            except Exception:
                self.logger.exception("Skipping '%s' after repeated failures.", pdf_path.name)
                continue

            document_header = self.config.extraction.document_separator.format(
                file_name=pdf_path.name
            )
            chunks.append(document_header + text)

        return StringUtils.normalize_line_breaks("".join(chunks))

    def _extract_pdf_text(self, pdf_path: Path) -> str:
        """
        Extract and clean text from a single PDF, page by page.
        """
        reader = PdfReader(pdf_path)
        page_separator = self.config.extraction.page_separator
        pages_text = []

        for page_number, page in enumerate(reader.pages, start=1):
            raw_text = page.extract_text() or ""
            cleaned_text = StringUtils.clean_page_text(raw_text)
            separator = page_separator.format(page_number=page_number)
            pages_text.append(f"{separator}{cleaned_text}")

        return "".join(pages_text)

    def _write_output(self, content: str) -> Path:
        output_dir = Path(self.config.dir.output)
        timestamp = datetime.now().strftime(self.config.extraction.timestamp_format)
        filename = f"{self.config.extraction.output_filename_prefix}_{timestamp}.txt"
        output_path = output_dir / filename

        self.file_manager.write_file(str(output_path), content)
        return output_path
