import json
import re
import os
import glob
import sys
from Levenshtein import distance as levenshtein_distance
import asyncio

# Add the project root to the PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.exception import CustomException
from utils.logger import logging, stop_listener, logger


filename = "Margret.pdf"


class LocalSearcher:
    def __init__(self, file_path):
        self.file_path = file_path
        # Extract the base name without extension
        base_name = os.path.splitext(os.path.basename(file_path))[0]

        # Construct the path to the JSON_Processed folder
        json_file_path = os.path.join(
            "JSON_Data", "JSON_Processed", f"{base_name}_JSON_Processed.json"
        )
        self.processed_data = []
        # Read the JSON data from the file
        with open(json_file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            self.processed_data = data.get("incidents", [])

    def getData(self):
        # Extract titles and descriptions
        titles = [incident.get("Title", "") for incident in self.processed_data]
        descriptions = [
            incident.get("Description", "") for incident in self.processed_data
        ]
        # Combine year, month, day, and title into one string
        LIST01 = [
            f"{incident.get('Year', '')} {incident.get('Month', '')} {incident.get('Day', '')} {incident.get('Title', '')}"
            for incident in self.processed_data
        ]
        # print("Titles:", titles[0])
        # print("Descriptions:", descriptions[0])
        return LIST01, descriptions


local_searcher = LocalSearcher(filename)
titles, descriptions = local_searcher.getData()

def localSearcher(st_list):
    # Initialize the Levenshtein comparator.
    def lev(s1, s2):
        return levenshtein_distance(s1, s2)

    # List of strings
    strings = st_list

    # Function to compare each string with every other string
    def compare_strings(strings):
        n = len(strings)
        results = []
        for i in range(n):
            for j in range(n):
                if i != j:
                    score = lev(strings[i], strings[j])
                    results.append((strings[i], strings[j], score))
        return results

    # Perform the comparison
    comparison_results = compare_strings(strings)

    # Print the results
    for result in comparison_results:
        # logging.info(
        #     f"Comparing '{result[0]}' with \n '{result[1]}': \n Score = {result[2]}"
        # )
        # print("-----------------------------------")
        # Save the results to a JSON file
        output_file = "comparison_results.json"
        with open(output_file, "w", encoding="utf-8") as file:
            json.dump(
                [
                    {"string1": result[0], "string2": result[1], "score": result[2]}
                    for result in comparison_results
                ],
                file,
                ensure_ascii=False,
                indent=4,
            )
        logging.info(f"Comparison results saved to {output_file}")


# localSearcher(titles)

