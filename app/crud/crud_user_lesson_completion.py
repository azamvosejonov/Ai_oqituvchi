from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Tuple, Optional

from app.crud.base import CRUDBase
from app.models import User
from app.models.user_lesson_progress import UserLessonCompletion
from app.schemas.user_lesson_completion import UserLessonCompletionCreate, UserLessonCompletionUpdate

class CRUDUserLessonCompletion(CRUDBase[UserLessonCompletion, UserLessonCompletionCreate, UserLessonCompletionUpdate]):
    def get_by_user(self, db: Session, *, user_id: int) -> List[UserLessonCompletion]:
        return db.query(self.model).filter(self.model.user_id == user_id).all()

    def get_by_user_and_lesson(self, db: Session, *, user_id: int, lesson_id: int) -> Optional[UserLessonCompletion]:
        return db.query(self.model).filter(self.model.user_id == user_id, self.model.lesson_id == lesson_id).first()

    def get_completed_lesson_ids(self, db: Session, *, user_id: int) -> List[int]:
        """Returns a list of lesson IDs completed by a specific user."""
        completed_lessons = db.query(self.model.lesson_id).filter(self.model.user_id == user_id).all()
        return [lesson_id for lesson_id, in completed_lessons]

    def get_completed_lessons_count_for_user(self, db: Session, *, user_id: int) -> int:
        """Returns the count of completed lessons for a specific user."""
        return db.query(self.model).filter(self.model.user_id == user_id).count()

    def get_top_users_by_lesson_count(self, db: Session, *, skip: int = 0, limit: int = 10) -> List[Tuple[User, int]]:
        """
        Get users who have completed the most lessons.
        Returns a list of tuples, where each tuple contains a User object and their completed lesson count.
        """
        return (
            db.query(User, func.count(UserLessonCompletion.id).label('lesson_count'))
            .join(UserLessonCompletion, User.id == UserLessonCompletion.user_id)
            .group_by(User.id)
            .order_by(func.count(UserLessonCompletion.id).desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

user_lesson_completion = CRUDUserLessonCompletion(UserLessonCompletion)
