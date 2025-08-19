from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import Response
from typing import Any

from app.core.config import settings
from app.core.monitoring import get_metrics
from app.core.security import get_current_active_user
from app.models.user import User

router = APIRouter()

@router.get("", response_class=Response, responses={
    200: {
        "content": {"text/plain": {}},
        "description": "Returns the metrics in Prometheus format",
    }
})
async def get_prometheus_metrics(
    request: Request,
    current_user: User = Depends(get_current_active_user)
) -> Response:
    """
    Expose Prometheus metrics for monitoring the application.
    
    This endpoint returns metrics in the Prometheus exposition format.
    Access is restricted to authenticated users with appropriate permissions.
    """
    if not settings.ENABLE_MONITORING:
        raise HTTPException(
            status_code=501,
            detail="Monitoring is not enabled on this server"
        )
    
    # Get metrics from the monitoring system
    metrics = get_metrics()
    
    return Response(
        content=metrics,
        media_type="text/plain; version=0.0.4; charset=utf-8"
    )

# Health check endpoint
@router.get("/health")
async def health_check() -> dict[str, str]:
    """
    Health check endpoint for monitoring services.
    Returns a simple status message indicating the service is running.
    """
    return {"status": "ok"}

# System status endpoint
@router.get("/status")
async def system_status(
    current_user: User = Depends(get_current_active_user)
) -> dict[str, Any]:
    """
    Get detailed system status information.
    Requires authentication.
    """
    import platform
    from datetime import datetime
    try:
        import psutil  # type: ignore
    except Exception:
        psutil = None  # Fallback when psutil not available
    
    # Get system information
    system_info = {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "system": {
            "os": {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor()
            },
            "python": {
                "version": platform.python_version(),
                "implementation": platform.python_implementation(),
                "compiler": platform.python_compiler()
            },
            "cpu": (
                {
                    "physical_cores": psutil.cpu_count(logical=False),
                    "total_cores": psutil.cpu_count(logical=True),
                    "usage_percent": psutil.cpu_percent(interval=1, percpu=True),
                }
                if psutil
                else {
                    "physical_cores": None,
                    "total_cores": None,
                    "usage_percent": [],
                }
            ),
            "memory": (
                {
                    "total": psutil.virtual_memory().total,
                    "available": psutil.virtual_memory().available,
                    "used": psutil.virtual_memory().used,
                    "percent": psutil.virtual_memory().percent,
                }
                if psutil
                else {
                    "total": None,
                    "available": None,
                    "used": None,
                    "percent": None,
                }
            ),
            "disk": (
                {
                    "total": psutil.disk_usage('/').total,
                    "used": psutil.disk_usage('/').used,
                    "free": psutil.disk_usage('/').free,
                    "percent": psutil.disk_usage('/').percent,
                }
                if psutil
                else {
                    "total": None,
                    "used": None,
                    "free": None,
                    "percent": None,
                }
            ),
        },
        "app": {
            "name": settings.PROJECT_NAME,
            "environment": settings.ENVIRONMENT if hasattr(settings, 'ENVIRONMENT') else 'development',
            "debug": settings.DEBUG if hasattr(settings, 'DEBUG') else False,
            "monitoring_enabled": settings.ENABLE_MONITORING
        }
    }
    
    return system_info
