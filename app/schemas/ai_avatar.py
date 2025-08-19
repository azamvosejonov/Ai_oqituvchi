from pydantic import BaseModel, HttpUrl, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class AIAvatarBase(BaseModel):
    name: str
    description: Optional[str] = None
    avatar_url: HttpUrl
    voice_id: str
    language: str = "en-US"
    is_active: bool = True
    metadata: Dict[str, Any] = {}

    model_config = ConfigDict(
        from_attributes=True,
    )

class AIAvatarCreate(AIAvatarBase):
    pass

class AIAvatarUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    avatar_url: Optional[HttpUrl] = None
    voice_id: Optional[str] = None
    language: Optional[str] = None
    is_active: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(
        from_attributes=True,
    )

class AIAvatarInDBBase(AIAvatarBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )

class AIAvatar(AIAvatarInDBBase):
    pass

class AIAvatarInDB(AIAvatarInDBBase):
    pass

class LessonDifficulty(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class InteractiveLessonBase(BaseModel):
    title: str
    description: Optional[str] = None
    content: Dict[str, Any]
    avatar_id: int
    difficulty: LessonDifficulty = LessonDifficulty.BEGINNER
    estimated_duration: Optional[int] = None
    is_premium: bool = False
    is_active: bool = True
    tags: List[str] = []

    model_config = ConfigDict(
        from_attributes=True,
    )

class InteractiveLessonCreate(InteractiveLessonBase):
    pass

class InteractiveLessonUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    content: Optional[Dict[str, Any]] = None
    avatar_id: Optional[int] = None
    difficulty: Optional[LessonDifficulty] = None
    estimated_duration: Optional[int] = None
    is_premium: Optional[bool] = None
    is_active: Optional[bool] = None
    tags: Optional[List[str]] = None

    model_config = ConfigDict(
        from_attributes=True,
    )

class InteractiveLessonInDBBase(InteractiveLessonBase):
    id: int
    created_at: datetime
    updated_at: datetime
    avatar: AIAvatar

    model_config = ConfigDict(
        from_attributes=True,
    )

class InteractiveLesson(InteractiveLessonInDBBase):
    pass

class InteractiveLessonStart(BaseModel):
    lesson_id: str

    model_config = ConfigDict(
        from_attributes=True,
    )

class InteractiveLessonSession(BaseModel):
    lesson_id: int
    user_id: int
    current_step: int = 0
    progress: float = 0.0
    metadata: Dict[str, Any] = {}

    model_config = ConfigDict(
        from_attributes=True,
    )

class LessonInteraction(BaseModel):
    message: str

    model_config = ConfigDict(
        from_attributes=True,
    )

class LessonInteractionBase(BaseModel):
    user_message: str
    ai_response: str
    metadata: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(
        from_attributes=True,
    )

class LessonInteractionCreate(LessonInteractionBase):
    pass

class LessonInteractionInDB(LessonInteractionBase):
    id: int
    session_id: int
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )

class PronunciationAssessmentRequest(BaseModel):
    reference_text: str

    model_config = ConfigDict(
        from_attributes=True,
    )

class PronunciationAssessmentResponse(BaseModel):
    accuracy_score: float
    pronunciation_score: float
    completeness_score: float
    fluency_score: float
    words: List[Dict[str, Any]]

    model_config = ConfigDict(
        from_attributes=True,
    )

class InteractiveResponse(BaseModel):
    message: str
    audio_url: Optional[HttpUrl] = None
    audio_data: Optional[bytes] = None
    next_step: int
    is_complete: bool = False
    options: Optional[List[Dict[str, Any]]] = None
    feedback: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(
        from_attributes=True,
    )
