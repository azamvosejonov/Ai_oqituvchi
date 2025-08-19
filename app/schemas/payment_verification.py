from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
import enum
from pydantic import HttpUrl

# Shared properties
class PaymentVerificationStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class PaymentVerificationBase(BaseModel):
    username: str = Field(..., description="Username of the payer")
    payment_proof_path: str = Field(..., description="Path to the uploaded payment proof")
    status: PaymentVerificationStatus = Field(
        default=PaymentVerificationStatus.PENDING,
        description="Verification status"
    )
    admin_notes: Optional[str] = Field(None, description="Admin notes about the verification")
    rejection_reason: Optional[str] = None

    class Config:
        model_config = ConfigDict(
            from_attributes=True,
        )

# Properties to receive on creation
class PaymentVerificationCreate(PaymentVerificationBase):
    user_id: int = Field(..., description="ID of the user making the payment")

    class Config:
        model_config = ConfigDict(
            from_attributes=True,
        )

# Properties to receive on update
class PaymentVerificationUpdate(PaymentVerificationBase):
    status: Optional[PaymentVerificationStatus] = None
    admin_notes: Optional[str] = None

    class Config:
        model_config = ConfigDict(
            from_attributes=True,
        )

# Properties shared by models stored in DB
class PaymentVerificationInDBBase(PaymentVerificationBase):
    id: int
    user_id: int
    is_processed: bool
    created_at: datetime
    processed_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        model_config = ConfigDict(
            from_attributes=True,
        )

# Properties to return to client
class PaymentVerification(PaymentVerificationInDBBase):
    pass

    class Config:
        model_config = ConfigDict(
            from_attributes=True,
        )

# Properties stored in DB
class PaymentVerificationInDB(PaymentVerificationInDBBase):
    pass

    class Config:
        model_config = ConfigDict(
            from_attributes=True,
        )

# For admin actions
class PaymentVerificationApprove(BaseModel):
    admin_notes: Optional[str] = None
    plan_id: int | None = None
    premium_days: Optional[int] = None

    class Config:
        model_config = ConfigDict(
            from_attributes=True,
        )

class PaymentVerificationReject(PaymentVerificationApprove):
    admin_notes: str = Field(..., description="Reason for rejection")

    class Config:
        model_config = ConfigDict(
            from_attributes=True,
        )

class StripeCheckoutSession(BaseModel):
    session_id: str
    url: HttpUrl

    class Config:
        model_config = ConfigDict(
            from_attributes=True,
        )
