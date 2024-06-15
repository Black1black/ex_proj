from src.config import settings

import redis.asyncio as redis


redis = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, encoding="utf8",
                          decode_responses=True)

sub = redis.pubsub()


