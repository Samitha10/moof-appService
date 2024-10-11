from dotenv import load_dotenv
from pymongo import MongoClient, errors
import json
import sys
import os
from pathlib import Path

# Add the project root to the PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


load_dotenv()
# Initialize the MomentDatabase object
url = os.getenv("MONGO_URI")


class MongoDBJsonSaver:
    def __init__(self, mongo_url, database):
        self.mongo_client = MongoClient(mongo_url)
        self.database = self.mongo_client[database]

    def mongoSaver(self, collection_name: str, operation_id: str):
        operation_id = str(operation_id)
        collection_name = self.database[collection_name]

        # Directory structure
        directory = Path(f"JSON_Data/{operation_id}")

        # Load JSON files from enhanced and extracted folders
        for folder in ["extracted", "enhanced"]:
            folder_path = os.path.join(directory, folder)
            for file in os.listdir(folder_path):
                if file.endswith(".json"):
                    file_path = os.path.join(folder_path, file)
                    with open(file_path, "r") as f:
                        data = json.load(f)
                        data["_id"] = (
                            f"{operation_id}_{file}"  # Optional: Assign file name as _id
                        )
                        try:
                            collection_name.update_one(
                                {"_id": data["_id"]}, {"$set": data}, upsert=True
                            )
                        except Exception as e:
                            print(f"Error processing file {file}: {e}")
                            continue

        # Load the _processed.json file
        processed_file_path = directory / f"{operation_id}_processed.json"
        if processed_file_path.exists():
            with open(processed_file_path, "r") as f:
                data = json.load(f)
                data["_id"] = operation_id + "_processed"
                try:
                    collection_name.update_one(
                        {"_id": data["_id"]}, {"$set": data}, upsert=True
                    )
                except Exception as e:
                    print(f"Error processing _processed.json: {e}")

        # Load the _similar.json file
        similar_file_path = directory / f"{operation_id}_similar.json"
        if similar_file_path.exists():
            with open(similar_file_path, "r") as f:
                data = json.load(f)
                new_data = {"_id": operation_id + "_similar", "similar_items": data}
                try:
                    collection_name.update_one(
                        {"_id": new_data["_id"]}, {"$set": new_data}, upsert=True
                    )
                except Exception as e:
                    print(f"Error processing _similar.json: {e}")

        # Load the _wikidata.json file
        wiki_file_path = directory / f"{operation_id}_wikidata.json"
        if wiki_file_path.exists():
            with open(wiki_file_path, "r") as f:
                data = json.load(f)
                new_data = {"_id": operation_id + "_wikidata", "wikidata": data}
                try:
                    collection_name.update_one(
                        {"_id": new_data["_id"]}, {"$set": new_data}, upsert=True
                    )
                except Exception as e:
                    print(f"Error processing _wikidata.json: {e}")


"""     def mongoSaver(self, collection_name: str):
        operation_id = str(collection_name)
        collection_name = self.database[collection_name]
        # Directory structure
        directory = Path(f"JSON_Data/{operation_id}")

        # Load JSON files from enhanced and extracted folders
        for folder in ["extracted", "enhanced"]:
            folder_path = os.path.join(directory, folder)
            for file in os.listdir(folder_path):
                if file.endswith(".json"):
                    file_path = os.path.join(folder_path, file)
                    with open(file_path, "r") as f:
                        data = json.load(f)
                        data["_id"] = file  # Optional: Assign file name as _id
                        try:
                            collection_name.insert_one(data)
                        except errors.DuplicateKeyError:
                            collection_name.update_one(
                                {"_id": file}, {"$set": data}, upsert=True
                            )

        # Load the _processed.json file
        processed_file_path = directory / f"{operation_id}_processed.json"
        with open(processed_file_path, "r") as f:
            data = json.load(f)
            data["_id"] = (
                operation_id + "_processed"
            )  # Optional: Assign file name as _id
            try:
                collection_name.insert_one(data)
            except errors.DuplicateKeyError:
                collection_name.update_one(
                    {"_id": operation_id + "_processed"}, {"$set": data}, upsert=True
                )
        # Load the _similar.json file
        similar_file_path = directory / f"{operation_id}_similar.json"
        if similar_file_path.exists():
            with open(similar_file_path, "r") as f:
                data = json.load(f)
                new_data = {"_id": operation_id + "_similar", "similar_items": data}

                try:
                    collection_name.insert_one(new_data)
                except errors.DuplicateKeyError:
                    collection_name.update_one(
                        {"_id": operation_id + "_similar"},
                        {"$set": new_data},
                        upsert=True,
                    ) """

# saver = MongoDBJsonSaver(url, "mooflife")
# saver.mongoSaver(operation_id="gitanjali", collection_name="JSON_Data")
