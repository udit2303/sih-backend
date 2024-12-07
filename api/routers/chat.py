from io import BytesIO
import os
from fastapi import APIRouter, HTTPException, Depends, Request, Form
from bson import ObjectId
from datetime import datetime, timezone
from typing import List
from models.chat import Chat, Message
from models.context import Context
from models.user import User
from core.database import db
from redisDB.database import redis_cache as cache   
from core.middleware import get_current_user
import base64
from PIL import Image
# from core.model import model
router = APIRouter()

# GET /context - Get all context titles and IDs for the authenticated user
@router.get("/context")
async def get_all_contexts(user: User = Depends(get_current_user)):
    context_collection = db.contexts_collection
    contexts_cursor = context_collection.find({"user_id": ObjectId(user["_id"])})
    contexts = await contexts_cursor.to_list(length=100)  # Limit to 100 contexts for now
    #Array with only the context titles and id
    filtered_contexts = [{"title": context["title"], "id": str(context["_id"])} for context in contexts]
    print("Filtered Contexts: ", filtered_contexts)
    return filtered_contexts
# POST /context - Create a new context and return all context IDs and titles for the user
@router.post("/context")
async def create_context(message: str = Form(...), user: User = Depends(get_current_user)):
    context_collection = db.contexts_collection
    new_context = {
        "user_id": user["_id"],
        "title": message[:10] + "...",  # Using message as title here temporarily
        "created_at": datetime.now(timezone.utc)
    }
    result = await context_collection.insert_one(new_context)
    new_context["_id"] = result.inserted_id
    new_chat = {
        "context_id": new_context["_id"],
        "user_id": user["_id"],
        "chats": [
            {
                "sender": "user",
                "message": message,
                "timestamp": datetime.now(timezone.utc)
            },
            {
                "sender": "bot",
                "message": "Welcome to the new context!",
                "timestamp": datetime.now(timezone.utc)
            }
        ]
    }
    db.chats_collection.insert_one(new_chat)
    return {"id": str(new_context["_id"]), "title": new_context["title"]}


@router.get("/{context_id}")
async def get_chats_by_context(context_id: str, user: User = Depends(get_current_user)):
    print("Getting chat for context: ", context_id)

    chat_collection  = db.chats_collection
    chat_document = await cache.get(context_id, user["_id"])
    if not chat_document:
        raise HTTPException(status_code=404, detail="Chat context not found for this user")
    
    return chat_document

@router.post("/{context_id}")
async def post_chat_to_context(context_id: str, chat_request: Request, user: User = Depends(get_current_user)):
    chat_document = await chat_request.json()
    if(chat_document.get("image")):
        print("Image received")
        #Base 64 image, build it
        image_data = base64.b64decode(chat_document["image"])
        image = Image.open(BytesIO(image_data))
        image_path = f"images/{context_id}_{datetime.now().timestamp()}.png"
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        image.save(image_path)
        chat_document["image"] = image_path.replace("images/", "")
    print(chat_document)
    new_message = [{
        "sender": "user",
        "message": chat_document["message"],
        "image": chat_document.get("image") if chat_document.get("image") else None,
        "timestamp": datetime.now(timezone.utc)
    }]
    # ai_response = model.getResponse(chat_request)
    ai_response = "This is a placeholder response from the AI model"
    new_message.append({
        "sender": "bot",
        "message": ai_response,
        "timestamp": datetime.now(timezone.utc)
    })
    await cache.update(context_id, user["_id"], new_message)
    return new_message