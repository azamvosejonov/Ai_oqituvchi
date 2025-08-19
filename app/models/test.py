from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, Float, func, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base
import enum

class TestType(enum.Enum):
    IELTS = "ielts"
    TOEFL = "toefl"
    PRACTICE = "practice"

class TestSectionType(enum.Enum):
    LISTENING = "listening"
    READING = "reading"
    WRITING = "writing"
    SPEAKING = "speaking"

class QuestionType(enum.Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"
    ESSAY = "essay"
    MATCHING = "matching"
    FILL_BLANKS = "fill_blanks"

class Test(Base):
    """Model for storing test information"""
    __tablename__ = "tests"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    test_type = Column(String(50), nullable=False)
    duration_minutes = Column(Integer, nullable=False)  # Total duration in minutes
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    sections = relationship("TestSection", back_populates="test", cascade="all, delete-orphan")
    attempts = relationship("TestAttempt", back_populates="test")

class TestSection(Base):
    """Model for test sections (Listening, Reading, Writing, Speaking)"""
    __tablename__ = "test_sections"
    
    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("tests.id"), nullable=False)
    section_type = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    instructions = Column(Text)
    duration_minutes = Column(Integer, nullable=False)  # Duration for this section
    order_index = Column(Integer, nullable=False)  # To maintain section order
    
    # Relationships
    test = relationship("Test", back_populates="sections")
    questions = relationship("TestQuestion", back_populates="section", cascade="all, delete-orphan")

class TestQuestion(Base):
    """Model for test questions"""
    __tablename__ = "test_questions"
    
    id = Column(Integer, primary_key=True, index=True)
    section_id = Column(Integer, ForeignKey("test_sections.id"), nullable=False)
    question_type = Column(String(50), nullable=False)
    question_text = Column(Text, nullable=False)
    question_data = Column(JSON)  # For storing question-specific data (options, correct answers, etc.)
    audio_url = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    marks = Column(Float, default=1.0)  # Marks for this question
    order_index = Column(Integer, nullable=False)  # To maintain question order
    
    # Relationships
    section = relationship("TestSection", back_populates="questions")
    answers = relationship("TestAnswer", back_populates="question")

class TestAttempt(Base):
    """Model for tracking user test attempts"""
    __tablename__ = "test_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    test_id = Column(Integer, ForeignKey("tests.id"), nullable=False)
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True))
    time_spent_seconds = Column(Integer, default=0)  # Total time spent in seconds
    is_completed = Column(Boolean, default=False)
    total_score = Column(Float, default=0.0)
    max_score = Column(Float, default=0.0)
    
    # Relationships
    user = relationship("User", back_populates="test_attempts", foreign_keys=lambda: [TestAttempt.user_id])
    test = relationship("Test", back_populates="attempts")
    answers = relationship("TestAnswer", back_populates="attempt", cascade="all, delete-orphan")

class TestAnswer(Base):
    """Model for storing user answers to test questions"""
    __tablename__ = "test_answers"
    
    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey("test_attempts.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("test_questions.id"), nullable=False)
    answer_data = Column(Text)  # For storing the user's answer
    is_correct = Column(Boolean, default=None)  # NULL = not graded yet
    score = Column(Float, default=0.0)  # Score for this answer
    feedback = Column(Text)  # Feedback for the answer
    
    # Relationships
    attempt = relationship("TestAttempt", back_populates="answers")
    question = relationship("TestQuestion", back_populates="answers")
