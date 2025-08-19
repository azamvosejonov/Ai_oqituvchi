from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime

from app import models, schemas
from app.schemas.payment_verification import PaymentVerificationStatus


def get_dashboard_stats(db: Session) -> schemas.DashboardStats:
    # Basic counts
    total_users = db.query(func.count(models.User.id)).scalar()
    total_courses = db.query(func.count(models.Course.id)).scalar()
    total_lessons = db.query(func.count(models.InteractiveLesson.id)).scalar()
    total_words = db.query(func.count(models.Word.id)).scalar()

    # Correctly count premium users by checking for active subscriptions
    premium_users = db.query(func.count(models.User.id)).join(models.User.subscriptions).filter(
        models.Subscription.is_active == True,
        models.Subscription.end_date >= func.now()
    ).distinct().scalar()

    # Subscription and Revenue stats
    active_subscriptions = (
        db.query(func.count(models.Subscription.id))
        .filter(models.Subscription.is_active == True, models.Subscription.end_date >= func.now())
        .scalar()
    )
    
    total_revenue_query = db.query(func.sum(models.Subscription.amount_paid)).filter(
        models.Subscription.is_active == True
    )
    total_revenue = total_revenue_query.scalar() or 0.0

    # AI Usage stats (map to schema fields)
    gemini_requests = db.query(func.sum(models.UserAIUsage.gemini_requests)).scalar() or 0
    stt_requests = db.query(func.sum(models.UserAIUsage.stt_requests)).scalar() or 0
    tts_characters = db.query(func.sum(models.UserAIUsage.tts_characters)).scalar() or 0

    # Payment stats
    pending_payments = db.query(models.PaymentVerification).filter(
        models.PaymentVerification.status == PaymentVerificationStatus.PENDING
    ).count()

    # Top learners
    top_learners_query = (
        db.query(
            models.User.full_name,
            func.count(models.UserLessonCompletion.id).label('completed_lessons')
        )
        .join(models.UserLessonCompletion, models.User.id == models.UserLessonCompletion.user_id)
        .group_by(models.User.id)
        .order_by(desc('completed_lessons'))
        .limit(5)
        .all()
    )
    
    top_learners = [{
        "full_name": name, "completed_lessons": count
    } for name, count in top_learners_query]

    # Top 5 Popular Courses (by user enrollment/subscription - assuming via lesson completion)
    # This is a simplified proxy. A direct enrollment table would be better.
    top_courses_query = (
        db.query(
            models.Course.title,
            func.count(models.User.id).label('enrolled_users')
        )
        .join(models.InteractiveLesson, models.Course.id == models.InteractiveLesson.course_id)
        .join(models.UserLessonCompletion, models.InteractiveLesson.id == models.UserLessonCompletion.lesson_id)
        .join(models.User, models.User.id == models.UserLessonCompletion.user_id)
        .group_by(models.Course.id)
        .order_by(desc('enrolled_users'))
        .limit(5)
        .all()
    )
    top_courses = [{
        "title": title, "enrolled_users": count
    } for title, count in top_courses_query]

    return schemas.DashboardStats(
        total_users=total_users,
        premium_users=premium_users,
        total_courses=total_courses,
        total_lessons=total_lessons,
        total_words=total_words,
        active_subscriptions=active_subscriptions,
        total_revenue=total_revenue,
        ai_usage_stats={
            # Our schema expects these names:
            # - tts_chars_used: use total tts characters
            # - stt_seconds_used: if we only have requests count, use that as a proxy
            # - chat_tokens_used: not tracked; approximate with gemini_requests for now (0 if none)
            "tts_chars_used": tts_characters,
            "stt_seconds_used": stt_requests,
            "chat_tokens_used": gemini_requests,
        },
        pending_payments=pending_payments,
        top_learners=top_learners,
        top_courses=top_courses,
    )
