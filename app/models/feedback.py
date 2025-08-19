from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base_class import Base

class Feedback(Base):
    __tablename__ = "feedbacks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    rating = Column(Float, nullable=True)  # 1-5 rating
    is_public = Column(Boolean, default=False)
    status = Column(String(20), default="pending")  # pending, approved, rejected
    response = Column(Text, nullable=True)
    response_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    response_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="feedbacks")
    responder = relationship("User", foreign_keys=[response_by])
    
    def __repr__(self):
        return f"<Feedback {self.id} by User {self.user_id}>"
