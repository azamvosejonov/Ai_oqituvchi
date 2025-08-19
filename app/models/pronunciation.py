from sqlalchemy import Column, Integer, String, ForeignKey, Float, Text, DateTime, Boolean, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class PronunciationPhrase(Base):
    """Model for storing pronunciation practice phrases"""
    __tablename__ = "pronunciation_phrases"
    
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False, index=True)
    level = Column(String, nullable=False, index=True)  # beginner, intermediate, advanced
    category = Column(String, index=True)  # e.g., greetings, numbers, common_phrases
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    attempts = relationship("PronunciationAttempt", back_populates="phrase")


class PronunciationSession(Base):
    """Model for tracking pronunciation practice sessions"""
    __tablename__ = "pronunciation_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    level = Column(String, nullable=False, index=True)
    completed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="pronunciation_practice_sessions", foreign_keys=lambda: [PronunciationSession.user_id])
    attempts = relationship("PronunciationAttempt", back_populates="session")


class PronunciationAttempt(Base):
    """Model for storing individual pronunciation attempts"""
    __tablename__ = "pronunciation_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("pronunciation_sessions.id"), nullable=True)
    phrase_id = Column(Integer, ForeignKey("pronunciation_phrases.id"), nullable=False)
    audio_file_path = Column(String, nullable=True)
    recognized_text = Column(String, nullable=True)
    expected_text = Column(String, nullable=False)
    score = Column(Float, nullable=True)  # 0-100 score
    feedback = Column(Text, nullable=True)
    analysis_data = Column(JSON, nullable=True)  # Detailed analysis results
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="pronunciation_practice_attempts", foreign_keys=lambda: [PronunciationAttempt.user_id])
    session = relationship("PronunciationSession", back_populates="attempts")
    phrase = relationship("PronunciationPhrase", back_populates="attempts")
    analysis_results = relationship(
        "PronunciationAnalysisResult",
        back_populates="attempt",
        cascade="all, delete-orphan"
    )


class PronunciationAnalysisResult(Base):
    """Model for storing detailed pronunciation analysis results"""
    __tablename__ = "pronunciation_analysis_results"
    
    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey("pronunciation_attempts.id"), nullable=False)
    word_level_analysis = Column(JSON, nullable=True)  # Per-word analysis
    phoneme_analysis = Column(JSON, nullable=True)  # Phoneme-level analysis
    prosody_analysis = Column(JSON, nullable=True)  # Stress, intonation, rhythm
    error_patterns = Column(JSON, nullable=True)  # Common error patterns
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    attempt = relationship("PronunciationAttempt", back_populates="analysis_results")


class UserPronunciationProfile(Base):
    """Model for storing user-specific pronunciation profile and progress"""
    __tablename__ = "user_pronunciation_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    overall_score = Column(Float, default=0.0)  # Overall pronunciation score (0-100)
    total_attempts = Column(Integer, default=0)
    last_practice = Column(DateTime(timezone=True), nullable=True)
    
    # Common error patterns (JSON structure)
    common_errors = Column(JSON, default=dict)
    
    # Progress by difficulty level
    beginner_score = Column(Float, default=0.0)
    intermediate_score = Column(Float, default=0.0)
    advanced_score = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="pronunciation_profile", foreign_keys=lambda: [UserPronunciationProfile.user_id])
