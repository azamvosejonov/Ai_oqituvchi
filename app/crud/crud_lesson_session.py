from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from app.crud.base import CRUDBase
from app.models import LessonSession
from app.schemas.lesson_session import LessonSessionCreate, LessonSessionUpdate


class CRUDLessonSession(CRUDBase[LessonSession, LessonSessionCreate, LessonSessionUpdate]):
    def get_multi_by_user(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[LessonSession]:
        return (
            db.query(self.model)
            .filter(LessonSession.user_id == user_id)
            .order_by(LessonSession.start_time.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_active_session(
        self, db: Session, *, user_id: int, lesson_id: int
    ) -> Optional[LessonSession]:
        return (
            db.query(self.model)
            .filter(
                LessonSession.user_id == user_id,
                LessonSession.lesson_id == lesson_id,
                LessonSession.status == "in_progress"
            )
            .order_by(LessonSession.start_time.desc())
            .first()
        )
    
    def complete_session(
        self, db: Session, *, db_obj: LessonSession
    ) -> LessonSession:
        db_obj.status = "completed"
        db_obj.end_time = func.now()
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


lesson_session = CRUDLessonSession(LessonSession)
