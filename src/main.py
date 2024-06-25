from contextlib import asynccontextmanager
import time

from fastapi import FastAPI, Request
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from src.auth.router import router as auth_router
from src.chat.router import router as chat_router
from src.databases.redisdb import redis
from src.logger import logger
from src.users.router import router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    FastAPICache.init(RedisBackend(redis), prefix="cache")
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(users_router)

 # uvicorn app.main:app --reload
#  pip install black flake8 autoflake isort pyright
# black file --diff --color
# black /src тформатирует всё в папке
# isort src -rc

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    # При подключении Prometheus + Grafana подобный лог не требуется
    logger.info("Request handling time", extra={
        "process_time": round(process_time, 4)
    })
    return response