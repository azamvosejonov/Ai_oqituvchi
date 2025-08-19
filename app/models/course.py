from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Float, Enum as DBEnum, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base
import enum

class Course(Base):
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    short_description = Column(String(500), nullable=True)
    thumbnail_url = Column(String(500), nullable=True)
    is_published = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)
    difficulty_level = Column(String(50), default="beginner")  # beginner, intermediate, advanced
    estimated_duration = Column(Integer, nullable=True)  # in minutes
    language = Column(String(50), default="en")
    price = Column(Float, default=0.0)
    discount_price = Column(Float, nullable=True)
    instructor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    category = Column(String(100), nullable=True)
    tags = Column(JSON, nullable=True)  # Stored as JSON array
    requirements = Column(JSON, nullable=True)  # Stored as JSON array
    learning_outcomes = Column(JSON, nullable=True)  # Stored as JSON array
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    instructor = relationship("User", back_populates="courses_taught")
    lessons = relationship("app.models.lesson.InteractiveLesson", back_populates="course", cascade="all, delete-orphan")
    enrollments = relationship("Enrollment", back_populates="course", cascade="all, delete-orphan")
    certificates = relationship("Certificate", back_populates="course")
    homeworks = relationship("app.models.homework.Homework", back_populates="course", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Course {self.title}>"


class Enrollment(Base):
    __tablename__ = "enrollments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    enrollment_date = Column(DateTime, default=datetime.utcnow)
    completion_date = Column(DateTime, nullable=True)
    progress = Column(Integer, default=0)  # 0-100 percentage
    is_active = Column(Boolean, default=True)
    last_accessed = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")
    
    def __repr__(self):
        return f"<Enrollment User {self.user_id} in Course {self.course_id}>"
