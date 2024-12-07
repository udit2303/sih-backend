import asyncio
from redis.asyncio import Redis
from bson import ObjectId
from datetime import datetime
from pymongo import ReturnDocument
from pydantic import BaseModel
import json
from core.database import db  
# Redis Connection Manager
class RedisCache:
    """Redis caching and synchronization utility."""
    
    def __init__(self, redis_url: str):
        self.client = Redis.from_url(redis_url, decode_responses=True)
    
    async def connect(self):
        """Connect to Redis and subscribe to key expiration events."""
        await self.client.config_set("notify-keyspace-events", "Ex")
        self.pubsub = self.client.pubsub()
        await self.pubsub.subscribe("__keyevent@0__:expired")
        asyncio.create_task(self.listen_for_evictions())
        print("Connected to Redis!")
    
    async def listen_for_evictions(self):
        """Listen for Redis key eviction events and handle them."""
        async for message in self.pubsub.listen():
            if message["type"] == "message":
                key = message["data"]
                await self.on_eviction(key)

    async def close(self):
        """Close the Redis connection."""
        await self.pubsub.close()
        await self.client.close()
        print("Disconnected from Redis!")

    async def get(self, context_id: str, user_id: str):
        """
        Retrieve chats from Redis for the given context and user ID.
        If not found, fetch from MongoDB, populate Redis, and return the data.
        """
        redis_key = f"{context_id}:user:{user_id}"
        chats_json = await self.client.get(redis_key)

        if chats_json:
            return json.loads(chats_json)
        
        chat_document = await db.chats_collection.find_one(
            {"context_id": ObjectId(context_id), "user_id": ObjectId(user_id)}
        )
        if not chat_document:
            return None

        # Transform MongoDB data for caching
        chat_document["_id"] = str(chat_document["_id"])
        chat_document["context_id"] = str(chat_document["context_id"])
        chat_document["user_id"] = str(chat_document["user_id"])
        for message in chat_document["chats"]:
            message["timestamp"] = message["timestamp"].isoformat()

        await self.client.set(redis_key, json.dumps(chat_document), ex=3600)
        return chat_document

    async def update(self, context_id: str, user_id: str, new_chats: list):    
        """
        Update chats in Redis and MongoDB for the given context and user ID.
        """
        redis_key = f"{context_id}:user:{user_id}"
        chat_document = await self.get(context_id, user_id)  # Fetch current data

        if not chat_document:
            raise ValueError("Chat context not found.")

        # Update chats in memory
        chat_document["chats"].extend(new_chats)
        for message in new_chats:
            message["timestamp"] = message["timestamp"].isoformat()

        # Update Redis
        await self.client.set(redis_key, json.dumps(chat_document), ex=3600)

    async def periodic_sync(self, interval: int = 600):
        """
        Periodically sync Redis data to MongoDB.
        """
        while True:
            keys = await self.client.keys("*:user:*")
            for key in keys:
                chats_json = await self.client.get(key)
                if chats_json:
                    chat_data = json.loads(chats_json)

                    # Update MongoDB with the latest data
                    await db.chats_collection.find_one_and_replace(
                        {"context_id": ObjectId(chat_data["context_id"]), "user_id": ObjectId(chat_data["user_id"])},
                        chat_data,
                        upsert=True
                    )
            print("Periodic sync completed.")
            await asyncio.sleep(interval)

    async def on_eviction(self, key: str):
        """
        Handle eviction events from Redis and update MongoDB.
        """
        chats_json = await self.client.get(key)
        if chats_json:
            chat_data = json.loads(chats_json)

            # Update MongoDB with the evicted data
            await db.chats_collection.find_one_and_replace(
                {"context_id": ObjectId(chat_data["context_id"]), "user_id": ObjectId(chat_data["user_id"])},
                chat_data,
                upsert=True
            )
            print(f"Evicted key {key} synced to MongoDB.")

# Initialize Redis
redis_cache = RedisCache(redis_url="redis://localhost:6379")

# Example usage in your application
async def initialize_services():
    await redis_cache.connect()
    await db.connect()

async def close_services():
    await redis_cache.close()
    await db.close()
