from pathlib import Path


class DirectoryManager:

    @staticmethod
    def get_csv_files(input_folder):
        """
        Get all CSV files in the input folder.
        """
        return list(input_folder.glob("*.csv"))

    @staticmethod
    def get_pdf_files(input_folder, extension=".pdf"):
        """
        Get all PDF files in the input folder, sorted by name for
        deterministic processing order.
        """
        folder = Path(input_folder)
        return sorted(folder.glob(f"*{extension}"))

    def list_files(self, folder_path, extension=None):
        """
        List all files in the given folder.
        """
        folder = Path(folder_path)
        if extension:
            return [file.name for file in folder.iterdir() if file.is_file() and file.suffix == extension]
        return [file.name for file in folder.iterdir() if file.is_file()]
