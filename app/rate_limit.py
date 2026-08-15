from fastapi_limiter import FastAPILimiter
from fastapi_limiter.util import get_remote_address
from redis.asyncio import from_url
import os

async def init_rate_limiter():
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    await FastAPILimiter.init(await from_url(redis_url))
