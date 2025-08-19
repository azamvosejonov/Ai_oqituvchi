from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Any
from datetime import datetime, timedelta
import io

from app import models, schemas, crud
from app.api import deps
from app.services import ai_service
from app.core.config import settings

router = APIRouter()

@router.get("/ai/usage", response_model=List[schemas.UserAIUsage])
async def get_ai_usage_stats(
    start_date: Optional[datetime] = Query(None, description="Start date for filtering"),
    end_date: Optional[datetime] = Query(None, description="End date for filtering"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser)
):
    """Get AI usage statistics for admin"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    query = db.query(models.UserAIUsage)
    
    if start_date:
        query = query.filter(models.UserAIUsage.timestamp >= start_date)
    if end_date:
        query = query.filter(models.UserAIUsage.timestamp <= end_date)
    if user_id:
        query = query.filter(models.UserAIUsage.user_id == user_id)
    
    return query.order_by(models.UserAIUsage.timestamp.desc()).all()

@router.get("/ai/models", response_model=List[dict])
async def get_available_ai_models(
    current_user: models.User = Depends(deps.get_current_active_superuser)
):
    """Get list of available AI models"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return [
        {"id": "gpt-4o", "name": "GPT-4o", "max_tokens": 128000, "supports_vision": True},
        {"id": "gemini-2.0-flash", "name": "Gemini 2.0 Flash", "max_tokens": 1000000, "supports_vision": True},
        {"id": "claude-3-opus", "name": "Claude 3 Opus", "max_tokens": 200000, "supports_vision": True},
    ]

@router.post("/ai/update-model-usage", response_model=dict)
async def update_ai_model_usage(
    model_id: str = Query(..., description="AI model ID"),
    enabled: bool = Query(True, description="Whether to enable or disable the model"),
    current_user: models.User = Depends(deps.get_current_active_superuser)
):
    """Enable/disable AI model usage"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # In a real implementation, you would update this in a database or config
    return {
        "status": "success",
        "model_id": model_id,
        "enabled": enabled,
        "message": f"Model {model_id} has been {'enabled' if enabled else 'disabled'}"
    }
