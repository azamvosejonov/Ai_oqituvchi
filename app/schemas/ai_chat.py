from typing import List, Optional, Dict, Any, Union
from enum import Enum
from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from datetime import datetime

class DifficultyLevel(str, Enum):
    """Enum for difficulty levels of exercises and lessons."""
    BEGINNER = "beginner"
    ELEMENTARY = "elementary"
    PRE_INTERMEDIATE = "pre_intermediate"
    INTERMEDIATE = "intermediate"
    UPPER_INTERMEDIATE = "upper_intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    NATIVE = "native"

    model_config = ConfigDict(
        from_attributes=True,
    )

class AIChatInput(BaseModel):
    """Input model for AI chat requests."""
    message: str = Field(..., description="The user's message to the AI")
    lesson_id: Optional[int] = Field(None, description="Optional lesson ID for context")
    session_id: Optional[str] = Field(None, description="Optional session ID for multi-turn conversations")
    metadata: Optional[Dict[str, Any]] = Field(
        None, 
        description="Additional metadata for the message"
    )
    log_usage: bool = Field(
        True, 
        description="Whether to log this interaction for quota purposes"
    )

    model_config = ConfigDict(
        from_attributes=True,
    )

class AIChatResponse(BaseModel):
    """Response model for AI chat requests."""
    response: str = Field(..., description="The AI's response message")
    message_id: Optional[str] = Field(
        None, 
        description="Unique identifier for this message"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the response was generated"
    )
    remaining_quota: Optional[int] = Field(
        None,
        description="Remaining quota for the user, if applicable"
    )
    message_type: str = Field(
        "text",
        description="Type of the message (e.g., 'text', 'audio', 'error')"
    )
    audio_response: Optional[bytes] = Field(
        None,
        description="Binary audio data if the response includes speech"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional metadata for the response"
    )

    model_config = ConfigDict(
        from_attributes=True,
    )

class PronunciationFeedback(BaseModel):
    """Model for pronunciation assessment feedback."""
    overall_score: float = Field(
        ..., 
        ge=0, 
        le=100,
        description="Overall pronunciation score (0-100)"
    )
    accuracy_score: float = Field(
        ...,
        ge=0,
        le=100,
        description="Accuracy score (0-100)"
    )
    fluency_score: float = Field(
        ...,
        ge=0,
        le=100,
        description="Fluency score (0-100)"
    )
    completeness_score: float = Field(
        ...,
        ge=0,
        le=100,
        description="Completeness score (0-100)"
    )
    feedback: List[str] = Field(
        ...,
        description="Detailed feedback on pronunciation"
    )
    word_assessments: List[Dict[str, Any]] = Field(
        [],
        description="Detailed assessment of individual words"
    )
    transcript: str = Field(
        ...,
        description="The recognized text from the audio"
    )
    reference_text: str = Field(
        ...,
        description="The reference text that was spoken"
    )
    remaining_quota: Optional[int] = Field(
        None,
        description="Remaining pronunciation assessment quota"
    )

    model_config = ConfigDict(
        from_attributes=True,
    )

class WritingFeedbackInput(BaseModel):
    """Input model for writing feedback requests."""
    text: str = Field(..., description="The text to analyze")
    prompt: Optional[str] = Field(
        None,
        description="Optional writing prompt or instructions"
    )
    language: str = Field(
        "en",
        description="Language of the text (ISO 639-1 code)"
    )
    skill_level: Optional[str] = Field(
        None,
        description="The user's self-reported skill level (beginner, intermediate, advanced)"
    )
    context: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional context for the writing task"
    )

    model_config = ConfigDict(
        from_attributes=True,
    )

