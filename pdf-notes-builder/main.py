import os
import shutil

from app.utils.config import load_config
from app.utils.logger import setup_logger
from app.pdf_text_extractor import PdfTextExtractor

if __name__ == "__main__":
    # Setup the environment and directories
    config = load_config("config.json")
    dirs = [config.dir.output_html, config.dir.logs]
    for directory in dirs:
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
    except Exception:
        logger.exception("Unhandled exception occurred.")
        raise
