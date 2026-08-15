import functools
import json
from datetime import timedelta
import redis
import os

redis_client = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

def cache(expire: int = 300):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            cached = redis_client.get(key)
            if cached:
                return json.loads(cached)
            
            result = await func(*args, **kwargs)
            redis_client.setex(key, expire, json.dumps(result, default=str))
            return result
        return wrapper
    return decorator
