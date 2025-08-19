from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app import crud, models, schemas
from tests.test_pronunciation import random_lower_string


def create_test_pronunciation_phrase(
    db: Session, 
    text: Optional[str] = None,
    level: str = "beginner",
    category: str = "test"
) -> models.PronunciationPhrase:
    """Create a test pronunciation phrase"""
    if text is None:
        text = f"Test phrase {random_lower_string()}"
    
    phrase_in = schemas.PronunciationPhraseCreate(
        text=text,
        level=level,
        category=category
    )
    
    return crud.crud_pronunciation_phrase.create(db, obj_in=phrase_in)


def create_test_pronunciation_session(
    db: Session, 
    user_id: int = 1,
    level: str = "beginner",
    phrases: Optional[list[int]] = None,
    completed: bool = False
) -> models.PronunciationSession:
    """Create a test pronunciation session"""
    if phrases is None:
        phrases = []
        for _ in range(3):
            phrase = create_test_pronunciation_phrase(db)
            phrases.append(phrase.id)
    
    session_in = schemas.PronunciationSessionCreate(
        user_id=user_id,
        level=level,
        phrases=phrases
    )
    
    session = crud.crud_pronunciation_session.create(db, obj_in=session_in)
    
    if completed:
        session.completed = True
        session.completed_at = datetime.now(timezone.utc)
        db.add(session)
        db.commit()
        db.refresh(session)
    
    return session


def create_test_pronunciation_attempt(
    db: Session,
    user_id: int = 1,
    session_id: Optional[int] = None,
    phrase_id: Optional[int] = None,
    score: Optional[float] = 85.5,
    feedback: Optional[str] = None
) -> models.PronunciationAttempt:
    """Create a test pronunciation attempt"""
    if phrase_id is None:
        phrase = create_test_pronunciation_phrase(db)
        phrase_id = phrase.id
    
    if feedback is None:
        feedback = f"Test feedback {random_lower_string()}"
    
    attempt_data = {
        "user_id": user_id,
        "session_id": session_id,
        "phrase_id": phrase_id,
        "recognized_text": "test recognized text",
        "expected_text": "test expected text",
        "score": score,
        "feedback": feedback,
        "analysis_data": {
            "word_level": {"test": 0.8},
            "phoneme_level": {"t": 0.9, "e": 0.8, "s": 0.7, "t": 0.9}
        }
    }
    
    return crud.crud_pronunciation_attempt.create(db, obj_in=attempt_data)


def create_test_user_pronunciation_profile(
    db: Session,
    user_id: int = 1,
    overall_score: float = 75.0,
    total_attempts: int = 5,
    common_errors: Optional[dict] = None
) -> models.UserPronunciationProfile:
    """Create a test user pronunciation profile"""
    if common_errors is None:
        common_errors = {
            "vowel_length": 3,
            "stress_placement": 2,
            "consonant_clusters": 1
        }
    
    profile = crud.crud_user_pronunciation_profile.get_by_user(db, user_id=user_id)
    
    if profile is None:
        profile = models.UserPronunciationProfile(
            user_id=user_id,
            overall_score=overall_score,
            total_attempts=total_attempts,
            common_errors=common_errors,
            beginner_score=70.0,
            intermediate_score=75.0,
            advanced_score=80.0,
            last_practice=datetime.now(timezone.utc)
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
    
    return profile
