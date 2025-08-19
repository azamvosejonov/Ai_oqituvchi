from pydantic import BaseModel, ConfigDict
import datetime

# Base schema for AI usage properties
class UserAIUsageBase(BaseModel):
    gpt4o_requests_left: int
    stt_requests_left: int
    tts_chars_left: int
    pronunciation_analysis_left: int

    model_config = ConfigDict(
        from_attributes=True,
    )

# Schema for creating a new usage record (not typically used directly by API)
class UserAIUsageCreate(UserAIUsageBase):
    user_id: int

    model_config = ConfigDict(
        from_attributes=True,
    )

# Schema for updating usage record
class UserAIUsageUpdate(BaseModel):
    gpt4o_requests_left: int | None = None
    stt_requests_left: int | None = None
    tts_chars_left: int | None = None
    pronunciation_analysis_left: int | None = None

    model_config = ConfigDict(
        from_attributes=True,
    )

# Schema for reading usage data from DB
class UserAIUsageInDBBase(UserAIUsageBase):
    id: int
    user_id: int
    usage_date: datetime.datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class UserAIUsage(UserAIUsageInDBBase):
    pass

    model_config = ConfigDict(
        from_attributes=True,
    )
