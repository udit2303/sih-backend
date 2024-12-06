from pydantic import BaseModel, Field
from bson import ObjectId
from datetime import datetime
from typing import Optional, List

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    class Config:
        json_encoders = {ObjectId: str}

class Message(BaseModel):
    sender: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.now(datetime.timezone.utc))

class Chat(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    context_id: PyObjectId
    user_id: PyObjectId 
    chats: List[Message]  
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
