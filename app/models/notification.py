import datetime
import enum
import json
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base

class NotificationType(str, enum.Enum):
    GENERAL = 'general'
    PAYMENT = 'payment'
    SUBSCRIPTION = 'subscription'
    SYSTEM = 'system'
    FORUM_NEW_REPLY = 'forum_new_reply'
    CERTIFICATE_ISSUED = 'certificate_issued'
    # Payment verification specific types
    PAYMENT_VERIFICATION_SUBMITTED = 'payment_verification_submitted'
    PAYMENT_VERIFICATION_APPROVED = 'payment_verification_approved'
    PAYMENT_VERIFICATION_REJECTED = 'payment_verification_rejected'
    # Admin specific types
    ADMIN_PAYMENT_VERIFICATION_SUBMITTED = 'admin_payment_verification_submitted'

class PaymentStatus(str, enum.Enum):
    PENDING = 'pending'
    COMPLETED = 'completed'
    FAILED = 'failed'
    REFUNDED = 'refunded'

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(255), nullable=True)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    notification_type = Column(String(50), default=NotificationType.GENERAL, nullable=False, index=True)
    data = Column(JSON, nullable=True, default=dict)
    
    # Payment specific fields
    payment_status = Column(String(20), nullable=True, index=True)
    payment_id = Column(String(100), nullable=True, index=True)
    payment_provider = Column(String(50), nullable=True)
    amount = Column(Integer, nullable=True)  # in smallest currency unit (e.g., cents)
    currency = Column(String(3), default='USD')
    receipt_url = Column(String(512), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    
    def __init__(self, **kwargs):
        # Convert notification_type to string if it's an enum
        if 'notification_type' in kwargs and hasattr(kwargs['notification_type'], 'value'):
            kwargs['notification_type'] = kwargs['notification_type'].value
        super().__init__(**kwargs)
    
    @property
    def payment_data(self):
        """Helper to access payment data"""
        if self.notification_type in [NotificationType.PAYMENT, NotificationType.SUBSCRIPTION]:
            return {
                'payment_id': self.payment_id,
                'status': self.payment_status,
                'amount': self.amount,
                'currency': self.currency,
                'receipt_url': self.receipt_url,
                'provider': self.payment_provider,
                'data': self.data or {}
            }
        return None
