from fastapi import FastAPI
from fastapi_cache import FastAPICache

from src.auth.router import router as auth_router
from src.chat.router import router as chat_router

from src.utils.mongo_utils import init_mongo_collections


from contextlib import asynccontextmanager

from fastapi_cache.backends.redis import RedisBackend

from src.databases.redisdb import redis

@asynccontextmanager
async def lifespan(app: FastAPI):
    FastAPICache.init(RedisBackend(redis), prefix="cache")
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)
app.include_router(chat_router)

 # uvicorn app.main:app --reload



# @app.on_event("startup")
# async def startup_event():
#     'Стартовая инициализация индексов и коллекций в mongo_db'
#     await init_mongo_collections()
