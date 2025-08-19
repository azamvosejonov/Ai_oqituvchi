from sqlalchemy.orm import Session
from typing import List

from app.crud.base import CRUDBase
from app.models import Feedback
from app.schemas import FeedbackCreate, FeedbackUpdate

class CRUDFeedback(CRUDBase[Feedback, FeedbackCreate, FeedbackUpdate]):
    def create_with_owner(
        self, db: Session, *, obj_in: FeedbackCreate, user_id: int
    ) -> Feedback:
        db_obj = self.model(**obj_in.model_dump(), user_id=user_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_user(self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100) -> List[Feedback]:
        return db.query(self.model).filter(Feedback.user_id == user_id).offset(skip).limit(limit).all()

    def remove(self, db: Session, *, id: int) -> Feedback:
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj


feedback = CRUDFeedback(Feedback)
