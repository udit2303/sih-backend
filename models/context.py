from pydantic import BaseModel, Field, field_validator
from bson import ObjectId
from datetime import datetime
from typing import Optional

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

class Context(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId  
    title: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True

    @field_validator("id", mode="before", check_fields=False)
    def validate_id(cls, v):
        return PyObjectId.validate(v)

    @field_validator("user_id", mode="before", check_fields=False)
    def validate_user_id(cls, v):
        return PyObjectId.validate(v)

    @staticmethod
    def json_encoders():
        return {ObjectId: str}
