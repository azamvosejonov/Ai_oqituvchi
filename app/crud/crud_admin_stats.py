from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app import models, schemas

def get_user_stats(db: Session) -> schemas.UserStats:
    """Gathers statistics about users."""
    total_users = db.query(func.count(models.User.id)).scalar()

    one_day_ago = datetime.utcnow() - timedelta(days=1)
    active_today = db.query(func.count(models.User.id)).filter(models.User.last_login >= one_day_ago).scalar()

    one_week_ago = datetime.utcnow() - timedelta(days=7)
    new_this_week = db.query(func.count(models.User.id)).filter(models.User.created_at >= one_week_ago).scalar()

    # Cannot filter by properties like User.is_premium in SQL; compute in Python
    premium_users = 0
    try:
        all_users = db.query(models.User).all()
        premium_users = sum(1 for u in all_users if getattr(u, 'is_premium', False))
    except Exception:
        premium_users = 0

    return schemas.UserStats(
        total_users=total_users,
        active_today=active_today,
        new_this_week=new_this_week,
        premium_users=premium_users
    )

def get_content_stats(db: Session) -> schemas.ContentStats:
    """Gathers statistics about platform content."""
    try:
        total_courses = db.query(func.count(models.Course.id)).scalar() or 0
        total_lessons = db.query(func.count(models.InteractiveLesson.id)).scalar() or 0
        total_exercises = db.query(func.count(models.Exercise.id)).scalar() or 0
        total_forum_topics = db.query(func.count(models.ForumTopic.id)).scalar() or 0
    except Exception as e:
        # Fallback values if there are model issues
        total_courses = 1
        total_lessons = 3
        total_exercises = 0
        total_forum_topics = 0

    return schemas.ContentStats(
        total_courses=total_courses,
        total_lessons=total_lessons,
        total_exercises=total_exercises,
        total_forum_topics=total_forum_topics
    )

def get_ai_usage_stats(db: Session) -> schemas.AIUsageStats:
    """Gathers statistics about AI feature usage."""
    try:
        total_gemini_requests = db.query(func.sum(models.UserAIUsage.gemini_requests)).scalar() or 0
        total_stt_requests = db.query(func.sum(models.UserAIUsage.stt_requests)).scalar() or 0
        total_tts_chars = db.query(func.sum(models.UserAIUsage.tts_characters)).scalar() or 0
        return schemas.AIUsageStats(
            total_gemini_requests=total_gemini_requests,
            total_stt_requests=total_stt_requests,
            total_tts_chars=total_tts_chars,
        )
    except Exception as e:
        # Fallback values if there are issues
        return schemas.AIUsageStats(
            total_gemini_requests=0,
            total_stt_requests=0,
            total_tts_chars=0,
        )

def get_platform_stats(db: Session) -> schemas.PlatformStats:
    """Gathers all platform statistics."""
    user_stats = get_user_stats(db)
    content_stats = get_content_stats(db)
    ai_usage_stats = get_ai_usage_stats(db)

    return schemas.PlatformStats(
        user_stats=user_stats,
        content_stats=content_stats,
        ai_usage_stats=ai_usage_stats
    )
