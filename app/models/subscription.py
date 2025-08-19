from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Boolean, Text
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    duration_days = Column(Integer, nullable=False)  # Subscription duration in days
    stripe_price_id = Column(String(255), unique=True, nullable=True)
    is_active = Column(Boolean, default=True)
    features = Column(Text, nullable=True)  # JSON string of features
    ai_quota = Column(Integer, nullable=False, default=0)

    # AI Quotas
    gpt4o_requests_quota = Column(Integer, default=0)
    stt_requests_quota = Column(Integer, default=0)
    tts_chars_quota = Column(Integer, default=0)
    pronunciation_analysis_quota = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    subscriptions = relationship("Subscription", back_populates="plan")
    
    def __repr__(self):
        return f"<SubscriptionPlan {self.name}>"


class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("subscription_plans.id"), nullable=False)
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    payment_id = Column(String(100), nullable=True)
    payment_method = Column(String(50), nullable=True)
    amount_paid = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="subscriptions")
    plan = relationship("SubscriptionPlan", back_populates="subscriptions")
    
    def __repr__(self):
        return f"<Subscription {self.user_id} - {self.plan_id}>"
    
    @property
    def is_valid(self) -> bool:
        """Check if subscription is currently active."""
        now = datetime.utcnow()
        return self.is_active and self.start_date <= now <= self.end_date
