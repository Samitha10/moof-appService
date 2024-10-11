from pymongo import MongoClient
from bson import ObjectId
from qdrant_client import QdrantClient
import os
from dotenv import load_dotenv
import json
import sys
from pathlib import Path
from qdrant_client.http.models import Filter, FieldCondition, MatchValue

# Add the project root to the PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


load_dotenv()
# Initialize the MomentDatabase object
url = os.getenv("MONGO_URI")
qdrantUrl = os.getenv("QDRANT_URL")
qdrantKey = os.getenv("QDRANT_KEY")


class Moment_to_Vector_Handler:
    def __init__(
        self, mongo_url, qdrant_url, qdrant_api_key, db_ai, ai_moments, counts
    ):
        self.mongo_client = MongoClient(mongo_url)
        self.db = self.mongo_client[db_ai]
        self.collection = self.db[ai_moments]
        self.counts_collection = self.db[counts]
        self.qdrant_client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)

    def create_list_from_moments(self):
        LIST01 = []
        all_ids_in_list = []
        moments = self.collection.find()

        for moment in moments:
            moment_dict = {
                "_id": str(moment["_id"]),
                "moment_date": moment["moment_date"],
                "moment_title": moment["moment_title"],
                "moment_details": f"In {moment['moment_date']} {moment['era']}, {moment['moment_details']}",
                "life": str(moment["life"]),
            }

            LIST01.append(moment_dict)
            all_ids_in_list.append(str(moment["_id"]))

        self.counts_collection.update_one(
            {"_id": "moment_ids"},
            {"$set": {"all_ids": all_ids_in_list}},
            upsert=True,
        )

        return LIST01

    def find_missing_documents(self):
        LIST02 = []
        stored_ids_doc = self.counts_collection.find_one({"_id": "moment_ids"})

        if stored_ids_doc:
            all_ids_in_list = set(stored_ids_doc.get("all_ids", []))
        else:
            all_ids_in_list = set()

        mongo_ids_set = {
            str(moment["_id"]) for moment in self.collection.find({}, {"_id": 1})
        }
        missing_ids = mongo_ids_set - all_ids_in_list

        if missing_ids:
            missing_moments = self.collection.find(
                {"_id": {"$in": [ObjectId(_id) for _id in missing_ids]}}
            )

            for moment in missing_moments:
                missing_moment_dict = {
                    "_id": str(moment["_id"]),
                    "moment_date": moment["moment_date"],
                    "moment_title": moment["moment_title"],
                    "moment_details": f"In {moment['moment_date']} {moment['era']}, {moment['moment_details']}",
                    "life": str(moment["life"]),
                }

                LIST02.append(missing_moment_dict)

            self.counts_collection.update_one(
                {"_id": "moment_ids"},
                {"$addToSet": {"all_ids": {"$each": list(missing_ids)}}},
            )

        deleted_ai_ids = all_ids_in_list - mongo_ids_set
        if deleted_ai_ids:
            self.counts_collection.update_many(
                {"_id": "moment_ids"},
                {"$pull": {"all_ids": {"$in": list(deleted_ai_ids)}}},
            )
        LIST03 = list(deleted_ai_ids)
        print("Deleted ai moments are fouund", LIST03)
        return LIST02, LIST03

    def add_to_qdrant(self, original_list):
        docs = []
        metadata = []
        if original_list == []:
            print("No new moments to add to Qdrant.")
        else:
            for item in original_list:
                docs.append(item["moment_details"])
                item_copy = item.copy()
                del item_copy["moment_details"]
                metadata.append(item_copy)

            self.qdrant_client.add(
                collection_name="moments01",
                documents=docs,
                metadata=metadata,
                batch_size=128,
            )

    def delete_in_qdrant(self, delete_list):
        if not delete_list:
            print("No moments to delete from Qdrant.")
            return

        try:
            for delete_id in delete_list:
                filter_condition = Filter(
                    must=[FieldCondition(key="_id", match=MatchValue(value=delete_id))]
                )

                self.qdrant_client.delete(
                    collection_name="moments01", points_selector=filter_condition
                )

        except Exception as e:
            print(f"Error deleting moments from Qdrant: {e}")


