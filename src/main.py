# import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from src.auth.router import router as auth_router
from src.chat.router import router as chat_router
from src.databases.redisdb import redis

# from src.utils.mongo_utils import init_mongo_collections







@asynccontextmanager
async def lifespan(app: FastAPI):
    FastAPICache.init(RedisBackend(redis), prefix="cache")
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)
app.include_router(chat_router)

 # uvicorn app.main:app --reload
#  pip install black flake8 autoflake isort pyright
# black file --diff --color
# black /src тформатирует всё в папке
# isort src -rc

