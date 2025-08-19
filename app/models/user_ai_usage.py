from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base_class import Base


class UserAIUsage(Base):
    __tablename__ = "user_ai_usage"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    usage_date = Column(DateTime, nullable=False, default=datetime.now)
    
    # Fields to track total usage
    gemini_requests = Column(Integer, default=0)
    stt_requests = Column(Integer, default=0)
    tts_characters = Column(Integer, default=0)
    pronunciation_analysis = Column(Integer, default=0)

    # Fields to track remaining quota
    gpt4o_requests_left = Column(Integer, default=0)
    tts_chars_left = Column(Integer, default=0)
    stt_requests_left = Column(Integer, default=0)
    pronunciation_analysis_left = Column(Integer, default=0)

    # Relationship
    user = relationship("User", back_populates="ai_usage")
