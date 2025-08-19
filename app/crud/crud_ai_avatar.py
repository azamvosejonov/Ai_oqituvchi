from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.ai_avatar import AIAvatar
from app.models.lesson import InteractiveLesson
from app.schemas.ai_avatar import (
    AIAvatarCreate, AIAvatarUpdate,
)
from app.schemas.interactive_lesson import (
    InteractiveLessonCreate, InteractiveLessonUpdate
)
from app.crud.base import CRUDBase

class CRUDAvatar(CRUDBase[AIAvatar, AIAvatarCreate, AIAvatarUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[AIAvatar]:
        return db.query(self.model).filter(self.model.name == name).first()

    def get_by_voice_id(self, db: Session, voice_id: str) -> Optional[AIAvatar]:
        return db.query(self.model).filter(self.model.voice_id == voice_id).first()
    
    def get_active_avatars(self, db: Session) -> List[AIAvatar]:
        return db.query(self.model).filter(self.model.is_active == True).all()

class CRUDInteractiveLesson(CRUDBase[InteractiveLesson, InteractiveLessonCreate, InteractiveLessonUpdate]):
    def get_multi_by_avatar(
        self, db: Session, *, avatar_id: int, skip: int = 0, limit: int = 100
    ) -> List[InteractiveLesson]:
        return (
            db.query(self.model)
            .filter(self.model.avatar_id == avatar_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_active_lessons(
        self, db: Session, *, skip: int = 0, limit: int = 100, difficulty: str = None
    ) -> List[InteractiveLesson]:
        query = db.query(self.model).filter(self.model.is_active == True)
        if difficulty:
            query = query.filter(self.model.difficulty == difficulty)
        return query.offset(skip).limit(limit).all()
    
    def start_lesson_session(
        self, db: Session, lesson_id: int, user_id: int
    ) -> Dict[str, Any]:
        """Start a new interactive lesson session"""
        lesson = self.get(db, lesson_id)
        if not lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lesson not found"
            )
        
        # In a real app, you would create a session record in the database
        session_data = {
            "lesson_id": lesson_id,
            "user_id": user_id,
            "current_step": 0,
            "progress": 0.0,
            "started_at": db.func.now(),
            "metadata": {}
        }
        
        # Get the first message from the lesson content
        first_step = lesson.content.get("steps", [{}])[0] if lesson.content.get("steps") else {}
        
        return {
            "session": session_data,
            "lesson": lesson,
            "current_step": first_step
        }

ai_avatar = CRUDAvatar(AIAvatar)
interactive_lesson = CRUDInteractiveLesson(InteractiveLesson)
