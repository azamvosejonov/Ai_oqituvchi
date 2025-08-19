from fastapi import APIRouter

# Create the main API router
api_router = APIRouter()

def include_api_routers():
    """
    Include all API routers from the endpoints module.
    This function is called after all modules are loaded to avoid circular imports.
    """
    from app.api.api_v1.endpoints import (
        users,
        courses,
        lessons,
        admin_users,
        admin_courses,
    )

    api_router.include_router(users.router, prefix="/users", tags=["users"])
    api_router.include_router(courses.router, prefix="/courses", tags=["courses"])
    api_router.include_router(lessons.router, prefix="/lessons", tags=["lessons"])
    api_router.include_router(admin_users.router, prefix="/admin/users", tags=["admin_users"])
    api_router.include_router(admin_courses.router, prefix="/admin/courses", tags=["admin_courses"])

    # The api_router is updated by the include_routers function
    return api_router

# Note: The include_api_routers() function should be called after all modules are loaded
# This is typically done in the main FastAPI application file (main.py or app/main.py)