class WritingFeedback(BaseModel):
    """Model for writing feedback."""
    grammar_feedback: Optional[str] = Field(
        None,
        description="Feedback on grammar and spelling"
    )
    vocabulary_feedback: Optional[str] = Field(
        None,
        description="Feedback on vocabulary usage"
    )
    structure_feedback: Optional[str] = Field(
        None,
        description="Feedback on sentence and paragraph structure"
    )
    coherence_feedback: Optional[str] = Field(
        None,
        description="Feedback on coherence and cohesion"
    )
    task_achievement: Optional[str] = Field(
        None,
        description="Feedback on how well the task was achieved"
    )
    suggestions: List[str] = Field(
        [],
        description="Specific suggestions for improvement"
    )
    overall_score: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="Overall writing quality score (0-100)"
    )
    corrected_text: Optional[str] = Field(
        None,
        description="The corrected version of the input text"
    )
    remaining_quota: Optional[int] = Field(
        None,
        description="Remaining writing feedback quota"
    )
    raw_feedback: Optional[Dict[str, Any]] = Field(
        None,
        description="Raw feedback from the AI model"
    )

    model_config = ConfigDict(
        from_attributes=True,
    )

class LessonSessionCreate(BaseModel):
    """Model for creating a new lesson session."""
    lesson_id: int = Field(..., description="ID of the lesson")
    user_id: int = Field(..., description="ID of the user")
    status: str = Field("in_progress", description="Status of the session")
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional metadata for the session"
    )

    model_config = ConfigDict(
        from_attributes=True,
    )

class LessonSessionUpdate(BaseModel):
    """Model for updating a lesson session."""
    status: Optional[str] = Field(None, description="New status of the session")
    progress: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="Progress percentage (0-100)"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional metadata to update"
    )

    model_config = ConfigDict(
        from_attributes=True,
    )

class LessonSessionResponse(LessonSessionCreate):
    """Response model for lesson session operations."""
    id: int = Field(..., description="Unique identifier for the session")
    created_at: datetime = Field(..., description="When the session was created")
    updated_at: datetime = Field(..., description="When the session was last updated")
    progress: float = Field(0.0, description="Current progress percentage")

    model_config = ConfigDict(
        from_attributes=True,
    )

class ChatMessage(BaseModel):
    """Model for chat messages in the conversation history."""
    role: str = Field(..., description="Role of the message sender (user, assistant, system)")
    content: str = Field(..., description="The message content")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the message was sent"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional metadata for the message"
    )

    model_config = ConfigDict(
        from_attributes=True,
    )

class ConversationHistory(BaseModel):
    """Model for conversation history."""
    session_id: str = Field(..., description="ID of the conversation session")
    messages: List[ChatMessage] = Field(
        [],
        description="List of messages in the conversation"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the conversation was started"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the conversation was last updated"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional metadata for the conversation"
    )

    model_config = ConfigDict(
        from_attributes=True,
    )

class WebRTCOffer(BaseModel):
    """Model for WebRTC offer/answer exchange."""
    sdp: str = Field(..., description="The SDP message")
    type: str = Field(..., description="The type of SDP (offer/answer)")
    session_id: Optional[str] = Field(
        None,
        description="Session ID for the WebRTC connection"
    )

    model_config = ConfigDict(
        from_attributes=True,
    )

class WebRTCIceCandidate(BaseModel):
    """Model for WebRTC ICE candidates."""
    candidate: str = Field(..., description="The ICE candidate string")
    sdp_mid: Optional[str] = Field(
        None,
        description="The media stream identification"
    )
    sdp_mline_index: Optional[int] = Field(
        None,
        description="The index of the media description"
    )
    session_id: Optional[str] = Field(
        None,
        description="Session ID for the WebRTC connection"
    )

    model_config = ConfigDict(
        from_attributes=True,
    )

class WebRTCSessionCreate(BaseModel):
    """Model for creating a new WebRTC session."""
    user_id: int = Field(..., description="ID of the user")
    lesson_id: Optional[int] = Field(
        None,
        description="Optional lesson ID if this is part of a lesson"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional metadata for the session"
    )

    model_config = ConfigDict(
        from_attributes=True,
    )

class WebRTCSessionResponse(WebRTCSessionCreate):
    """Response model for WebRTC session operations."""
    id: str = Field(..., description="Unique identifier for the session")
    created_at: datetime = Field(..., description="When the session was created")
    status: str = Field(..., description="Current status of the session")
    metadata: Dict[str, Any] = Field(
        {},
        description="Additional metadata for the session"
    )

    model_config = ConfigDict(
        from_attributes=True,
    )
