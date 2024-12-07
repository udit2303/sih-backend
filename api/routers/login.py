from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from core.database import db
from models.user import User
from bson import ObjectId
from jose import jwt 
import os
from datetime import datetime, timezone
from core.auth import create_access_token, verify_password, hash_password

# Pydantic Models
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    refCode : int = 0

class UserLogin(BaseModel):
    email: EmailStr
    password: str

router = APIRouter()

# Signup Route
@router.post("/signup")
async def signup(user: UserCreate):
    users_collection = db.get_collection("users")

    existing_user = await users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = hash_password(user.password)

    new_user = {
        "name": user.username,
        "email": user.email,
        "password": hashed_password,
        "is_admin": True if user.refCode == 1234 else False,    
        "created_at": datetime.now(timezone.utc)
    }
    result = await users_collection.insert_one(new_user)
    access_token = create_access_token(
        data={"sub": str(existing_user["_id"])}
    )

    return {"msg": "User created successfully", "user_id": str(result.inserted_id), "access_token": access_token, "token_type": "bearer"}

# Login Route
@router.post("/login")
async def login(user: UserLogin):
    users_collection = db.get_collection("users")
    # Find user by email
    existing_user = await users_collection.find_one({"email": user.email})
    if not existing_user:
        raise HTTPException(status_code=400, detail="Invalid email or password")

    # Verify password
    if not verify_password(user.password, existing_user["password"]):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    # Create JWT token
    access_token = create_access_token(
        data={"sub": str(existing_user["email"])}
    )
    return {"access_token": access_token, "token_type": "bearer"}
