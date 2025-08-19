from fastapi import APIRouter

# Import endpoints
from app.api.endpoints import utils, course, ai_assistant, recommendations, homework, payment_verification, ai_conversation, subscription
from app.api.admin import courses as admin_courses

# Create the API router
api_router = APIRouter()

def include_routers():
    """
    Include all API routers to avoid circular imports.
    This function is called after all modules are loaded.
    """
    # Include all routers
    # api_router.include_router(login.router, tags=["login"])
    # api_router.include_router(users.router, prefix="/users", tags=["users"]) # This seems to be from v1, disabling for now
    api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
    api_router.include_router(subscription.router, prefix="/subscriptions", tags=["subscriptions"])
    api_router.include_router(course.router, prefix="/courses", tags=["courses"])
    # api_router.include_router(lessons.router, prefix="/lessons", tags=["lessons"]) # This seems to be from v1, disabling for now
    # api_router.include_router(words.router, prefix="/words", tags=["words"]) # This seems to be from v1, disabling for now
    # api_router.include_router(user_progress.router, prefix="/user-progress", tags=["user-progress"]) # This seems to be from v1, disabling for now
    # api_router.include_router(forum.router, prefix="/forum", tags=["forum"]) # This seems to be from v1, disabling for now
    # api_router.include_router(admin.router, prefix="/admin", tags=["admin"]) # This seems to be from v1, disabling for now
    # api_router.include_router(ielts.router, prefix="/ielts", tags=["ielts"]) # This seems to be from v1, disabling for now
    api_router.include_router(homework.router, prefix="/homework", tags=["homework"])
    # api_router.include_router(exercises.router, prefix="/exercises", tags=["exercises"]) # This seems to be from v1, disabling for now
    # api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"]) # This seems to be from v1, disabling for now
    api_router.include_router(payment_verification.router, prefix="/payment-verifications", tags=["payment-verifications"])
    api_router.include_router(ai_conversation.router, prefix="/ai", tags=["ai"])
    
    # Recommendations
    api_router.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])
    api_router.include_router(ai_assistant.router, prefix="/ai", tags=["ai-assistant"])

    # Admin routers
    api_router.include_router(admin_courses.router, prefix="/admin/courses", tags=["admin-courses"])
