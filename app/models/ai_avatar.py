from sqlalchemy import Column, Integer, String, ForeignKey, JSON, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class AIAvatar(Base):
    """AI Avatar model for interactive lessons"""
    __tablename__ = "ai_avatars"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    avatar_url = Column(String(512), nullable=False)
    voice_id = Column(String(100), nullable=False)
    language = Column(String(20), default="en-US", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    metadata_ = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    interactive_lessons = relationship("app.models.lesson.InteractiveLesson", back_populates="avatar")
