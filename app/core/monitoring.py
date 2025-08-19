import time
import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from functools import wraps

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from prometheus_client import Counter, Histogram, Gauge, generate_latest, REGISTRY

from app.core.config import settings

# Configure logger
logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP Requests',
    ['method', 'endpoint', 'http_status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP Request Latency',
    ['method', 'endpoint']
)

ACTIVE_USERS = Gauge(
    'active_users',
    'Number of active users in the last 5 minutes'
)

# In-memory storage for active users (in a production environment, use Redis)
active_users: Dict[str, float] = {}

class MonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware to monitor HTTP requests and responses"""
    
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Skip metrics endpoint
        if request.url.path == '/metrics':
            return await call_next(request)
        
        # Track request start time
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate request duration
        process_time = time.time() - start_time
        
        # Update metrics
        endpoint = request.url.path
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=endpoint,
            http_status=response.status_code
        ).inc()
        
        REQUEST_LATENCY.labels(
            method=request.method,
            endpoint=endpoint
        ).observe(process_time)
        
        # Log request
        logger.info(
            f"{request.method} {endpoint} - "
            f"Status: {response.status_code} - "
            f"Duration: {process_time:.4f}s"
        )
        
        return response

def track_user_activity(user_id: str):
    """Track user activity for active users monitoring"""
    if not user_id:
        return
    
    active_users[user_id] = time.time()
    
    # Clean up inactive users (5 minutes threshold)
    current_time = time.time()
    inactive_users = [
        uid for uid, last_seen in active_users.items()
        if current_time - last_seen > 300  # 5 minutes
    ]
    
    for uid in inactive_users:
        active_users.pop(uid, None)
    
    # Update active users gauge
    ACTIVE_USERS.set(len(active_users))

def monitor_endpoint(func):
    """Decorator to monitor specific endpoints with custom metrics"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = await func(*args, **kwargs)
            status_code = 200
            return result
        except Exception as e:
            status_code = getattr(e, 'status_code', 500)
            raise e
        finally:
            process_time = time.time() - start_time
            endpoint = func.__name__
            
            # Update metrics
            REQUEST_COUNT.labels(
                method=func.__name__.upper(),
                endpoint=endpoint,
                http_status=status_code
            ).inc()
            
            REQUEST_LATENCY.labels(
                method=func.__name__.upper(),
                endpoint=endpoint
            ).observe(process_time)
    
    return wrapper

def get_metrics() -> bytes:
    """Get Prometheus metrics"""
    # Update active users count before returning metrics
    ACTIVE_USERS.set(len(active_users))
    return generate_latest(REGISTRY)

def log_database_metrics():
    """Log database performance metrics"""
    # This would be implemented to query database-specific metrics
    # For example, for PostgreSQL:
    # - Number of connections
    # - Cache hit ratio
    # - Long-running queries
    # - Table sizes
    pass

# Schedule periodic tasks
if settings.ENABLE_MONITORING:
    import threading
    from datetime import datetime, timedelta
    
    def periodic_metrics():
        """Periodically collect and log metrics"""
        while True:
            try:
                log_database_metrics()
                # Update other metrics here
            except Exception as e:
                logger.error(f"Error collecting metrics: {str(e)}")
            
            # Run every 5 minutes
            time.sleep(300)
    
    # Start the metrics collection in a background thread
    metrics_thread = threading.Thread(target=periodic_metrics, daemon=True)
    metrics_thread.start()
