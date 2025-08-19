from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Any

from .word import Word


class LessonBase(BaseModel):
    title: str
    content: Optional[str] = None
    video_url: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True,
    )


class LessonCreate(LessonBase):
    course_id: int
    title: str
    content: str
    order: int
    is_premium: bool = False
    video_url: Optional[str] = None
    avatar_id: int

    model_config = ConfigDict(
        from_attributes=True,
    )


class LessonUpdate(LessonBase):
    title: Optional[str] = None
    content: Optional[str] = None
    order: Optional[int] = None
    is_premium: Optional[bool] = None
    video_url: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True,
    )


class LessonInDBBase(LessonBase):
    id: int
    course_id: int
    title: str

    model_config = ConfigDict(
        from_attributes=True,
    )


class Lesson(LessonInDBBase):
    id: int
    content: Any  # Allow any type for content to fix validation
    is_premium: Optional[bool] = False  # Make is_premium optional
    order: int
    video_url: Optional[str] = None
    words: List[Word] = []

    model_config = ConfigDict(
        from_attributes=True,
    )


class LessonInDB(LessonInDBBase):
    model_config = ConfigDict(
        from_attributes=True,
    )
