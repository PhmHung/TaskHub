import redis.asyncio as redis
from redis.asyncio.connection import ConnectionPool

from app.core.config import settings

pool = ConnectionPool.from_url(settings.redis_url, decode_responses=True)


async def get_redis_client() -> redis.Redis:
    return redis.Redis(connection_pool=pool)