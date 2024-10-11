import json
import os
import sys
import wikipedia
from pathlib import Path
import warnings

# Add the project root to the PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.exception import CustomException
from utils.logger import logging

warnings.filterwarnings("ignore", category=UserWarning, module="bs4")


class WikiSearch:
    def __init__(self) -> None:
        pass

    def getData(self, link: str, file_path: str):
        result = []
        page_title = link.split("/")[-1]
        try:
            wiki = wikipedia.page(page_title)
            data = wiki.content
            image_links = wiki.images
            result.append(
                {
                    "wiki_link": link,
                    "page_title": page_title,
                    "content": data,
                    "links": image_links,
                    "source_id": file_path,
                }
            )
        except wikipedia.exceptions.DisambiguationError as e:
            # If there's a disambiguation page, we'll use the first option
            try:
                wiki = wikipedia.page(e.options[0])
                data = wiki.content
                image_links = wiki.images
                result.append(
                    {
                        "wiki_link": link,
                        "page_title": page_title,
                        "content": data,
                        "links": image_links,
                        "source_id": file_path,
                    }
                )
            except Exception as e:
                print(f"Error fetching data for {page_title}")
                return None
        except wikipedia.exceptions.PageError:
            print(f"Page not found for {page_title}")
            return None
        except Exception as e:
            print(f"An error occurred while fetching data for {page_title}: {str(e)}")
            return None

        return result

    def process(self, data: list, file_path: str):
        if not data:
            logging.warning("Data is empty")
            return None

        required_keys = ["page_title", "content", "links", "source_id", "wiki_link"]
        for item in data:
            if not all(
                key in item and (item[key] or key == "links") for key in required_keys
            ):
                logging.warning("Data is missing required keys or contains null values")
                return None

        # Process the data as needed
        logging.info(f"Processing data for file: {file_path}")
        # Add your processing logic here
        # Remove the 'content' key from each item in the data
        for item in data:
            if "content" in item:
                content = item["content"]
                del item["content"]

        # Create the directory if it doesn't exist
        save_dir = Path(f"JSON_Data/{file_path}")
        save_dir.mkdir(parents=True, exist_ok=True)

        # Define the save path
        save_path = Path(save_dir / f"{file_path}_wikidata.json")

        # Save the data to a JSON file
        with open(save_path, "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)

        logging.info(f"Data saved to {save_path}")

        return f"{content}"


#! Usage
# link = "https://en.wikipedia.org/wiki/Gitanjali"


# wiki = WikiSearch()
# result = wiki.getData(link=link, file_path="111")
# content = wiki.process(result, "111")
# print(content)
