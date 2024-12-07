from fastapi import Request, HTTPException
from core.auth import verify_token
from starlette.middleware.base import BaseHTTPMiddleware

class JWTAuthenticationMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, protected_paths: list):
        super().__init__(app)
        self.protected_paths = protected_paths

    async def dispatch(self, request: Request, call_next):
        # Check if the request path needs protection
        if any(request.url.path.startswith(path) for path in self.protected_paths):
            token = request.headers.get("Authorization")

            if token is None:
                raise HTTPException(status_code=403, detail="Authorization token is missing")
            
            token = token.split(" ")[1] if token.startswith("Bearer ") else token
            
            user = await verify_token(token)
            
            if user is None:
                raise HTTPException(status_code=403, detail="Invalid or expired token")
            
            request.state.user = user
        
        # Call the next middleware or route handler
        response = await call_next(request)
        return response
