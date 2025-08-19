from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class LessonSessionStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"

from .user import User
from .lesson import Lesson


# Shared properties
class LessonSessionBase(BaseModel):
    status: LessonSessionStatus = Field(LessonSessionStatus.IN_PROGRESS, description="Status of the session")
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    lesson_id: int

    model_config = ConfigDict(
        from_attributes=True,
    )


# Properties to receive on session creation
class LessonSessionCreate(LessonSessionBase):
    user_id: int

    model_config = ConfigDict(
        from_attributes=True,
    )


# Properties to receive on session update
class LessonSessionUpdate(BaseModel):
    status: Optional[LessonSessionStatus] = None
    end_time: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes=True,
    )


# Properties shared by models stored in DB
class LessonSessionInDBBase(LessonSessionBase):
    id: int
    user_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes=True,
    )


# Properties to return to client
class LessonSession(LessonSessionInDBBase):
    user: Optional[User] = None
    lesson: Optional[Lesson] = None

    model_config = ConfigDict(
        from_attributes=True,
    )


# Properties properties stored in DB
class LessonSessionInDB(LessonSessionInDBBase):
    pass

    model_config = ConfigDict(
        from_attributes=True,
    )


# Additional models
class LessonSessionWithInteractions(LessonSession):
    interactions: List[dict] = []

    model_config = ConfigDict(
        from_attributes=True,
    )
