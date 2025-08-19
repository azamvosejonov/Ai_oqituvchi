"""
Foydalanuvchi darajasi va progress modellari.
"""
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class UserLevel(str, PyEnum):
    BEGINNER = "beginner"
    ELEMENTARY = "elementary"
    PRE_INTERMEDIATE = "pre_intermediate"
    INTERMEDIATE = "intermediate"
    UPPER_INTERMEDIATE = "upper_intermediate"
    ADVANCED = "advanced"
    PROFICIENT = "proficient"

class UserProgress(Base):
    """Foydalanuvchi progressi modeli."""
    __tablename__ = "user_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    level = Column(SQLEnum(UserLevel), default=UserLevel.BEGINNER, nullable=False)
    
    # Progress metrikalari
    vocabulary_score = Column(Float, default=0.0)  # Lug'at boyligi balli
    grammar_score = Column(Float, default=0.0)     # Grammatika balli
    speaking_score = Column(Float, default=0.0)    # Gapirish balli
    listening_score = Column(Float, default=0.0)   # Eshitish balli
    
    # Progress statistikasi
    total_lessons_completed = Column(Integer, default=0)  # Tugatilgan darslar soni
    total_exercises_completed = Column(Integer, default=0)  # Bajarilgan mashqlar soni
    total_time_spent = Column(Integer, default=0)  # Sarflangan vaqt (daqiqalarda)
    
    # Progressni yangilash vaqti
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Aloqalar
    user = relationship("User", back_populates="progress", foreign_keys=lambda: [UserProgress.user_id])
    
    def calculate_overall_score(self) -> float:
        """Umumiy ballni hisoblash."""
        return (self.vocabulary_score * 0.25 + 
                self.grammar_score * 0.25 + 
                self.speaking_score * 0.25 + 
                self.listening_score * 0.25)
    
    def determine_level(self) -> UserLevel:
        """Foydalanuvchi darajasini aniqlash."""
        score = self.calculate_overall_score()
        
        if score >= 90:
            return UserLevel.PROFICIENT
        elif score >= 80:
            return UserLevel.ADVANCED
        elif score >= 65:
            return UserLevel.UPPER_INTERMEDIATE
        elif score >= 50:
            return UserLevel.INTERMEDIATE
        elif score >= 35:
            return UserLevel.PRE_INTERMEDIATE
        elif score >= 20:
            return UserLevel.ELEMENTARY
        else:
            return UserLevel.BEGINNER

# UserLessonProgress model has been moved to user_lesson_progress.py to avoid circular imports.
