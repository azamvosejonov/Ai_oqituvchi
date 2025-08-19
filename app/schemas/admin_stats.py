from pydantic import BaseModel, ConfigDict
from typing import Dict

class UserStats(BaseModel):
    total_users: int
    active_today: int
    new_this_week: int
    premium_users: int

    model_config = ConfigDict(
        from_attributes=True,
    )

class ContentStats(BaseModel):
    total_courses: int
    total_lessons: int
    total_exercises: int
    total_forum_topics: int

    model_config = ConfigDict(
        from_attributes=True,
    )

class AIUsageStats(BaseModel):
    total_gemini_requests: int
    total_stt_requests: int
    total_tts_chars: int

    model_config = ConfigDict(
        from_attributes=True,
    )

class PlatformStats(BaseModel):
    user_stats: UserStats
    content_stats: ContentStats
    ai_usage_stats: AIUsageStats
    # Add other stats as needed, e.g., financial

    model_config = ConfigDict(
        from_attributes=True,
    )
