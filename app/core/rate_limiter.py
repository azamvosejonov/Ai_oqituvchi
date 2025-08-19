import time
from typing import Dict, Tuple, Optional, Union
import re
from datetime import datetime, timedelta
import redis
from fastapi import HTTPException, status

from app.core.config import settings

class RateLimiter:
    """
    Rate limiter implementation using Redis.
    Supports different rate limits for different types of users and endpoints.
    """
    
    def __init__(self, redis_client: redis.Redis = None):
        """
        Initialize the rate limiter.
        
        Args:
            redis_client: Optional Redis client instance. If not provided, a new one will be created.
        """
        self.redis = redis_client or redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD or None,
            decode_responses=False
        )
        
        # Default rate limits (can be overridden in settings)
        self.default_limits = {
            'global': '1000/minute',
            'anonymous': '100/minute',
            'authenticated': '1000/minute',
            'premium': '10000/minute',
            'admin': '100000/minute',
        }
        
        # Parse rate limit strings (e.g., '100/minute' -> (100, 60))
        self._parsed_limits = {}
        for key, limit_str in self.default_limits.items():
            self._parsed_limits[key] = self._parse_rate_limit(limit_str)
    
    def _parse_rate_limit(self, limit_str: str) -> Tuple[int, int]:
        """
        Parse a rate limit string into (limit, period_seconds) tuple.
        
        Args:
            limit_str: Rate limit string in the format 'N/period' (e.g., '100/minute')
            
        Returns:
            Tuple of (limit, period_seconds)
        """
        if not limit_str:
            return 0, 0
            
        try:
            limit, period = limit_str.split('/')
            limit = int(limit.strip())
            period = period.strip().lower()
            
            # Convert period to seconds
            if period.startswith('second'):
                period_sec = 1
            elif period.startswith('minute'):
                period_sec = 60
            elif period.startswith('hour'):
                period_sec = 3600
            elif period.startswith('day'):
                period_sec = 86400
            else:
                # Default to seconds if no known period
                period_sec = int(period)
                
            return limit, period_sec
            
        except (ValueError, AttributeError):
            # If parsing fails, use very high limits (effectively no limit)
            return 10**9, 1
    
    def get_limit_info(
        self, 
        key: str, 
        limit_str: Optional[str] = None
    ) -> Dict[str, int]:
        """
        Get rate limit information for a given key.
        
        Args:
            key: The rate limit key (e.g., 'user:123' or 'ip:1.2.3.4')
            limit_str: Optional rate limit string to use (e.g., '100/minute')
            
        Returns:
            Dictionary with rate limit information
        """
        if not settings.USE_RATE_LIMITING:
            return {
                'limit': 10**9,
                'remaining': 10**9,
                'reset': int(time.time()) + 60,
                'used': 0
            }
            
        # Get the appropriate rate limit
        if limit_str:
            limit, period = self._parse_rate_limit(limit_str)
        else:
            # Try to determine the limit based on the key prefix
            if key.startswith('user:'):
                limit, period = self._parsed_limits.get('authenticated', (1000, 60))
            elif key.startswith('premium:'):
                limit, period = self._parsed_limits.get('premium', (10000, 60))
            elif key.startswith('admin:'):
                limit, period = self._parsed_limits.get('admin', (100000, 60))
            else:
                limit, period = self._parsed_limits.get('anonymous', (100, 60))
        
        # Get the current window
        now = int(time.time())
        window_start = now // period * period
        window_key = f"ratelimit:{key}:{window_start}"
        
        # Get current count
        try:
            current = int(self.redis.get(window_key) or 0)
        except (redis.RedisError, ValueError):
            current = 0
        
        # Calculate remaining requests and reset time
        remaining = max(0, limit - current - 1)
        reset = window_start + period
        
        return {
            'limit': limit,
            'remaining': remaining,
            'reset': reset,
            'used': current
        }
    
    def is_allowed(
        self, 
        key: str, 
        limit_str: Optional[str] = None
    ) -> bool:
        """
        Check if a request is allowed based on the rate limit.
        
        Args:
            key: The rate limit key (e.g., 'user:123' or 'ip:1.2.3.4')
            limit_str: Optional rate limit string to use (e.g., '100/minute')
            
        Returns:
            True if the request is allowed, False if rate limited
        """
        if not settings.USE_RATE_LIMITING:
            return True
            
        # Get the appropriate rate limit
        if limit_str:
            limit, period = self._parse_rate_limit(limit_str)
        else:
            # Try to determine the limit based on the key prefix
            if key.startswith('user:'):
                limit, period = self._parsed_limits.get('authenticated', (1000, 60))
            elif key.startswith('premium:'):
                limit, period = self._parsed_limits.get('premium', (10000, 60))
            elif key.startswith('admin:'):
                limit, period = self._parsed_limits.get('admin', (100000, 60))
            else:
                limit, period = self._parsed_limits.get('anonymous', (100, 60))
        
        if limit <= 0 or period <= 0:
            return True
        
        # Get the current window
        now = int(time.time())
        window_start = now // period * period
        window_key = f"ratelimit:{key}:{window_start}"
        
        # Use a pipeline for atomic operations
        pipe = self.redis.pipeline()
        
        try:
            # Increment the counter for this window
            pipe.incr(window_key)
            
            # Set expiration for the key (slightly longer than the period)
            pipe.expire(window_key, period + 10)
            
            # Execute the pipeline
            results = pipe.execute()
            
            # The first result is the new counter value
            current = results[0] if results else 0
            
            return current <= limit
            
        except redis.RedisError:
            # If Redis is down, allow the request
            return True
    
    def get_remaining_requests(
        self, 
        key: str, 
        limit_str: Optional[str] = None
    ) -> int:
        """
        Get the number of remaining requests for a given key.
        
        Args:
            key: The rate limit key (e.g., 'user:123' or 'ip:1.2.3.4')
            limit_str: Optional rate limit string to use (e.g., '100/minute')
            
        Returns:
            Number of remaining requests in the current window
        """
        limit_info = self.get_limit_info(key, limit_str)
        return limit_info['remaining']
    
    def reset_limit(self, key: str) -> None:
        """
        Reset the rate limit for a given key.
        
        Args:
            key: The rate limit key to reset
        """
        if not settings.USE_RATE_LIMITING:
            return
            
        try:
            # Delete all rate limit keys for this identifier
            pattern = f"ratelimit:{key}:*"
            keys = self.redis.keys(pattern)
            if keys:
                self.redis.delete(*keys)
        except redis.RedisError:
            pass
