from pydantic import BaseModel, Field, field_validator
from bson import ObjectId
from datetime import datetime, timezone
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

    @classmethod
    def __get_pydantic_json_schema__(cls, schema):
        schema.update(type="string")

class Message(BaseModel):
    sender: str
    message: str
    image: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Chat(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    context_id: PyObjectId
    user_id: PyObjectId 
    chats: List[Message]  

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True

    @field_validator("id", mode="before", check_fields=False)
    def validate_id(cls, v):
        return PyObjectId.validate(v)

    @field_validator("context_id", mode="before", check_fields=False)
    def validate_context_id(cls, v):
        return PyObjectId.validate(v)

    @field_validator("user_id", mode="before", check_fields=False)
    def validate_user_id(cls, v):
        return PyObjectId.validate(v)

    @staticmethod
    def json_encoders():
        return {ObjectId: str}
