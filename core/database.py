from motor.motor_asyncio import AsyncIOMotorClient
from core.config import settings
from bson import ObjectId
from pymongo.errors import CollectionInvalid
import json
from typing import Optional

class MongoDB:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(MongoDB, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    client: AsyncIOMotorClient = None
    database = None
    users_collection = None
    contexts_collection = None
    chats_collection = None

    async def connect(self):
        """Establish a connection to MongoDB and setup collections."""
        try:
            self.client = AsyncIOMotorClient(settings.database_url)
            self.database = self.client.get_database()
            self.users_collection = self.database.get_collection("users")
            self.contexts_collection = self.database.get_collection("contexts")
            self.chats_collection = self.database.get_collection("chats")
            print("Connected to MongoDB!")
        except Exception as e:
            print(f"Failed to connect to MongoDB: {e}")

    async def close(self):
        """Close the MongoDB connection."""
        if self.client:
            self.client.close()
            print("Disconnected from MongoDB!")

    async def _create_indexes(self):
        """Create indexes for collections (optional)."""
        await self.chats_collection.create_index([("context_id", 1)])

    # Helper method to get a collection
    def get_collection(self, collection_name: str):
        return self.database.get_collection(collection_name)

    # Utility functions for CRUD operations
    async def find_one(self, collection_name: str, query: dict) -> Optional[dict]:
        collection = self.get_collection(collection_name)
        return await collection.find_one(query)

    async def find_many(self, collection_name: str, query: dict) -> list:
        collection = self.get_collection(collection_name)
        cursor = collection.find(query)
        return await cursor.to_list(length=None)

    async def insert_one(self, collection_name: str, document: dict) -> dict:
        collection = self.get_collection(collection_name)
        result = await collection.insert_one(document)
        return {"inserted_id": str(result.inserted_id)}

    async def update_one(self, collection_name: str, query: dict, update: dict) -> dict:
        collection = self.get_collection(collection_name)
        result = await collection.update_one(query, {'$set': update})
        return {"matched_count": result.matched_count, "modified_count": result.modified_count}

    async def delete_one(self, collection_name: str, query: dict) -> dict:
        collection = self.get_collection(collection_name)
        result = await collection.delete_one(query)
        return {"deleted_count": result.deleted_count}



# Instances for MongoDB and Redis
db = MongoDB()

# Connection handlers
async def connect():
    """Connect to MongoDB"""
    await db.connect()

async def close():
    """Close connections to MongoDB """
    await db.close()
