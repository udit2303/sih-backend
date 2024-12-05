from fastapi import FastAPI
from core.config import settings

app = FastAPI(debug=settings.debug)

@app.get("/")
async def root():
    return {"message": "Welcome to the Chatbot Backend!"}
    