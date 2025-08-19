from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class Certificate(Base):
    __tablename__ = "certificates"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True)
    course_name = Column(String(255), nullable=False)
    level_completed = Column(String(100), nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    issue_date = Column(DateTime, default=datetime.utcnow)
    expiry_date = Column(DateTime, nullable=True)
    verification_code = Column(String(100), unique=True, index=True, nullable=False)
    is_valid = Column(Boolean, default=True)
    file_path = Column(String(500), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="certificates")
    course = relationship("Course", back_populates="certificates")
    
    def __repr__(self):
        return f"<Certificate {self.title} for User {self.user_id}>"
