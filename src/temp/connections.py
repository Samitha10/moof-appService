import os
from langchain_groq import ChatGroq
from langchain_voyageai.embeddings import VoyageAIEmbeddings
import pymongo


class LLM:
    def __init__(self):
        api_key = os.environ.get("GROQ_KEY")
        self.llm = ChatGroq(temperature=0.2, model="gemma2-9b-it", api_key=api_key)


llm = LLM().llm
print(llm.invoke("hello"))


class Embeddings:
    def __init__(self):
        voyage_api_key = os.environ.get("VOYAGE_KEY")
        self.embeddings = VoyageAIEmbeddings(
            voyage_api_key=voyage_api_key, model="voyage-2"
        )


class MongoDB:
    def __init__(self):
        Mongo_URI = os.environ.get("MONGO_URI")
        client = pymongo.MongoClient(Mongo_URI)
        self.db = client.get_database()

    def lives_collection(self):
        return self.db["lives"]

    def moments_collection(self):
        return self.db["moments"]

    def close_connection(self):
        self.client.close()
