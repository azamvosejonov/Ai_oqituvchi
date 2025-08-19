from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base_class import Base


class VideoAnalysis(Base):
    """Video tahlili uchun model"""
    __tablename__ = "video_analyses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    video_url = Column(String(512), nullable=False)
    thumbnail_url = Column(String(512), nullable=True)
    duration = Column(Integer, nullable=True)  # video davomiyligi sekundlarda
    language = Column(String(10), default="uz", nullable=False)
    is_processed = Column(Boolean, default=False, nullable=False)
    processing_status = Column(String(20), default="pending")  # pending, processing, completed, failed
    analysis_metadata = Column(JSON, nullable=True)  # qo'shimcha ma'lumotlar
    
    # Aloqalar
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    owner = relationship("User", back_populates="video_analyses")
    
    # Vaqt belgilari
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class VideoSegment(Base):
    """Video segmentlari uchun model"""
    __tablename__ = "video_segments"
    
    id = Column(Integer, primary_key=True, index=True)
    video_analysis_id = Column(Integer, ForeignKey("video_analyses.id", ondelete="CASCADE"), nullable=False)
    start_time = Column(Integer, nullable=False)  # segment boshlanish vaqti (sekundlarda)
    end_time = Column(Integer, nullable=False)    # segment tugash vaqti (sekundlarda)
    text = Column(Text, nullable=True)            # transkripsiya matni
    summary = Column(Text, nullable=True)         # qisqacha mazmuni
    
    # Aloqalar
    video_analysis = relationship("VideoAnalysis", back_populates="segments")
    questions = relationship("VideoQuestion", back_populates="segment", cascade="all, delete-orphan")


class VideoQuestion(Base):
    """Video asosidagi savollar uchun model"""
    __tablename__ = "video_questions"
    
    id = Column(Integer, primary_key=True, index=True)
    segment_id = Column(Integer, ForeignKey("video_segments.id", ondelete="CASCADE"), nullable=False)
    question_type = Column(String(50), nullable=False)  # multiple_choice, true_false, short_answer, etc.
    question_text = Column(Text, nullable=False)
    options = Column(JSON, nullable=True)  # variantlar
    correct_answer = Column(JSON, nullable=False)  # to'g'ri javob
    explanation = Column(Text, nullable=True)      # tushuntirish
    difficulty = Column(String(20), default="medium")  # easy, medium, hard
    
    # Aloqalar
    segment = relationship("VideoSegment", back_populates="questions")
    
    # Vaqt belgilari
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


# Aloqalarni qo'shamiz
VideoAnalysis.segments = relationship("VideoSegment", back_populates="video_analysis", cascade="all, delete-orphan")
