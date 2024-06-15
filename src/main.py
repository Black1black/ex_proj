from fastapi import FastAPI

from src.auth.router import router as auth_router
from src.chat.router import router as chat_router

from src.utils.mongo_utils import init_mongo_collections


app = FastAPI()
app.include_router(auth_router)
app.include_router(chat_router)

 # uvicorn app.main:app --reload



@app.on_event("startup")
async def startup_event():
    'Стартовая инициализация индексов и коллекций в mongo_db'
    await init_mongo_collections()
