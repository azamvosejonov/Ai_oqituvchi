from typing import List
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.models.user import User
from app.models.user_level import UserLevel
from app.schemas import Lesson


def get_recommended_lessons(db: Session, user: User, limit: int = 10) -> List[Lesson]:
    """
    Recommends lessons to a user based on their current level and completion history.

    Args:
        db: The database session.
        user: The user for whom to recommend lessons.
        limit: The maximum number of lessons to recommend.

    Returns:
        A list of recommended lesson objects.
    """
    current_user_level: UserLevel = user.get_current_level()

    # Get IDs of lessons the user has already completed
    completed_lesson_ids = crud.user_lesson_completion.get_completed_lesson_ids(db, user_id=user.id)

    # Find courses that match the user's level
    # Note: We assume course.difficulty_level string matches UserLevel enum values
    courses = db.query(models.Course).filter(models.Course.difficulty_level == current_user_level.value).all()

    recommended_lessons = []
    for course in courses:
        for lesson in course.lessons:
            if lesson.id not in completed_lesson_ids and lesson.is_active:
                recommended_lessons.append(lesson)
            if len(recommended_lessons) >= limit:
                break
        if len(recommended_lessons) >= limit:
            break

    # If no lessons found at the current level, maybe suggest from a lower level or any level?
    # For now, we just return what we have.
    return recommended_lessons
