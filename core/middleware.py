from fastapi import Request, HTTPException
from core.auth import verify_token

class JWTAuthenticationMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, request: Request):
        token = request.headers.get("Authorization")
        
        if token is None:
            raise HTTPException(status_code=403, detail="Authorization token is missing")
        
        token = token.split(" ")[1] if token.startswith("Bearer ") else token
        
        user = await verify_token(token)
        
        if user is None:
            raise HTTPException(status_code=403, detail="Invalid or expired token")
        
        request.state.user = user
        return await self.app(request)
