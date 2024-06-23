import redis.asyncio as redis
import os

redis_client = None


async def init_redis_pool(redis_url=None):
    global redis_client
    if redis_client is None:
        redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379")
        redis_client = await redis.from_url(redis_url, decode_responses=True)


async def close_redis_pool():
    global redis_client
    if redis_client:
        await redis_client.aclose()
        redis_client = None


def get_redis():
    global redis_client
    if redis_client is None:
        raise Exception("Redis client is not initialized")
    return redis_client