class Moment_to_MongoDBHandler:
    def __init__(self, uri, db_origin, db_ai, origin_moments, ai_moments, origin_lifes):
        self.client = MongoClient(uri)
        self.db_origin = self.client[db_origin]
        self.db_ai = self.client[db_ai]
        self.origin_moments = self.db_origin[origin_moments]
        self.origin_lifes = self.db_origin[origin_lifes]
        self.ai_moments = self.db_ai[ai_moments]
        self.fields_to_keep = {
            "_id": 1,
            "moment_date": 1,
            "moment_title": 1,
            "moment_details": 1,
            "moment_type": 1,
            "era": 1,
            "life": 1,
        }
        # print(f"Origin database: {self.db_origin.name}")
        # print(f"AI database: {self.db_ai.name}")
        # print(f"Origin collection: {self.origin_moments.name}")
        # print(f"AI collection: {self.ai_moments.name}")

    def copy_moments_to_vector(self):
        # Print the name of the origin database and collection
        print(f"Origin database: {self.db_origin.name}")
        print(f"Origin collection: {self.origin_moments.name}")

        # Check if the collection exists
        if self.origin_moments.name not in self.db_origin.list_collection_names():
            print(
                f"Collection '{self.origin_moments.name}' does not exist in the origin database."
            )
            return

        # Count the total number of documents in the origin collection
        total_docs = self.origin_moments.count_documents({})
        print(f"Total documents in origin collection: {total_docs}")

        # Attempt to fetch the moments
        moments = list(self.origin_moments.find({}, self.fields_to_keep))
        print(f"Found {len(moments)} moments in origin database")

        if len(moments) == 0:
            print("No moments found. Checking the first document in the collection:")
            first_doc = self.origin_moments.find_one()
            if first_doc:
                print("Fields in the first document:")
                for key in first_doc.keys():
                    print(f"- {key}")
            else:
                print("The collection appears to be empty.")

        copied_count = 0
        for moment in moments:
            if not self.ai_moments.find_one({"_id": moment["_id"]}):
                self.ai_moments.insert_one(moment)
                copied_count += 1

        print(f"Copied {copied_count} new moments to AI database")

    def update_ai_moments(self):
        origin_moments_ids = set(
            doc["_id"] for doc in self.origin_moments.find({}, {"_id": 1})
        )
        ai_moment_ids = set(doc["_id"] for doc in self.ai_moments.find({}, {"_id": 1}))

        missing_ids_ai = origin_moments_ids - ai_moment_ids
        print(f"Found missing ids in ai_moments : {missing_ids_ai}")
        if missing_ids_ai:
            missing_documents = self.origin_moments.find(
                {"_id": {"$in": list(missing_ids_ai)}}, self.fields_to_keep
            )
            self.ai_moments.insert_many(missing_documents)

        deleted_ids_origin = ai_moment_ids - origin_moments_ids
        print(f"Found deleted ids in origin_moments : {deleted_ids_origin}")
        if deleted_ids_origin:
            self.ai_moments.delete_many({"_id": {"$in": list(deleted_ids_origin)}})

    def get_life_name_by_id(self, _id=None):
        # Step 2: Connect to the MongoDB server

        # Step 4: Access the lifes collection
        collection = self.origin_lifes

        # Step 6: Query the collection using the provided _id
        result = collection.find_one({"_id": ObjectId(_id)})

        # Step 7: Extract and return the life_name from the query result
        if result:
            return str(result.get("life_name", None))
        else:
            return None


class SimilarSearcher:
    def __init__(self, qdrant_url, qdrant_api_key):
        self.qdrant_client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)

    def search_in_qdrant(self, query_text, life_id):
        if life_id:
            search_result = self.qdrant_client.query(
                collection_name="moments01",
                query_text=query_text,
                limit=1,
                query_filter={
                    "must": [
                        {
                            "key": "life",
                            "match": {
                                "value": life_id  # Replace True with the actual value for filtering
                            },
                        }
                    ]
                },
            )
        else:
            search_result = self.qdrant_client.query(
                collection_name="moments01", query_text=query_text, limit=1
            )

        if search_result:
            hit = search_result[0]
            score = hit.score
            exsist_mom_id = hit.metadata["_id"]
        else:
            score = None
            exsist_mom_id = None
        return score, exsist_mom_id


class SimilarItemFinder:
    def __init__(self, file_path, vector_search):
        # Extract the filename without extension from the given file path
        # self.file_name = os.path.splitext(os.path.basename(file_path))[0]
        self.file_path = file_path
        self.json_file_path = (
            Path("JSON_Data") / self.file_path / f"{self.file_path}_processed.json"
        )
        self.vector_search = vector_search  # Search function passed as input

    def searcher(self, doc, life_id):
        return self.vector_search.search_in_qdrant(doc, life_id)

    def process_json(self, life_id):
        # Load the JSON data from the appropriate file
        with open(self.json_file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        output = []

        # Iterate through each incident in the 'incidents' list
        for i, incident in enumerate(data["incidents"]):
            description = incident.get("Description", "")

            if description:
                # Perform the search using the description
                score, exsist_mom_id = self.searcher(description, life_id=None)

                # Add the result to the output list
                output.append(
                    {
                        "created_mom_id": i,
                        "exsist_mom_id": exsist_mom_id,
                        "score": score,
                    }
                )
                # Save the output to a JSON file
                with open(
                    Path("JSON_Data")
                    / self.file_path
                    / f"{self.file_path}_similar.json",
                    "w",
                    encoding="utf-8",
                ) as outfile:
                    json.dump(output, outfile, indent=4)
        print(output)
        return output


# moment_to_mongo_handler = Moment_to_MongoDBHandler(
#     uri=url,
#     db_origin="mooflife_copy",
#     db_ai="mooflife_ai",
#     origin_moments="moments",
#     ai_moments="moments",
#     origin_lifes="lives",
# )

# moment_to_mongo_handler.copy_moments_to_vector()
# moment_to_mongo_handler.update_ai_moments()


# moment_vector_handler = Moment_to_Vector_Handler(
#     mongo_url=url,
#     qdrant_url=qdrantUrl,
#     qdrant_api_key=qdrantKey,
#     db_ai="mooflife_ai",
#     ai_moments="moments",
#     counts="Counts",
# )
# list01 = moment_vector_handler.create_list_from_moments()
# moment_vector_handler.add_to_qdrant(list01)


# list02, list03 = moment_vector_handler.find_missing_documents()
# moment_vector_handler.add_to_qdrant(list02)
# moment_vector_handler.delete_in_qdrant(list03)


# print(
#     moment_to_mongo_handler.get_life_name_by_id(
#         _id="66a9dcfcfd9351eda96be083", life_collection="lifes"
#     )
# )
