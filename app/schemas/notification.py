from pydantic import BaseModel, EmailStr, HttpUrl, ConfigDict, Field
import datetime
from typing import Optional, Dict, Any, List
from enum import Enum

class NotificationType(str, Enum):
    GENERAL = 'general'
    PAYMENT = 'payment'
    SUBSCRIPTION = 'subscription'
    SYSTEM = 'system'
    FORUM_NEW_REPLY = 'forum_new_reply'
    CERTIFICATE_ISSUED = 'certificate_issued'
    PAYMENT_VERIFICATION_SUBMITTED = 'payment_verification_submitted'
    PAYMENT_VERIFICATION_APPROVED = 'payment_verification_approved'
    PAYMENT_VERIFICATION_REJECTED = 'payment_verification_rejected'
    ADMIN_PAYMENT_VERIFICATION_SUBMITTED = 'admin_payment_verification_submitted'

class PaymentStatus(str, Enum):
    PENDING = 'pending'
    COMPLETED = 'completed'
    FAILED = 'failed'
    REFUNDED = 'refunded'

# Shared properties
class NotificationBase(BaseModel):
    message: Optional[str] = None
    notification_type: NotificationType = NotificationType.GENERAL
    data: Optional[Dict[str, Any]] = None

    class Config:
        model_config = ConfigDict(
            from_attributes=True,
        )

# Properties to receive on item creation
class NotificationCreate(NotificationBase):
    message: str
    user_id: int
    notification_type: NotificationType = NotificationType.GENERAL
    data: Optional[Dict[str, Any]] = None

    class Config:
        model_config = ConfigDict(
            from_attributes=True,
        )

class PaymentNotificationCreate(BaseModel):
    user_id: int
    amount: float
    currency: str = 'USD'
    payment_method: str
    status: PaymentStatus = PaymentStatus.PENDING
    subscription_plan_id: int
    subscription_duration_days: Optional[int] = None
    user_full_name: Optional[str] = None
    user_email: Optional[EmailStr] = None
    user_phone: Optional[str] = None
    receipt_url: Optional[HttpUrl] = None
    payment_provider: str = 'stripe'  # stripe, click, payme, etc.
    payment_id: str  # ID from payment provider
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        model_config = ConfigDict(
            from_attributes=True,
        )

class UnreadCount(BaseModel):
    unread_count: int

    class Config:
        model_config = ConfigDict(
            from_attributes=True,
        )

# Properties to receive on item update
class NotificationUpdate(BaseModel):
    is_read: Optional[bool] = None
    status: Optional[PaymentStatus] = None
    receipt_url: Optional[HttpUrl] = None

    class Config:
        model_config = ConfigDict(
            from_attributes=True,
        )


# Properties shared by models stored in DB
class NotificationInDBBase(BaseModel):
    id: int
    user_id: int
    message: str
    is_read: bool
    created_at: datetime.datetime
    notification_type: NotificationType
    data: Optional[Dict[str, Any]] = None

    class Config:
        model_config = ConfigDict(
            from_attributes=True,
        )


# Properties to return to client
class Notification(NotificationInDBBase):
    pass

    class Config:
        model_config = ConfigDict(
            from_attributes=True,
        )


# Properties stored in DB
class NotificationInDB(NotificationInDBBase):
    pass

    class Config:
        model_config = ConfigDict(
            from_attributes=True,
        )
