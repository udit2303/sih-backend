from fastapi import Request, HTTPException, Depends
from core.auth import verify_token
from models.user import User

async def get_current_user(request: Request) -> User:
    """
    Dependency to extract and verify the current user from the Authorization header.
    """
    token = request.headers.get("Authorization")
    if not token:
        raise HTTPException(status_code=403, detail="Authorization token is missing")
    token = token.split(" ")[1] if token.startswith("Bearer ") else token
    user = await verify_token(token)
    if not user:
        raise HTTPException(status_code=403, detail="Invalid or expired token")
    
    return user
