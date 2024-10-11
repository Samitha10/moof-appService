# Add
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.process_logger import process_logger


class TestClass:
    def some_method(self):
        process_logger.log("Trying 01", level="warning")
        return True
