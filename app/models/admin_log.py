from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base_class import Base

class AdminLog(Base):
    __tablename__ = "admin_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50), nullable=True)  # e.g., 'user', 'course', 'lesson'
    entity_id = Column(Integer, nullable=True)  # ID of the affected entity
    details = Column(JSON, nullable=True)  # Additional details about the action
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    admin = relationship("User", foreign_keys=[admin_id])
    
    def __repr__(self):
        return f"<AdminLog {self.action} by Admin {self.admin_id}>"
