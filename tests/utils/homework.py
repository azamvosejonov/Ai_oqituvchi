from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app import crud, schemas
from .utils import random_lower_string
from app.models import Homework


def create_random_homework(
    db: Session, *, lesson_id: int, course_id: int, teacher_id: int
) -> Homework:
    """
    Create a random homework assignment for testing.
    """
    title = random_lower_string()
    description = random_lower_string() * 3
    due_date = datetime.now() + timedelta(days=7)
    homework_in = schemas.HomeworkCreate(
        title=title,
        description=description,
        due_date=due_date,
        lesson_id=lesson_id,
        course_id=course_id,
        homework_type="written",
    )
    return crud.homework.create(db=db, obj_in=homework_in, created_by=teacher_id)
