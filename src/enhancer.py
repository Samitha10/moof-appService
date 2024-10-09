import json
import os
import sys
from langchain_groq import ChatGroq
from pathlib import Path

# Add the project root to the PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.exception import CustomException
from utils.logger import logging

logging.info("Starting the process")


class IncidentProcessor:
    def __init__(self, id: int, file_path: str, searcher, Data_Enhancer):
        # Extract the file name without extension
        self.searcher = searcher
        self.Data_Enhancer = Data_Enhancer
        # file_name = os.path.splitext(os.path.basename(file_path))[0]

        # Construct the JSON file path
        json_file_path = os.path.join(
            "JSON_Data", f"{file_path}", "extracted", f"incidents_{id}.json"
        )

        self.filename = json_file_path
        self.file_name = file_path  # Store the file name for later use
        self.id = id  # Store the id for later use

        # with open(self.filename, "rb") as file:
        #     raw_data = file.read()
        #     result = chardet.detect(raw_data)
        #     encoding = result["encoding"

        # with open(self.file_path, "r", encoding=encoding) as file:
        #     self.data = json.load(file)

        with open(self.filename, "r", encoding="utf-8") as file:
            self.data = json.load(file)
            logging.info(f"Data loaded from {self.filename} and ready for processing")

    def format_string(self, input_list, existing_string):
        formatted_strings = ["#mooflife", "#mof", "#MomentOfLife"]
        for item in input_list:
            words = item.split()
            formatted_item = "#" + "".join(word.capitalize() for word in words)
            formatted_strings.append(
                formatted_item
            )  # Append the formatted string individually
        formatted_string = " ".join(formatted_strings)
        return existing_string + " " + formatted_string

    def word_count(self, text):
        return len(text.split())

    def title_enhancer(self, doc):
        return self.Data_Enhancer.Title_enhancer(doc)

    def description_enhancer(self, doc, exist_doc):
        return self.Data_Enhancer.Description_enhancer(doc, exist_doc)

    def validate_incidents(self):
        required_keys = ["Year", "Title", "Description"]
        valid_incidents = []

        for incident in self.data["incidents"]:
            if all(key in incident for key in required_keys) and all(
                incident[key] is not None for key in required_keys
            ):
                valid_incidents.append(incident)
            else:
                logging.warning(
                    f"Incident skipped: Missing required keys or null values. Incident: {incident}"
                )

        if not valid_incidents:
            logging.warning(
                "All incidents were invalid. Data does not contain required keys: 'Year', 'Title', 'Description' or some of their values are null"
            )
            self.data["incidents"] = None
        else:
            self.data["incidents"] = valid_incidents

        return self.data["incidents"]

    def process(self):
        validate_data = self.validate_incidents()

        if validate_data is None:
            logging.error("Data is empty, Nothing for processing")
            return self.data["incidents"]

        else:
            logging.info("Data is not empty, proceeding with processing")
            for moment in self.data["incidents"]:
                year = moment["Year"]
                title = moment["Title"]
                description = moment["Description"]

                To_search_doc = f"{year}. {title}. {description}"

                title_word_count = self.word_count(str(title))
                if title_word_count < 10 or title_word_count > 20:
                    doc1 = self.searcher.search_title(To_search_doc)
                    answer = self.title_enhancer(doc1)
                    if answer is not None:
                        try:
                            moment["Title"] = str(answer["blog_title"])
                            moment["category"] = answer["category"]
                        except Exception as e:
                            CustomException(e, sys)
                            moment["Title"] = None
                            moment["category"] = None
                    else:
                        moment["Title"] = None
                        moment["category"] = None

                description_word_count = self.word_count(str(description))
                if description_word_count < 150 or description_word_count > 450:
                    doc2 = self.searcher.search_description(To_search_doc)
                    answer = self.description_enhancer(doc2, To_search_doc)
                    if answer is not None:
                        try:
                            Tags = answer["Tags"]
                            Description = str(answer["Details"].replace("\n", " "))
                            moment["Description"] = self.format_string(
                                Tags, Description
                            )
                        except Exception as e:
                            logging.warning(CustomException(e, sys))
                            moment["Description"] = None
                    else:
                        moment["Description"] = None

    def save(self, file_path):
        # Construct the enhanced folder path
        enhanced_folder = os.path.join("JSON_Data", f"{file_path}", "enhanced")
        if not os.path.exists(enhanced_folder):
            os.makedirs(enhanced_folder, exist_ok=True)

        # Construct the enhanced file name
        enhanced_name = os.path.join(
            enhanced_folder, f"incidents_{self.id}_enhanced.json"
        )

        # Save the processed data to the enhanced file path
        if self.data["incidents"] is not None:
            with open(enhanced_name, "w", encoding="utf-8") as new_file:
                json.dump(self.data, new_file, indent=4)
            print(f"File has been processed and saved as {enhanced_name}")
        else:
            self.data = {"incidents": []}
            with open(enhanced_name, "w", encoding="utf-8") as new_file:
                json.dump(self.data, new_file, indent=4)
            print(f"File has been processed and saved as {enhanced_name}")


# processer = IncidentProcessor(0, "00000000000", "searcher", "Data_Enhancer")
# result = {
#     "incidents": [
#         {
#             "Year": "1979",
#             "Month": "May",
#             "Day": "4",
#             "Title": "Became Prime Minister of the United Kingdom",
#             "Description": "Thatcher introduced a series of economic policies intended to reverse high inflation and Britain's struggles in the wake of the Winter of Discontent and an oncoming recession.",
#             "Era": "CE",
#         },
#         {
#             "Year": "1975",
#             "Month": "February",
#             "Day": "11",
#             "Title": "Became Leader of the Opposition",
#             "Description": "Thatcher defeated Edward Heath in the Conservative Party leadership election to become leader of the opposition, the first woman to lead a major political party in the UK.",
#             "Era": "CE",
#         },
#     ]
# }
# processer.save(id=0, file_path="00000000000", data=result)
