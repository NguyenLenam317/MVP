from typing import Any, Optional
from functools import wraps
from datetime import datetime, timedelta
import json
from redis import Redis
from ..core.config import settings

class CacheService:
    def __init__(self):
        self.redis = Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True
        )

    def generate_cache_key(self, endpoint: str, params: dict) -> str:
        """Generate a unique cache key based on endpoint and parameters."""
        sorted_params = dict(sorted(params.items()))
        params_str = json.dumps(sorted_params, sort_keys=True)
        return f"cache:{endpoint}:{hash(params_str)}"

    def cache_response(
        self,
        endpoint: str,
        ttl_seconds: int = 3600  # Default 1 hour
    ):
        """Decorator to cache API responses."""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Generate cache key
                params = {k: v for k, v in kwargs.items() if k != "db"}
                cache_key = self.generate_cache_key(endpoint, params)

                # Check cache
                cached = self.redis.get(cache_key)
                if cached:
                    return json.loads(cached)

                # Execute function and cache result
                result = await func(*args, **kwargs)
                
                # Cache the result
                self.redis.setex(
                    cache_key,
                    timedelta(seconds=ttl_seconds),
                    json.dumps(result)
                )

                return result

            return wrapper
        return decorator

    def invalidate_cache(self, endpoint: str, params: dict):
        """Invalidate cache for specific endpoint and parameters."""
        cache_key = self.generate_cache_key(endpoint, params)
        self.redis.delete(cache_key)

    def invalidate_brand_cache(self, brand_id: int):
        """Invalidate all caches related to a specific brand."""
        pattern = f"cache:*brand_{brand_id}*"
        keys = self.redis.keys(pattern)
        if keys:
            self.redis.delete(*keys)

    def get_cache_stats(self) -> dict:
        """Get cache statistics."""
        return {
            "cache_size": self.redis.dbsize(),
            "cache_hits": self.redis.get("cache:hits") or 0,
            "cache_misses": self.redis.get("cache:misses") or 0,
            "cache_ttl": settings.CACHE_TTL
        }

# Initialize cache service
cache_service = CacheService()
