import enum

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean, func, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.db.base_class import Base

class LessonDifficulty(str, enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


class InteractiveLesson(Base):
    """Model for storing interactive lessons"""
    __tablename__ = "interactive_lessons"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(Text)
    video_url = Column(String, nullable=True)  # Optional URL for a lesson video
    content = Column(JSON, nullable=False)  # Could be JSON/Markdown for structured content
    order = Column(Integer, nullable=False)
    is_premium = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    estimated_duration = Column(Integer, nullable=True)  # Duration in minutes
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    avatar_id = Column(Integer, ForeignKey("ai_avatars.id"), nullable=False)
    difficulty = Column(SQLAlchemyEnum(LessonDifficulty), default=LessonDifficulty.MEDIUM, nullable=False)
    tags = Column(JSON, nullable=True)  # e.g., ["grammar", "pronunciation", "business"]

    # Relationships - using string-based references to avoid circular imports
    avatar = relationship("AIAvatar", back_populates="interactive_lessons")
    course = relationship("Course", back_populates="lessons")
    user_progress = relationship("UserLessonProgress", back_populates="lesson", cascade="all, delete-orphan", passive_deletes=True)
    sessions = relationship(
        "LessonSession",
        back_populates="lesson",
        primaryjoin="LessonSession.lesson_id == InteractiveLesson.id",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    exercises = relationship("Exercise", back_populates="lesson")
    homeworks = relationship("Homework", back_populates="lesson")
    completions = relationship(
        "UserLessonCompletion",
        back_populates="lesson",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    vocabulary = relationship("Word", back_populates="lesson")


class LessonSession(Base):
    """Model for tracking user's lesson sessions"""
    __tablename__ = "lesson_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    lesson_id = Column(Integer, ForeignKey("interactive_lessons.id", ondelete="CASCADE"), nullable=False)
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(50), default="in_progress")  # in_progress, completed, abandoned
    
    # Relationships - using string-based references to avoid circular imports
    user = relationship("User", back_populates="lesson_sessions")
    lesson = relationship("InteractiveLesson", back_populates="sessions", primaryjoin="LessonSession.lesson_id == InteractiveLesson.id")
    interactions = relationship("LessonInteraction", back_populates="session", cascade="all, delete-orphan")


class LessonInteraction(Base):
    """Model for storing user-AI interactions during a lesson"""
    __tablename__ = "lesson_interactions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("lesson_sessions.id"), nullable=False)
    user_input = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    session = relationship("LessonSession", back_populates="interactions")
