import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class PaymentVerification(Base):
    """Model for tracking payment verification requests"""
    __tablename__ = "payment_verifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    username = Column(String, nullable=False)
    payment_proof_path = Column(String, nullable=False)  # Path to uploaded payment proof
    status = Column(String, default="pending")
    admin_notes = Column(String, nullable=True)
    is_processed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="payment_verifications")

    def __repr__(self):
        return f"<PaymentVerification {self.id} - {self.status}>"
