import time
from typing import Callable, Awaitable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp

from app.core.config import settings
from app.core.monitoring import track_user_activity, logger
from app.core.rate_limiter import RateLimiter

class ActivityTrackerMiddleware(BaseHTTPMiddleware):
    """
    Middleware to track user activity and apply rate limiting.
    """
    
    def __init__(
        self,
        app: ASGIApp,
        rate_limiter: RateLimiter = None,
    ) -> None:
        super().__init__(app)
        self.rate_limiter = rate_limiter or RateLimiter()
    
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Skip rate limiting for certain paths
        if self._should_skip_rate_limit(request.url.path):
            return await call_next(request)
        
        # Get user IP and user ID if authenticated
        user_ip = request.client.host if request.client else "unknown"
        user_id = None
        
        # Try to get user ID from auth token if available
        if "user" in request.scope:
            user = request.scope.get("user")
            if user and hasattr(user, "id"):
                user_id = str(user.id)
        
        # Apply rate limiting
        if user_id:
            # Higher limits for authenticated users
            limit_key = f"user:{user_id}"
            limit = settings.RATE_LIMIT_AUTHENTICATED
        else:
            # Lower limits for anonymous users
            limit_key = f"ip:{user_ip}"
            limit = settings.RATE_LIMIT_ANONYMOUS
        
        # Check rate limit
        if not self.rate_limiter.is_allowed(limit_key, limit):
            return Response(
                content={"detail": "Rate limit exceeded"},
                status_code=429,
                media_type="application/json"
            )
        
        # Track user activity
        if user_id:
            track_user_activity(user_id)
        
        # Process the request
        start_time = time.time()
        try:
            response = await call_next(request)
            
            # Add rate limit headers to the response
            self._add_rate_limit_headers(
                response, 
                limit_key=limit_key,
                limit=limit
            )
            
            return response
            
        except Exception as e:
            # Log the error but don't expose details to the client
            logger.error(f"Request failed: {str(e)}")
            raise
        
        finally:
            # Log request processing time
            process_time = time.time() - start_time
            logger.debug(
                f"Request processed in {process_time:.4f}s: "
                f"{request.method} {request.url.path} - "
                f"User: {user_id or 'anonymous'}"
            )
    
    def _should_skip_rate_limit(self, path: str) -> bool:
        """Check if rate limiting should be skipped for the given path"""
        # Skip rate limiting for health checks and metrics
        skip_paths = [
            "/health",
            "/metrics",
            "/docs",
            "/redoc",
            "/openapi.json"
        ]
        return any(path.startswith(p) for p in skip_paths)
    
    def _add_rate_limit_headers(
        self, 
        response: Response, 
        limit_key: str,
        limit: str
    ) -> None:
        """Add rate limit headers to the response"""
        if not hasattr(response, "headers"):
            return
            
        # Get rate limit info
        limit_info = self.rate_limiter.get_limit_info(limit_key, limit)
        
        # Add rate limit headers (RFC 6585)
        response.headers["X-RateLimit-Limit"] = str(limit_info["limit"])
        response.headers["X-RateLimit-Remaining"] = str(limit_info["remaining"])
        response.headers["X-RateLimit-Reset"] = str(limit_info["reset"])
        
        # Add RateLimit headers (GitHub style)
        response.headers["RateLimit-Limit"] = str(limit_info["limit"])
        response.headers["RateLimit-Remaining"] = str(limit_info["remaining"])
        response.headers["RateLimit-Reset"] = str(limit_info["reset"])
        response.headers["RateLimit-Used"] = str(limit_info["used"])
        
        # Add Retry-After header if rate limited
        if limit_info["remaining"] <= 0:
            response.headers["Retry-After"] = str(limit_info["reset"] - int(time.time()))
