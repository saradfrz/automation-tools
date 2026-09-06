import os
import shutil

from dotenv import load_dotenv

from app.utils.config import load_config
from app.utils.logger import setup_logger
from app.ocr.notes_builder import NotesBuilder

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
        load_dotenv()

        notes_builder = NotesBuilder(config=config, logger=logger)
        output_path = notes_builder.build_notes()

        logger.info(f"Notes file ready at: {output_path}")
    except Exception:
        logger.exception("Unhandled exception occurred.")
        raise
