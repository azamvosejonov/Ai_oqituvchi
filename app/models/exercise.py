from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum, JSON, DateTime, Boolean, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base
import enum

class ExerciseType(str, enum.Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    FILL_IN_BLANK = "fill_in_blank"
    MATCHING = "matching"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"
    ESSAY = "essay"
    LISTENING = "listening"
    SPEAKING = "speaking"
    TRANSLATION = "translation"
    DICTATION = "dictation"

class DifficultyLevel(str, enum.Enum):
    BEGINNER = "beginner"
    ELEMENTARY = "elementary"
    PRE_INTERMEDIATE = "pre_intermediate"
    INTERMEDIATE = "intermediate"
    UPPER_INTERMEDIATE = "upper_intermediate"
    ADVANCED = "advanced"
    PROFICIENCY = "proficiency"

class Exercise(Base):
    """Model for storing exercise questions."""
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    exercise_type = Column(Enum(ExerciseType), nullable=False)
    difficulty = Column(Enum(DifficultyLevel), nullable=False)
    correct_answer = Column(JSON, nullable=False)  # Can be string, array, or object
    explanation = Column(Text, nullable=True)
    options = Column(JSON, nullable=True)  # For multiple choice, matching, etc.
    tags = Column(JSON, nullable=True)  # Grammar points, topics, etc.
    lesson_id = Column(Integer, ForeignKey("interactive_lessons.id"), nullable=True)
    audio_url = Column(String(512), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    metadata_ = Column("metadata", JSON, nullable=True)  # Additional metadata

    # Relationships
    lesson = relationship("app.models.lesson.InteractiveLesson", back_populates="exercises")
    attempts = relationship("ExerciseAttempt", back_populates="exercise")

class ExerciseAttempt(Base):
    """Model for tracking user attempts at exercises."""
    __tablename__ = "exercise_attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    user_answer = Column(JSON, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    score = Column(Float, nullable=False)  # 0.0 to 1.0
    feedback = Column(JSON, nullable=True)  # Detailed feedback
    time_spent = Column(Integer, nullable=True)  # Time spent in seconds
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="exercise_attempts")
    exercise = relationship("Exercise", back_populates="attempts")

class ExerciseSet(Base):
    """Model for grouping exercises into sets (e.g., for lessons or tests)."""
    __tablename__ = "exercise_sets"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    exercise_type = Column(Enum(ExerciseType), nullable=True)  # If all exercises are of same type
    difficulty = Column(Enum(DifficultyLevel), nullable=True)  # If all exercises are of same difficulty
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    metadata_ = Column("metadata", JSON, nullable=True)

    # Relationships
    exercises = relationship("ExerciseSetItem", back_populates="exercise_set")

class ExerciseSetItem(Base):
    """Junction table for exercises in exercise sets."""
    __tablename__ = "exercise_set_items"

    id = Column(Integer, primary_key=True, index=True)
    exercise_set_id = Column(Integer, ForeignKey("exercise_sets.id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    order = Column(Integer, default=0)
    points = Column(Integer, default=1)
    required = Column(Boolean, default=True)

    # Relationships
    exercise_set = relationship("ExerciseSet", back_populates="exercises")
    exercise = relationship("Exercise")


class TestSession(Base):
    """Model for tracking user test sessions."""
    __tablename__ = "test_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    test_type = Column(String(50), nullable=False)  # e.g., "ielts_listening", "toefl_writing"
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True), nullable=True)
    time_limit = Column(Integer, nullable=True)  # in seconds
    status = Column(String(20), default="in_progress")  # in_progress, completed, abandoned
    total_score = Column(Float, nullable=True)
    metadata_ = Column("metadata", JSON, nullable=True)

    # Relationships
    user = relationship("User", back_populates="test_sessions")
    responses = relationship("TestResponse", back_populates="test_session")

class TestResponse(Base):
    """Model for storing user responses to test questions."""
    __tablename__ = "test_responses"

    id = Column(Integer, primary_key=True, index=True)
    test_session_id = Column(Integer, ForeignKey("test_sessions.id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    user_answer = Column(JSON, nullable=True)
    is_correct = Column(Boolean, nullable=True)
    score = Column(Float, nullable=True)
    feedback = Column(JSON, nullable=True)
    time_spent = Column(Integer, nullable=True)  # in seconds
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    test_session = relationship("TestSession", back_populates="responses")
    exercise = relationship("Exercise")
