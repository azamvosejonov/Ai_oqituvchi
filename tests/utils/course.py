from sqlalchemy.orm import Session

from app import crud
from app.models.course import Course
from app.schemas.course import CourseCreate


def create_test_course(db: Session, instructor_id: int) -> Course:
    """Create a test course."""
    course_in = CourseCreate(
        title="Test Course",
        description="A course for testing purposes",
        difficulty_level="beginner",
        instructor_id=instructor_id  # Ensure instructor_id is passed
    )
    return crud.course.create_with_instructor(db=db, obj_in=course_in, instructor_id=instructor_id)


def create_random_course(db: Session, instructor_id: int) -> Course:
    """Backward-compatible alias expected by some tests."""
    return create_test_course(db, instructor_id=instructor_id)
