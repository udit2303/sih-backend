from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from core.config import settings
from api.routers.upload import router as upload_router
from api.routers.chat import router as chat_router
from api.routers.train import router as train_router
from api.routers.login import router as login_router
from fastapi.middleware.cors import CORSMiddleware
# from core.middleware import JWTAuthenticationMiddleware
from redisDB.database import initialize_services, redis_cache
app = FastAPI(debug=settings.debug)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change "*" to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# app.add_middleware(JWTAuthenticationMiddleware, protected_paths=[])
app.mount("/images", StaticFiles(directory="images"), name="images")
app.include_router(upload_router, prefix="/api/upload", tags=["Upload"])
app.include_router(train_router, prefix="/api/train", tags=["Training"])  # Example for the training route
app.include_router(chat_router, prefix="/api/chat", tags=["Chat"])  # Example for the chat route
app.include_router(login_router, prefix="/api/auth", tags=["Auth"])  # Example for the authentication route

@app.on_event("startup")
async def startup_event():
    await initialize_services()
# Root route
@app.get("/")
def read_root():
    return {"msg": "Welcome to the API"}
