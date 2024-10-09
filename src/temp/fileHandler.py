import os
import sys

# Add the project root to the PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.logger import logging
from utils.exception import CustomException


class FileHandler:
    def __init__(self, file_data):
        try:
            self.life_name = file_data["life_name"]
            self.file_list = [file_path for file_path in file_data["file_paths"]]
        except Exception as e:
            raise CustomException(e, sys)

    def get_file_data(self):
        return {"life_name": self.life_name, "file_list": self.file_list}

    logging.info("Files are loaded successfully.")
