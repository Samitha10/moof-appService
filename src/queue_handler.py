import os
import sys
from typing import List, Dict

# Add the project root to the PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# from utils.exception import CustomException
# from utils.logger import logging


class QueueHandler:
    def __init__(self) -> None:
        pass

    def process_list(self, input_list: List[Dict]):
        required_keys = [
            "operation_id",
            "file_path",
            "file_name",
            "life_id",
            "search_state",
            "prompt",
        ]
        wiki_list = []
        pdf_list = []
        failed_ids = []

        for item in input_list:
            # # Convert all values to string format
            # item = {key: str(value) for key, value in item.items()}

            # Check if all required keys are present, not null
            if all(key in item and item[key] for key in required_keys[:5]):
                # Check if file_path is a Wikipedia link or a PDF link
                if "wikipedia.org" in item["file_path"]:
                    wiki_list.append(item)
                else:
                    pdf_list.append(item)
            else:
                # If any of the required keys are missing or null, add operation_id to failed_ids
                failed_ids.append(item["operation_id"])

        return wiki_list, pdf_list, failed_ids


""" sample_list = [
    {
        "operation_id": "E1",
        "file_path": "https://en.wikipedia.org/wiki/Python_(programming_language)",
        "filename": "Python_(programming_language)",
        "life_id": "",
        "search_state": "True",
        "prompt": None,
    },
    {
        "operation_id": "E2",
        "file_path": "example.com",
        "filename": "Python_(programming_language)",
        "life_id": "123456",
        "search_state": None,
        "prompt": None,
    },
    {
        "operation_id": "E3",
        "file_path": "https://en.wikipedia.org/wiki/Python_(programming_language)",
        "filename": "Python_(programming_language)",
        "life_id": "123456",
        "search_state": "True",
        "prompt": None,
    },
    {
        "operation_id": "E4",
        "file_path": "example.com",
        "filename": "Python_(programming_language)",
        "life_id": "123456",
        "search_state": "True",
        "prompt": None,
    },
    {
        "operation_id": "E5",
        "file_path": "https://en.wikipedia.org/wiki/Python_(programming_language)",
        "filename": "Python_(programming_language)",
        "life_id": "123456",
        "search_state": "True",
        "prompt": None,
    },
]
 """
""" sample_list = [
    {
        "operation_id": "abcde",
        "file_path": "example.com",
        "file_name": "abc",
        "life_id": "123456",
        "search_state": True,
        "prompt": None,
    }
]
print(type(sample_list))
queueHandler = QueueHandler()
wiki_list, pdf_list, failed_ids = queueHandler.process_list(sample_list)
print(wiki_list)
print("--------------------------------------")
print(pdf_list)
print("--------------------------------------")
print(failed_ids)
print("--------------------------------------")
 """
