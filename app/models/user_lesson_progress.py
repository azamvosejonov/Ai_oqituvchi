"""
UserLessonProgress model for tracking user progress on lessons.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class UserLessonProgress(Base):
    """Model for tracking user progress on individual lessons."""
    __tablename__ = "user_lesson_progress"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    lesson_id = Column(Integer, ForeignKey("interactive_lessons.id", ondelete="CASCADE"), nullable=False)
    
    # Progress information
    is_completed = Column(Boolean, default=False, nullable=False)
    score = Column(Float, default=0.0, nullable=False)  # Score for the lesson (0-100)
    time_spent = Column(Integer, default=0, nullable=False)  # Time spent in seconds
    last_accessed = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="lesson_progress", foreign_keys=lambda: [UserLessonProgress.user_id])
    lesson = relationship("app.models.lesson.InteractiveLesson", back_populates="user_progress")


class UserLessonCompletion(Base):
    __tablename__ = "user_lesson_completions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    lesson_id = Column(Integer, ForeignKey("interactive_lessons.id", ondelete="CASCADE"), nullable=False)
    completed_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="lesson_completions")
    lesson = relationship("app.models.lesson.InteractiveLesson", back_populates="completions")
