from sqlalchemy import (Column, Integer, String, Text, DateTime, ForeignKey, Float,
                        Enum, Boolean, func, JSON)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base
import enum

from app.schemas.homework import HomeworkType, HomeworkStatus


# Import HomeworkType and HomeworkStatus from the correct location

class Homework(Base):
    """Homework model for storing homework assignments.
    
    This model represents a homework assignment that can be associated with a course and optionally a specific lesson.
    """
    __tablename__ = "homeworks"  # Changed from 'homework' to 'homeworks' for consistency
    __table_args__ = {
        'extend_existing': True,
        'sqlite_autoincrement': True
    }
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    instructions = Column(Text, nullable=True)
    homework_type = Column(Enum(HomeworkType), nullable=False, default=HomeworkType.WRITTEN)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    lesson_id = Column(Integer, ForeignKey("interactive_lessons.id", ondelete="CASCADE"), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    due_date = Column(DateTime(timezone=True), nullable=True)
    max_score = Column(Integer, default=100, nullable=False)
    is_published = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), default=func.now())
    metadata_ = Column("metadata", JSON, nullable=True)
    
    # Relationships with proper cascade and backrefs
    course = relationship("Course", back_populates="homeworks")
    
    # Relationship with Lesson using string-based reference to avoid circular imports
    lesson = relationship(
        "app.models.lesson.InteractiveLesson", 
        back_populates="homeworks",
        foreign_keys=[lesson_id],
    )
    
    # Relationship with User who created the homework
    creator_user = relationship("User", foreign_keys=[created_by])
    
    # Relationship with submissions
    submissions = relationship(
        "HomeworkSubmission", 
        back_populates="homework",
        cascade="all, delete-orphan"
    )
    
    # Relationship with oral assignment details
    oral_assignment_details = relationship("OralAssignment", back_populates="homework", uselist=False, cascade="all, delete-orphan")

class HomeworkSubmission(Base):
    """Homework submissions by students"""
    __tablename__ = "homework_submissions"
    
    id = Column(Integer, primary_key=True, index=True)
    homework_id = Column(Integer, ForeignKey("homeworks.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=True)  # For written answers or text content
    file_url = Column(String(512), nullable=True)  # For file uploads
    audio_url = Column(String(512), nullable=True)  # For oral submissions
    status = Column(Enum(HomeworkStatus), default=HomeworkStatus.PENDING, nullable=False)
    score = Column(Integer, nullable=True)
    feedback = Column(Text, nullable=True)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    graded_at = Column(DateTime(timezone=True), nullable=True)
    graded_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    metadata_ = Column("metadata", JSON, nullable=True)
    
    # Relationships
    homework = relationship("Homework", back_populates="submissions")
    student = relationship("User", back_populates="homework_submissions", foreign_keys=[student_id])
    grader = relationship("User", foreign_keys=[graded_by])

class OralAssignment(Base):
    """Specialized model for oral assignments"""
    __tablename__ = "oral_assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    homework_id = Column(Integer, ForeignKey("homeworks.id"), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    topic = Column(String(255), nullable=False)
    time_limit = Column(Integer, nullable=True)  # Time limit in seconds
    questions = Column(JSON, nullable=True)  # List of questions or prompts
    criteria = Column(JSON, nullable=True)  # Grading criteria
    
    # Relationship back to the main homework entry
    homework = relationship("Homework", back_populates="oral_assignment_details")
    user = relationship("User", back_populates="oral_assignments")

class HomeworkFeedback(Base):
    """Detailed feedback for homework submissions"""
    __tablename__ = "homework_feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("homework_submissions.id"), nullable=False)
    criteria_scores = Column(JSON, nullable=True)  # Detailed scores per criteria
    comments = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), default=func.now())
    
    # Relationships
    submission = relationship("HomeworkSubmission", backref="detailed_feedback")
