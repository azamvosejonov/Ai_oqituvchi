from typing import Any, List, Dict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud, models
from app.api import deps
from app.schemas.user import UserWithLessonCount
from app.schemas.role import Role as RoleSchema

router = APIRouter()


@router.get("/", response_model=Dict[str, Any])
def get_general_statistics(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get general platform statistics for authenticated users.
    """
    total_users = crud.user.get_count(db)
    total_lessons = crud.lesson.get_count(db)
    total_courses = crud.course.get_count(db)
    user_completed_lessons = crud.user_lesson_completion.get_completed_lessons_count_for_user(
        db, user_id=current_user.id
    )

    # Return basic statistics as dictionary
    return {
        "total_users": total_users,
        "total_lessons": total_lessons,
        "total_courses": total_courses,
        "user_completed_lessons": user_completed_lessons,
        "user_level": getattr(current_user, 'current_level', 'A1'),
        "user_is_premium": crud.user.is_premium(current_user)
    }


@router.get("/top-users", response_model=List[UserWithLessonCount])
def get_top_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 10,
    current_user: models.User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Get the top users by the number of completed lessons.
    (Admin only)
    """
    top_users_data = crud.user_lesson_completion.get_top_users_by_lesson_count(
        db, skip=skip, limit=limit
    )
    # Manually construct the response to match the Pydantic model
    result = [
        UserWithLessonCount(
            id=user.id,
            full_name=user.full_name,
            email=user.email,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            roles=[RoleSchema.model_validate(r, from_attributes=True) for r in user.roles],
            is_premium=crud.user.is_premium(user),
            lesson_count=count,
        )
        for user, count in top_users_data
    ]
    return result


@router.get("/payment-stats", response_model=Dict[str, Any])
def get_payment_stats(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Get payment statistics, such as total revenue and active subscriptions.
    (Admin only)
    """
    stats = crud.subscription.get_payment_statistics(db)
    return stats
