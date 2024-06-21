from src.config import settings

import redis.asyncio as redis

from contextlib import asynccontextmanager


class RedisConnect:
    redis = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, encoding="utf8",
                              decode_responses=True)

    @asynccontextmanager
    async def get_redis_client(self):
        client = self.redis
        try:
            yield client
        finally:
            await client.close()

    @asynccontextmanager
    async def get_pubsub_client(self, redis_client):
        pubsub = redis_client.pubsub()
        try:
            yield pubsub
        finally:
            await pubsub.close()

