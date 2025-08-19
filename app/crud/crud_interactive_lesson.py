from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.models.lesson import InteractiveLesson, LessonSession, LessonInteraction
from app.schemas.interactive_lesson import (
    InteractiveLessonCreate,
    InteractiveLessonUpdate,
    LessonSessionCreate,
    LessonInteractionCreate,
)
from app.crud.base import CRUDBase


class CRUDInteractiveLesson(
    CRUDBase[InteractiveLesson, InteractiveLessonCreate, InteractiveLessonUpdate]
):
    pass


class CRUDLessonSession(CRUDBase[LessonSession, LessonSessionCreate, Dict[str, Any]]):
    """CRUD operations for LessonSession model"""

    def get_by_user(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[LessonSession]:
        return (
            db.query(self.model)
            .filter(self.model.user_id == user_id)
            .order_by(desc(self.model.start_time))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_active_session(
        self, db: Session, *, user_id: int
    ) -> Optional[LessonSession]:
        return (
            db.query(self.model)
            .filter(self.model.user_id == user_id, self.model.status == "in_progress")
            .order_by(desc(self.model.start_time))
            .first()
        )

    def end_session(
        self, db: Session, *, session_id: int, user_id: int
    ) -> Optional[LessonSession]:
        session = self.get(db, id=session_id)
        if not session or session.user_id != user_id:
            return None

        session.status = "completed"
        session.end_time = datetime.utcnow()
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    def create(self, db: Session, *, obj_in: Dict[str, Any] | LessonSessionCreate) -> LessonSession:
        """Create a LessonSession ensuring only valid model fields are persisted.

        Accepts either a dict with keys (user_id, lesson_id, status) or a LessonSessionCreate,
        but only persists fields available on the LessonSession model.
        """
        data = obj_in.dict(exclude_unset=True) if hasattr(obj_in, "dict") else dict(obj_in)
        valid = {k: data[k] for k in ["user_id", "lesson_id", "status"] if k in data}
        db_obj = self.model(**valid)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


class CRUDLessonInteraction(
    CRUDBase[LessonInteraction, LessonInteractionCreate, Dict[str, Any]]
):
    """CRUD operations for LessonInteraction model"""

    def get_by_session(
        self, db: Session, *, session_id: int, skip: int = 0, limit: int = 100
    ) -> List[LessonInteraction]:
        return (
            db.query(self.model)
            .filter(self.model.session_id == session_id)
            .order_by(desc(self.model.timestamp))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_last_interaction(
        self, db: Session, *, session_id: int
    ) -> Optional[LessonInteraction]:
        return (
            db.query(self.model)
            .filter(self.model.session_id == session_id)
            .order_by(desc(self.model.timestamp))
            .first()
        )

    def create(self, db: Session, *, obj_in: LessonInteractionCreate | Dict[str, Any]) -> LessonInteraction:
        """Create interaction mapping schema fields to model fields and ignoring extras like audio_url."""
        data = obj_in.dict(exclude_unset=True) if hasattr(obj_in, "dict") else dict(obj_in)
        mapped = {
            "session_id": data.get("session_id"),
            # prefer 'user_input' from schema; fallback to legacy 'user_message' key if present
            "user_input": data.get("user_input") or data.get("user_message"),
            "ai_response": data.get("ai_response"),
        }
        db_obj = self.model(**mapped)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


interactive_lesson = CRUDInteractiveLesson(InteractiveLesson)
interactive_lesson_session = CRUDLessonSession(LessonSession)
interactive_lesson_interaction = CRUDLessonInteraction(LessonInteraction)
