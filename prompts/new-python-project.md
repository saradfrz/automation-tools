# Goal
You will build a python code that...
# Project Name
project_name = ''
# Project language
Python
# Specifications
```
{project_name}/
├── app
│   ├── {app_modules}
│   └── utils
│       ├── config.py
│       ├── directory.py
│       ├── file.py
│       ├── logger.py
│       ├── retry.py
│       └── string.py
├── input
│   └── # 
├── logs
│   ├── error.log
│   └── info.log
├── models
│   └── 
├── output # 
├── .env # for secrets
├── .gitignore
├── __init__.py
├── config.json # for commitable parametrized variables
├── main.py # entry point of the aplication
├── README.md # documentation
└── requirements.txt
```

## main.py structure

Don't modify this code, only add the missing logic
```python
import os
import shutil

from app.utils.config import load_config
from app.utils.logger import setup_logger
# from app.{created_module} import {module_class}

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
        # add logic here
    except Exception:
        logger.exception("Unhandled exception occurred.")
        raise
```

## config.py
Don't modify this code 
```python
import json
from pathlib import Path
from types import SimpleNamespace


def load_config(config_path):
    config_path = Path(config_path)

    with config_path.open("r", encoding="utf-8") as f:
        return json.load(f, object_hook=lambda d: SimpleNamespace(**d))
```

## directory.py
Don't modify this code. Only add missing logic
```python
from pathlib import Path

class DirectoryManager:
    
    @staticmethod
    def get_csv_files(input_folder):
        """
        Get all CSV files in the input folder.
        """
        return list(input_folder.glob("*.csv"))
    
    def list_files(self, folder_path, extension=None):
        """
        List all files in the given folder.
        """
        folder = Path(folder_path)
        if extension:
            return [file.name for file in folder.iterdir() if file.is_file() and file.suffix == extension]
        return [file.name for file in folder.iterdir() if file.is_file()]

``` 
## file.py 
Don't modify this code. Only add missing logic
```python
from pathlib import Path
import csv

class FileManager:

    @staticmethod
    def read_file(file_path):
        """
        Read the content of a file.
        """
        with open(file_path, 'r') as file:
            return file.read()
        
    def write_file(file_path, content):
        """
        Write content to a file.
        """
        with open(file_path, 'w') as file:
            file.write(content)
    
    def append_to_file(file_path, content):
        """
        Append content to a file.
        """
        with open(file_path, 'a') as file:
            file.write(content)
    
    def delete_file(file_path):
        """
        Delete a file.
        """
        Path(file_path).unlink(missing_ok=True)

    def file_exists(file_path):
        """
        Check if a file exists.
        """
        return Path(file_path).exists()
    
    @staticmethod
    def read_csv(file_path: str | Path, has_header=True):
        with open(file_path, "r", newline="", encoding="utf-8") as file:
            reader = csv.reader(file)

            if has_header:
                header = next(reader, None)
                rows = list(reader)
                return header, rows

            return None, list(reader)

        
    def save_csv(self, file_path: str, headers: list, data: list[list[str]]):
        """
        Save data to a CSV file.
        """
        with open(file_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter=';', quoting=csv.QUOTE_ALL)
            writer.writerow(headers)
            writer.writerows(data)

``` 
## logger.py 
Don't modify this code. 
```python
import logging
from pathlib import Path


def setup_logger() -> logging.Logger:
    """
    Configure the application's logger.

    Creates the logs directory if it does not exist and writes all
    INFO and ERROR messages to logs/application.log.
    """

    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    info_log_file = logs_dir / "info.log"
    error_log_file = logs_dir / "error.log"

    logger = logging.getLogger("invoice_pipeline")

    # Prevent duplicate handlers if called more than once
    if logger.hasHandlers():
        return logger

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    info_file_handler = logging.FileHandler(info_log_file, encoding="utf-8")
    info_file_handler.setLevel(logging.INFO)
    info_file_handler.setFormatter(formatter)

    error_file_handler = logging.FileHandler(error_log_file, encoding="utf-8")
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(formatter)

    logger.addHandler(info_file_handler)
    logger.addHandler(error_file_handler)

    return logger

``` 
## string.py 
Don't modify this code. Only add missing logic
```python
import re

class StringUtils:
    
    @staticmethod
    def replace_multiple_spaces(text):
        return re.sub(r'\s+', ' ', text).strip()
```



