from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, HttpUrl, ConfigDict, field_validator
import json
from datetime import datetime
from enum import Enum

# --- ENUMS ---
class LessonType(str, Enum):
    CONVERSATION = "conversation"
    PRONUNCIATION = "pronunciation"
    GRAMMAR = "grammar"
    VOCABULARY = "vocabulary"

class LessonSessionStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"

# --- INTERACTIVE LESSON SCHEMAS ---
class InteractiveLessonBase(BaseModel):
    title: str
    order: int
    description: Optional[str] = None
    video_url: Optional[str] = None
    difficulty: str = "beginner"
    is_premium: bool = False
    is_active: bool = True
    content: Dict[str, Any]
    tags: Optional[List[str]] = None
    estimated_duration: Optional[int] = None

    model_config = ConfigDict(
        from_attributes=True,
    )

    # Normalize JSON-like fields that might come from DB as strings
    @field_validator("content", mode="before")
    @classmethod
    def _normalize_content(cls, v):
        if v is None:
            return {}
        if isinstance(v, (dict, list)):
            return v
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                return parsed if isinstance(parsed, (dict, list)) else {"raw": v}
            except Exception:
                return {"raw": v}
        return v

    @field_validator("tags", mode="before")
    @classmethod
    def _normalize_tags(cls, v):
        if v is None:
            return None
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            # Try JSON array first
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
                if isinstance(parsed, str):
                    return [parsed]
            except Exception:
                # Fallback: treat as comma-separated values
                return [s.strip() for s in v.split(",") if s.strip()]
        return v

class InteractiveLessonCreate(InteractiveLessonBase):
    course_id: Optional[int] = None
    avatar_id: int

    model_config = ConfigDict(
        from_attributes=True,
    )

class InteractiveLessonUpdate(InteractiveLessonBase):
    pass

    model_config = ConfigDict(
        from_attributes=True,
    )

class InteractiveLessonInDBBase(InteractiveLessonBase):
    id: int
    course_id: int
    avatar_id: int

    model_config = ConfigDict(
        from_attributes=True,
    )

class InteractiveLesson(InteractiveLessonInDBBase):
    pass

    model_config = ConfigDict(
        from_attributes=True,
    )

# --- SESSION & INTERACTION SCHEMAS ---
class LessonSessionBase(BaseModel):
    """Base schema for lesson session"""
    lesson_type: LessonType
    topic: Optional[str] = None
    difficulty: str = "beginner"
    avatar_type: str = "default"
    status: LessonSessionStatus = LessonSessionStatus.IN_PROGRESS

    model_config = ConfigDict(
        from_attributes=True,
    )

class LessonSessionCreate(LessonSessionBase):
    """Schema for creating a new lesson session"""
    user_id: int

    model_config = ConfigDict(
        from_attributes=True,
    )

class LessonSessionUpdate(BaseModel):
    """Schema for updating a lesson session"""
    status: Optional[LessonSessionStatus] = None
    ended_at: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes=True,
    )

class LessonSessionInDBBase(LessonSessionBase):
    """Base schema for lesson session in database"""
    id: int
    user_id: int
    started_at: datetime
    ended_at: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes=True,
    )

class InteractiveLessonSessionCreate(LessonSessionBase):
    """Schema for creating a new interactive lesson session"""
    user_id: int

    model_config = ConfigDict(
        from_attributes=True,
    )

class LessonStart(BaseModel):
    """Data for starting a new interactive lesson"""
    lesson_type: LessonType = Field(..., description="Type of lesson (e.g., 'conversation', 'pronunciation')")
    topic: Optional[str] = Field(None, description="Optional topic for the lesson")
    difficulty: str = Field("beginner", description="Difficulty level (beginner, intermediate, advanced)")
    avatar_type: str = Field("default", description="Type of AI avatar to use")

    model_config = ConfigDict(
        from_attributes=True,
    )

class LessonStartResponse(BaseModel):
    """Response for starting a new interactive lesson"""
    id: int
    user_id: int
    lesson_type: LessonType
    started_at: datetime
    status: LessonSessionStatus
    avatar_type: str
    greeting: str
    avatar_name: str
    audio_url: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True,
    )

class UserMessage(BaseModel):
    """User message to AI tutor"""
    session_id: int = Field(..., description="ID of the current lesson session")
    message: str = Field(..., description="User's message to the AI tutor")
    message_type: str = Field("text", description="Type of message (text/audio)")

    model_config = ConfigDict(
        from_attributes=True,
    )

class AIResponse(BaseModel):
    """AI tutor's response"""
    text: str = Field(..., description="AI's text response")
    audio_url: Optional[str] = Field(None, description="URL to AI's audio response")
    avatar_type: str = Field(..., description="Type of AI avatar responding")
    avatar_name: str = Field(..., description="Name of the AI avatar")
    suggestions: Optional[List[str]] = Field(None, description="Suggested responses or actions")

    model_config = ConfigDict(
        from_attributes=True,
    )

class PronunciationAttemptBase(BaseModel):
    """Base schema for pronunciation attempt"""
    session_id: Optional[int] = None
    user_id: int
    expected_text: str
    recognized_text: str
    score: float
    feedback: Optional[str] = None
    word_scores: Optional[Dict[str, float]] = None
    audio_url: Optional[HttpUrl] = None

    model_config = ConfigDict(
        from_attributes=True,
    )

class PronunciationAttemptCreate(PronunciationAttemptBase):
    """Schema for creating a new pronunciation attempt"""
    pass

    model_config = ConfigDict(
        from_attributes=True,
    )

class PronunciationAttemptInDBBase(PronunciationAttemptBase):
    """Base schema for pronunciation attempt in database"""
    id: int
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )

class PronunciationAttempt(PronunciationAttemptInDBBase):
    """Schema for returning a pronunciation attempt"""
    pass

    model_config = ConfigDict(
        from_attributes=True,
    )

class PronunciationAssessment(BaseModel):
    """Pronunciation assessment result"""
    recognized_text: str = Field(..., description="Text recognized from speech")
    pronunciation_score: float = Field(..., description="Pronunciation score (0-1)")
    feedback: str = Field(..., description="Detailed feedback on pronunciation")
    word_scores: Optional[Dict[str, float]] = Field(None, description="Scores for individual words")

    model_config = ConfigDict(
        from_attributes=True,
    )

class LessonInteractionBase(BaseModel):
    """Base schema for lesson interaction"""
    session_id: int
    user_message: str
    ai_response: str
    audio_url: Optional[HttpUrl] = None

    model_config = ConfigDict(
        from_attributes=True,
    )

class LessonInteractionCreate(LessonInteractionBase):
    """Schema for creating a new lesson interaction"""
    pass

    model_config = ConfigDict(
        from_attributes=True,
    )

class LessonInteractionInDBBase(LessonInteractionBase):
    """Base schema for lesson interaction in database"""
    id: int
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )

class LessonInteraction(LessonInteractionInDBBase):
    """Schema for returning a lesson interaction"""
    pass

    model_config = ConfigDict(
        from_attributes=True,
    )

class InteractiveLessonSessionInDB(LessonSessionInDBBase):
    """Schema for interactive lesson session in database"""
    pass

    model_config = ConfigDict(
        from_attributes=True,
    )

class AvatarOption(BaseModel):
    """Available AI avatar options"""
    name: str = Field(..., description="Display name of the avatar")
    style: str = Field(..., description="Teaching style of the avatar")
    sample_greeting: str = Field(..., description="Sample greeting from the avatar")

    model_config = ConfigDict(
        from_attributes=True,
    )
