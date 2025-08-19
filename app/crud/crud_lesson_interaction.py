from sqlalchemy.orm import Session
from typing import List, Optional

from app.crud.base import CRUDBase
from app.models import LessonInteraction
from app.schemas.lesson_interaction import LessonInteractionCreate, LessonInteractionUpdate


class CRUDLessonInteraction(CRUDBase[LessonInteraction, LessonInteractionCreate, LessonInteractionUpdate]):
    def get_multi_by_session(
        self, db: Session, *, session_id: int, skip: int = 0, limit: int = 100
    ) -> List[LessonInteraction]:
        return (
            db.query(self.model)
            .filter(LessonInteraction.session_id == session_id)
            .order_by(LessonInteraction.timestamp.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def create_with_session(
        self, db: Session, *, obj_in: LessonInteractionCreate, session_id: int
    ) -> LessonInteraction:
        db_obj = LessonInteraction(
            **obj_in.dict(),
            session_id=session_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


lesson_interaction = CRUDLessonInteraction(LessonInteraction)
