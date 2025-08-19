from fastapi import APIRouter

from app.api.api_v1.endpoints import (
    login,
    users, subscription_plans, words, subscriptions,
    statistics, user_progress, feedback, forum, ai, notifications, tests,
    admin, courses, lessons, certificates, content, profile, ai_sessions, pronunciation
)
from app.api.endpoints import (
    interactive_lessons, homework, lesson_interactions, lesson_sessions, payments, webrtc,
    metrics, avatars, recommendations, exercises
)

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(subscription_plans.router, prefix="/subscription-plans", tags=["subscription-plans"])
api_router.include_router(courses.router, prefix="/courses", tags=["courses"])
api_router.include_router(subscriptions.router, prefix="/subscriptions", tags=["subscriptions"])
# The following are now handled by the user-facing or centralized admin routers
api_router.include_router(lessons.router, prefix="/lessons", tags=["lessons"])
api_router.include_router(words.router, prefix="/words", tags=["words"])
api_router.include_router(statistics.router, prefix="/statistics", tags=["statistics"])
api_router.include_router(user_progress.router, prefix="/user-progress", tags=["user-progress"])
api_router.include_router(certificates.router, prefix="/certificates", tags=["certificates"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["feedback"])
api_router.include_router(forum.router, prefix="/forum", tags=["forum"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(ai_sessions.router, prefix="/ai-sessions", tags=["ai-sessions"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(tests.router, prefix="/tests", tags=["tests"])
api_router.include_router(tests.admin_router, prefix="/admin/tests", tags=["admin-tests"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(content.router, prefix="/content", tags=["content"])
api_router.include_router(profile.router, prefix="/profile", tags=["profile"])
api_router.include_router(pronunciation.router, prefix="/pronunciation", tags=["pronunciation"])

# Interactive lessons endpoints
api_router.include_router(interactive_lessons.router, prefix="/interactive-lessons", tags=["interactive-lessons"])
api_router.include_router(lesson_interactions.router, prefix="/lesson-interactions", tags=["lesson-interactions"])
api_router.include_router(lesson_sessions.router, prefix="/lesson-sessions", tags=["lesson-sessions"])
api_router.include_router(homework.router, prefix="/homework", tags=["homework"])
api_router.include_router(payments.router, prefix="/payments", tags=["payments"])

# WebRTC endpoints
api_router.include_router(webrtc.router, prefix="/webrtc", tags=["webrtc"])

# Avatars endpoint
api_router.include_router(avatars.router, prefix="/avatars", tags=["avatars"])

# Other endpoints
api_router.include_router(metrics.router, prefix="/metrics", tags=["metrics"])
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])
api_router.include_router(exercises.router, prefix="/exercises", tags=["exercises"])
