from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from app.models import (
    PronunciationPhrase, PronunciationSession, PronunciationAttempt,
    PronunciationAnalysisResult, UserPronunciationProfile, User
)
from app.schemas.speech import PronunciationPhraseCreate, PronunciationSessionCreate

logger = logging.getLogger(__name__)

class CRUDPronunciationPhrase:
    """CRUD operations for PronunciationPhrase model"""
    
    def get(self, db: Session, id: int) -> Optional[PronunciationPhrase]:
        return db.query(PronunciationPhrase).get(id)
    
    def get_by_level(self, db: Session, level: str, skip: int = 0, limit: int = 10) -> List[PronunciationPhrase]:
        return (db.query(PronunciationPhrase)
                .filter(PronunciationPhrase.level == level)
                .offset(skip).limit(limit).all())
    
    def create(self, db: Session, obj_in: PronunciationPhraseCreate) -> PronunciationPhrase:
        try:
            data = obj_in.model_dump()
        except AttributeError:
            data = obj_in.dict()
        db_obj = PronunciationPhrase(**data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def list(
        self, db: Session, *, skip: int = 0, limit: int = 100, level: Optional[str] = None
    ) -> List[PronunciationPhrase]:
        q = db.query(PronunciationPhrase)
        if level:
            q = q.filter(PronunciationPhrase.level == level)
        return q.offset(skip).limit(limit).all()

    def update(self, db: Session, id: int, update_data: Dict[str, Any]) -> Optional[PronunciationPhrase]:
        obj = db.query(PronunciationPhrase).get(id)
        if not obj:
            return None
        for field in ["text", "level", "category"]:
            if field in update_data and update_data[field] is not None:
                setattr(obj, field, update_data[field])
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def remove(self, db: Session, id: int) -> bool:
        obj = db.query(PronunciationPhrase).get(id)
        if not obj:
            return False
        db.delete(obj)
        db.commit()
        return True

class CRUDPronunciationSession:
    """CRUD operations for PronunciationSession model"""
    
    def get(self, db: Session, id: int) -> Optional[PronunciationSession]:
        return db.query(PronunciationSession).get(id)
    
    def create(self, db: Session, obj_in: PronunciationSessionCreate) -> PronunciationSession:
        # Only accept columns that exist on the model and drop helper fields like 'phrases'
        try:
            data = obj_in.model_dump()
        except AttributeError:
            data = obj_in.dict()
        db_obj = PronunciationSession(
            user_id=data.get("user_id"),
            level=data.get("level"),
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def list_by_user(self, db: Session, user_id: int, *, skip: int = 0, limit: int = 100) -> List[PronunciationSession]:
        return (
            db.query(PronunciationSession)
            .filter(PronunciationSession.user_id == user_id)
            .order_by(PronunciationSession.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def mark_completed(self, db: Session, id: int) -> Optional[PronunciationSession]:
        obj = db.query(PronunciationSession).get(id)
        if not obj:
            return None
        obj.completed = True
        obj.completed_at = datetime.utcnow()
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

class CRUDPronunciationAttempt:
    """CRUD operations for PronunciationAttempt model"""
    
    def create(self, db: Session, obj_in: dict) -> PronunciationAttempt:
        db_obj = PronunciationAttempt(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

class CRUDUserPronunciationProfile:
    """CRUD operations for UserPronunciationProfile model"""
    
    def get_by_user(self, db: Session, user_id: int) -> Optional[UserPronunciationProfile]:
        return (db.query(UserPronunciationProfile)
                .filter(UserPronunciationProfile.user_id == user_id)
                .first())
    
    def create(self, db: Session, user_id: int) -> UserPronunciationProfile:
        db_obj = UserPronunciationProfile(user_id=user_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_or_create(self, db: Session, user_id: int) -> UserPronunciationProfile:
        profile = self.get_by_user(db, user_id)
        if profile:
            return profile
        return self.create(db, user_id)

    def update_on_attempt(self, db: Session, user_id: int, level: Optional[str], score: Optional[float]) -> UserPronunciationProfile:
        profile = self.get_or_create(db, user_id)
        profile.total_attempts = (profile.total_attempts or 0) + 1
        profile.last_practice = datetime.utcnow()
        if score is not None:
            # overall average
            prev_total = max((profile.total_attempts or 1) - 1, 0)
            if prev_total > 0:
                profile.overall_score = ((profile.overall_score or 0) * prev_total + score) / (prev_total + 1)
            else:
                profile.overall_score = score
            # level-specific
            if level == "beginner":
                profile.beginner_score = score if not profile.beginner_score else (profile.beginner_score * 0.8 + score * 0.2)
            elif level == "intermediate":
                profile.intermediate_score = score if not profile.intermediate_score else (profile.intermediate_score * 0.8 + score * 0.2)
            elif level == "advanced":
                profile.advanced_score = score if not profile.advanced_score else (profile.advanced_score * 0.8 + score * 0.2)
        db.add(profile)
        db.commit()
        db.refresh(profile)
        return profile

# Initialize CRUD instances
crud_pronunciation_phrase = CRUDPronunciationPhrase()
crud_pronunciation_session = CRUDPronunciationSession()
crud_pronunciation_attempt = CRUDPronunciationAttempt()
crud_user_pronunciation_profile = CRUDUserPronunciationProfile()
