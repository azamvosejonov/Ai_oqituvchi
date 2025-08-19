from pydantic import BaseModel, ConfigDict
from typing import Optional, Any
from datetime import datetime

# Subscription Plan Schemas

class SubscriptionPlanBase(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    duration_days: Optional[int] = None
    description: Optional[str] = None
    stripe_price_id: Optional[str] = None
    gpt4o_requests_quota: Optional[int] = 0
    stt_requests_quota: Optional[int] = 0
    tts_chars_quota: Optional[int] = 0
    pronunciation_analysis_quota: Optional[int] = 0

    model_config = ConfigDict(
        from_attributes=True,
    )

class SubscriptionPlanCreate(SubscriptionPlanBase):
    name: str
    price: float
    duration_days: int
    stripe_price_id: str

    model_config = ConfigDict(
        from_attributes=True,
    )

class SubscriptionPlanUpdate(SubscriptionPlanBase):
    pass

    model_config = ConfigDict(
        from_attributes=True,
    )

class SubscriptionPlanInDBBase(SubscriptionPlanBase):
    id: int
    name: str
    price: float
    description: Optional[str]
    stripe_price_id: Optional[str] = None
    gpt4o_requests_quota: int
    stt_requests_quota: int
    tts_chars_quota: int
    pronunciation_analysis_quota: int
    duration_days: int

    model_config = ConfigDict(
        from_attributes=True,
    )

class SubscriptionPlan(SubscriptionPlanInDBBase):
    pass

    model_config = ConfigDict(
        from_attributes=True,
    )

# Subscription Schemas

class SubscriptionBase(BaseModel):
    plan_id: int
    end_date: datetime
    is_active: bool = True

    model_config = ConfigDict(
        from_attributes=True,
    )

class SubscriptionCreate(SubscriptionBase):
    user_id: int

    model_config = ConfigDict(
        from_attributes=True,
    )

class SubscriptionUpdate(BaseModel):
    is_active: Optional[bool] = None

    model_config = ConfigDict(
        from_attributes=True,
    )

class SubscriptionInDBBase(SubscriptionBase):
    id: int
    user_id: int
    start_date: datetime
    plan: SubscriptionPlan

    model_config = ConfigDict(
        from_attributes=True,
    )

class Subscription(SubscriptionInDBBase):
    pass

    model_config = ConfigDict(
        from_attributes=True,
    )
