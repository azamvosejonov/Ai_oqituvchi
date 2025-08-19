from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field, ConfigDict

from .lesson import Lesson
from .exercise import Exercise

class PersonalizedRecommendations(BaseModel):
    lessons: Optional[List[Lesson]] = []
    exercises: Optional[List[Exercise]] = []

    model_config = ConfigDict(
        from_attributes=True,
    )

class AdaptiveLessonStep(BaseModel):
    step: int
    title: str
    description: str
    content_type: str # 'exercise' or 'explanation'
    content: Dict[str, Any]

    model_config = ConfigDict(
        from_attributes=True,
    )

class AdaptiveLessonPlan(BaseModel):
    lesson_id: int
    title: str
    steps: List[AdaptiveLessonStep]

    model_config = ConfigDict(
        from_attributes=True,
    )

class ForYouRecommendations(BaseModel):
    continue_learning: Optional[List[Lesson]] = []
    based_on_level: Optional[List[Lesson]] = []
    popular: Optional[List[Lesson]] = []
    new: Optional[List[Lesson]] = []

    model_config = ConfigDict(
        from_attributes=True,
    )
