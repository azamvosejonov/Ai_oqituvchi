from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

from .interactive_lesson import InteractiveLesson


class CourseBase(BaseModel):
    title: str
    description: Optional[str] = None
    difficulty_level: str
    short_description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    is_published: Optional[bool] = False
    is_featured: Optional[bool] = False
    estimated_duration: Optional[int] = None
    language: Optional[str] = "en"
    price: Optional[float] = 0.0
    discount_price: Optional[float] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    requirements: Optional[List[str]] = None
    learning_outcomes: Optional[List[str]] = None

    class Config:
        model_config = ConfigDict(
            from_attributes=True,
        )


class CourseCreate(CourseBase):
    instructor_id: int


class CourseUpdate(CourseBase):
    pass


class CourseInDBBase(CourseBase):
    id: int
    instructor_id: int
    instructor: Optional['User'] = None
    lessons: List[InteractiveLesson] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        model_config = ConfigDict(
            from_attributes=True,
        )


class Course(CourseInDBBase):
    pass


class CourseInDB(CourseInDBBase):
    pass
