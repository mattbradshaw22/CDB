# CRUD_Module.py

from pymongo import MongoClient
from pymongo.server_api import ServerApi
from urllib.parse import quote_plus
from dotenv import load_dotenv
import os

class CRUD:
    """CRUD operations for the animals collection in MongoDB"""

    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()

        # Read credentials from environment variables
        user = os.getenv("MONGO_USER")
        password = quote_plus(os.getenv("MONGO_PASS"))  # encode special chars
        cluster = os.getenv("MONGO_CLUSTER")
        db_name = os.getenv("MONGO_DB", "aac")
        col_name = os.getenv("MONGO_COL", "animals")
        app_name = os.getenv("APP_NAME", "Cluster0")

        # Verify required values are set
        if not all([user, password, cluster]):
            raise ValueError("Missing MongoDB credentials in .env file")

        # Build the Atlas connection string
        uri = f"mongodb+srv://{user}:{password}@{cluster}/{db_name}?retryWrites=true&w=majority&appName={app_name}"

        # Connect to MongoDB
        self.client = MongoClient(uri, server_api=ServerApi('1'))
        self.database = self.client[db_name]
        self.collection = self.database[col_name]

        # Ping to verify connection
        try:
            self.client.admin.command('ping')
            print("✅ Successfully connected to MongoDB Atlas!")
        except Exception as e:
            print("❌ Connection failed:", e)

    # C
    def create(self, data: dict):
        if not data:
            raise ValueError("Empty data; nothing to insert.")
        result = self.collection.insert_one(data)
        return str(result.inserted_id)

    # R
    def read(self, query: dict = None, projection: dict | None = None):
        query = query or {}
        cursor = self.collection.find(query, projection or None)
        return list(cursor)

    # U
    def update(self, query: dict, updated_values: dict):
        if not query:
            raise ValueError("Empty query; nothing to update.")
        result = self.collection.update_many(query, {"$set": updated_values})
        return {"matched": result.matched_count, "modified": result.modified_count}

    # D
    def delete(self, query: dict, many: bool = False):
        if not query:
            raise ValueError("Empty query; nothing to delete.")
        if many:
            result = self.collection.delete_many(query)
        else:
            result = self.collection.delete_one(query)
        return {"deleted": result.deleted_count}
