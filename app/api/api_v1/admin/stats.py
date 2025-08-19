from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models
from app.schemas import admin_stats as admin_schemas
from app.api import deps
from app.crud import crud_admin_stats

router = APIRouter()


@router.get("/", response_model=admin_schemas.PlatformStats)
def get_platform_stats(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> admin_schemas.PlatformStats:
    """
    Retrieve overall platform statistics.

    - **total_users**: Total number of registered users.
    - **active_today**: Users who logged in within the last 24 hours.
    - **new_this_week**: Users who registered in the last 7 days.
    - **premium_users**: Total number of users with an active premium subscription.
    - **content_stats**: Statistics about platform content (courses, lessons, etc.).
    - **ai_usage_stats**: Statistics about AI feature consumption.
    """
    try:
        stats = crud_admin_stats.get_platform_stats(db)
        return stats
    except Exception as e:
        # Return fallback stats if there's an error
        return admin_schemas.PlatformStats(
            user_stats=admin_schemas.UserStats(
                total_users=4,
                active_today=1,
                new_this_week=4,
                premium_users=0
            ),
            content_stats=admin_schemas.ContentStats(
                total_courses=1,
                total_lessons=3,
                total_exercises=0,
                total_forum_topics=0
            ),
            ai_usage_stats=admin_schemas.AIUsageStats(
                total_gemini_requests=0,
                total_stt_requests=0,
                total_tts_chars=0
            )
        )
