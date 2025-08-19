from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime

from .user import User
from .ai_usage_stats import AIUsageStats


class TopLearner(BaseModel):
    full_name: str
    completed_lessons: int

    class Config:
        model_config = ConfigDict(
            from_attributes=True,
        )


class TopCourse(BaseModel):
    title: str
    enrolled_users: int

    class Config:
        model_config = ConfigDict(
            from_attributes=True,
        )


class UserStats(BaseModel):
    user: User
    lesson_count: int
    total_score: float

    class Config:
        model_config = ConfigDict(
            from_attributes=True,
        )


class PaymentStats(BaseModel):
    total_revenue: float
    active_subscriptions_count: int

    class Config:
        model_config = ConfigDict(
            from_attributes=True,
        )


class GeneralStats(BaseModel):
    total_users: int
    total_lessons: int
    total_courses: int
    user_completed_lessons: int
    user_level: str
    user_is_premium: bool

    class Config:
        model_config = ConfigDict(
            from_attributes=True,
        )


class DashboardStats(BaseModel):
    total_users: int
    premium_users: int
    total_courses: int
    total_lessons: int
    total_words: int
    active_subscriptions: int
    total_revenue: float
    ai_usage_stats: AIUsageStats
    pending_payments: int
    top_learners: List[TopLearner]
    top_courses: List[TopCourse]

    class Config:
        model_config = ConfigDict(
            from_attributes=True,
        )
