from typing import Any, Optional, Union
import json
import redis
from functools import wraps
from datetime import timedelta

from app.core.config import settings

# Initialize Redis client
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD or None,
    decode_responses=True
)

def get_cache_key(prefix: str, *args, **kwargs) -> str:
    """Generate a cache key from function arguments"""
    key_parts = [prefix]
    
    # Add positional arguments
    for arg in args:
        if isinstance(arg, (str, int, float, bool)):
            key_parts.append(str(arg))
    
    # Add keyword arguments
    for k, v in sorted(kwargs.items()):
        if isinstance(v, (str, int, float, bool)):
            key_parts.append(f"{k}:{v}")
    
    return ":".join(key_parts)

def cache_result(prefix: str, ttl: int = 300):
    """
    Decorator to cache function results in Redis
    
    Args:
        prefix: Prefix for cache key
        ttl: Time to live in seconds (default: 5 minutes)
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Don't use cache if Redis is not available
            if not settings.USE_CACHE:
                return await func(*args, **kwargs)
                
            # Generate cache key
            cache_key = get_cache_key(prefix, *args, **kwargs)
            
            # Try to get from cache
            try:
                cached = redis_client.get(cache_key)
                if cached is not None:
                    return json.loads(cached)
            except redis.RedisError:
                # If Redis fails, just continue without cache
                pass
            
            # Call the original function
            result = await func(*args, **kwargs)
            
            # Cache the result
            try:
                if result is not None:
                    redis_client.setex(
                        cache_key,
                        timedelta(seconds=ttl),
                        json.dumps(result, default=str)
                    )
            except redis.RedisError:
                # If caching fails, just continue
                pass
                
            return result
        
        return wrapper
    return decorator

def invalidate_cache(prefix: str):
    """
    Decorator to invalidate cache entries matching a prefix
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Call the original function first
            result = await func(*args, **kwargs)
            
            # Invalidate cache
            try:
                if settings.USE_CACHE:
                    # Find all keys matching the prefix
                    keys = redis_client.keys(f"{prefix}:*")
                    if keys:
                        redis_client.delete(*keys)
            except redis.RedisError:
                # If invalidation fails, just continue
                pass
                
            return result
        
        return wrapper
    return decorator

def clear_all_caches():
    """Clear all cached data"""
    try:
        if settings.USE_CACHE:
            redis_client.flushdb()
            return True
    except redis.RedisError:
        pass
    return False
