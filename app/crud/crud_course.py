from typing import List, Optional

from sqlalchemy.orm import Session, joinedload

from app.crud.base import CRUDBase
from app.models.course import Course, Enrollment
from app.models.user_lesson_progress import UserLessonCompletion
from app.models.lesson import InteractiveLesson
from app.schemas.course import CourseCreate, CourseUpdate

import logging
logging.basicConfig(level=logging.INFO)

class CRUDCourse(CRUDBase[Course, CourseCreate, CourseUpdate]):
    def get_by_title(self, db: Session, *, title: str) -> Optional[Course]:
        return db.query(self.model).filter(self.model.title == title).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Course]:
        return (
            db.query(self.model)
            .options(joinedload(self.model.lessons))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_count(self, db: Session) -> int:
        return db.query(self.model).count()

    def create_with_instructor(self, db: Session, *, obj_in: CourseCreate, instructor_id: Optional[int] = None) -> Course:
        # Support explicit instructor_id passed by callers/tests.
        if instructor_id is not None:
            try:
                # Pydantic v2 models are immutable by default unless configured. Use model_copy/update.
                obj_in = obj_in.model_copy(update={"instructor_id": instructor_id})
            except Exception:
                # Fallback for plain dict-like or older schemas
                if hasattr(obj_in, "instructor_id"):
                    setattr(obj_in, "instructor_id", instructor_id)
        return super().create(db, obj_in=obj_in)

    def get_multi_by_instructor(
        self, db: Session, *, instructor_id: int, skip: int = 0, limit: int = 100
    ) -> List[Course]:
        return (
            db.query(self.model)
            .filter(Course.instructor_id == instructor_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def is_course_completed(self, db: Session, *, user_id: int, course_id: int) -> bool:
        """
        Check if a user has completed all lessons in a specific course.
        """
        # Get all lesson IDs for the course
        course_lessons_query = db.query(InteractiveLesson.id).filter(InteractiveLesson.course_id == course_id)
        course_lesson_ids = {row[0] for row in course_lessons_query.all()}

        if not course_lesson_ids:
            # An empty course cannot be completed
            return False

        # Get all completed lesson IDs for the user that are part of this course
        completed_lessons_query = db.query(UserLessonCompletion.lesson_id).filter(
            UserLessonCompletion.user_id == user_id,
            UserLessonCompletion.lesson_id.in_(course_lesson_ids)
        )
        completed_lesson_ids = {row[0] for row in completed_lessons_query.all()}

        # Check if the set of completed lessons is equal to the set of all course lessons
        return course_lesson_ids == completed_lesson_ids


course = CRUDCourse(Course)
