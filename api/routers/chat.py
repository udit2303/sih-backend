from fastapi import APIRouter, HTTPException, Depends
from bson import ObjectId
from datetime import datetime, timezone
from typing import List
from models.chat import Chat, Message
from models.context import Context
from models.user import User
from core.database import db
from redisDB.database import redis_cache as cache   
from core.middleware import get_current_user
# from core.model import model
router = APIRouter()
chat_collection  = db.chats_collection
context_collection = db.contexts_collection
@router.get("/{context_id}", response_model=Chat)
async def get_chats_by_context(context_id: str, user: User = Depends(get_current_user)):
    chat_document = await cache.get(context_id, user.id)
    if not chat_document:
        raise HTTPException(status_code=404, detail="Chat context not found for this user")
    
    return chat_document

@router.post("/{context_id}", response_model=Chat)
async def post_chat_to_context(context_id: str, chat_request: str, user: User = Depends(get_current_user)):

    new_message = [{
        "sender": "user",
        "message": chat_request,
        "timestamp": datetime.now(timezone.utc)
    }]
    # ai_response = model.getResponse(chat_request)
    ai_response = "This is a placeholder response from the AI model"
    new_message.append({
        "sender": "bot",
        "message": ai_response,
        "timestamp": datetime.now(datetime.timezone.utc)
    })
    cache.update(context_id, user.id, new_message)
    return {"msg": ai_response}

# GET /context - Get all context titles and IDs for the authenticated user
@router.get("/context")
async def get_all_contexts(user: User = Depends(get_current_user)):

    contexts_cursor = context_collection.find({"user_id": ObjectId(user.id)})
    contexts = await contexts_cursor.to_list(length=100)  # Limit to 100 contexts for now

    return {"contexts": contexts}

# POST /context - Create a new context and return all context IDs and titles for the user
@router.post("/context")
async def create_context(create_request: Message, user: User = Depends(get_current_user)):

    # Create a new context document
    new_context = {
        "user_id": ObjectId(user.id),
        "title": create_request.message,  # Using message as title here temporarily
        "created_at": datetime.now(timezone.utc),
    }

    # Insert the new context
    result = await context_collection.insert_one(new_context)

    contexts_cursor = context_collection.find({"user_id": ObjectId(user.id)})
    contexts = await contexts_cursor.to_list(length=100)

    return {"msg": "Context created successfully", "contexts": contexts}

