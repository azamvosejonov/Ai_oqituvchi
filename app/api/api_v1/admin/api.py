from fastapi import APIRouter

from app.api.api_v1.admin import (
    user_management, 
    course_management, 
    lesson_management, 
    exercise_management, 
    subscription_management, 
    feedback_management, 
    certificate_management,
    stats,
    content_management
)

api_router = APIRouter()
api_router.include_router(user_management.router, prefix="/users", tags=["admin-users"])
api_router.include_router(course_management.router, prefix="/courses", tags=["admin-courses"])
api_router.include_router(lesson_management.router, prefix="/lessons", tags=["admin-lessons"])
api_router.include_router(exercise_management.router, prefix="/exercises", tags=["admin-exercises"])
api_router.include_router(subscription_management.router, prefix="/subscriptions", tags=["admin-subscriptions"])
api_router.include_router(feedback_management.router, prefix="/feedback", tags=["admin-feedback"])
api_router.include_router(certificate_management.router, prefix="/certificates", tags=["admin-certificates"])
api_router.include_router(stats.router, prefix="/stats", tags=["admin-stats"])
api_router.include_router(content_management.router, prefix="/content", tags=["admin-content"])
