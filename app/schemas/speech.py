from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class PronunciationMistake(BaseModel):
    """Represents a pronunciation mistake found during analysis"""
    word: str = Field(..., description="The word with the mistake")
    expected: str = Field(..., description="The expected pronunciation")
    actual: str = Field(..., description="The actual pronunciation")
    error_type: str = Field(..., description="Type of error (omission, insertion, substitution, mispronunciation)")
    confidence: float = Field(..., description="Confidence score (0-1) of the detected mistake")
    suggested_correction: str = Field(..., description="Suggested correction")

    model_config = ConfigDict(
        from_attributes=True,
    )

class PronunciationAnalysisResult(BaseModel):
    """Result of pronunciation analysis"""
    success: bool = Field(..., description="Whether the analysis was successful")
    score: float = Field(..., ge=0, le=100, description="Pronunciation score (0-100)")
    recognized_text: str = Field(..., description="The recognized text from speech")
    expected_text: str = Field(..., description="The expected text")
    mistakes: List[Dict[str, Any]] = Field(..., description="List of pronunciation mistakes")
    feedback: str = Field(..., description="Human-readable feedback")

    model_config = ConfigDict(
        from_attributes=True,
    )

class PronunciationPhraseBase(BaseModel):
    """Base model for pronunciation practice phrases"""
    text: str = Field(..., description="The phrase text")
    level: str = Field(..., description="Difficulty level (beginner, intermediate, advanced)")
    category: Optional[str] = Field(None, description="Optional category for the phrase")

    model_config = ConfigDict(
        from_attributes=True,
    )

class PronunciationPhraseCreate(PronunciationPhraseBase):
    """Model for creating a new pronunciation phrase"""
    pass

class PronunciationPhrase(PronunciationPhraseBase):
    """Full pronunciation phrase model with ID"""
    id: int

    model_config = ConfigDict(
        from_attributes=True,
    )

class PronunciationSessionBase(BaseModel):
    """Base model for pronunciation practice sessions"""
    user_id: int = Field(..., description="User ID who owns the session")
    level: str = Field(..., description="Difficulty level")
    phrases: List[int] = Field(..., description="List of phrase IDs in this session")

    model_config = ConfigDict(
        from_attributes=True,
    )

class PronunciationSessionCreate(PronunciationSessionBase):
    """Model for creating a new pronunciation practice session"""
    pass

class PronunciationSession(PronunciationSessionBase):
    """Full pronunciation session model with ID and timestamps"""
    id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )

class PronunciationHistoryItem(BaseModel):
    """Item in pronunciation practice history"""
    id: int
    text: str
    score: float
    date: str
    feedback: str

    model_config = ConfigDict(
        from_attributes=True,
    )

class PronunciationPracticeSession(BaseModel):
    """Pronunciation practice session with phrases"""
    session_id: int
    phrases: List[Dict[str, str]]
    level: str
    created_at: str

    model_config = ConfigDict(
        from_attributes=True,
    )

class SpeechToTextRequest(BaseModel):
    """Request model for speech-to-text conversion"""
    audio_data: str = Field(..., description="Base64 encoded audio data")
    language: str = Field(default="uz-UZ", description="Language code (default: uz-UZ)")

    model_config = ConfigDict(
        from_attributes=True,
    )

class TextToSpeechRequest(BaseModel):
    """Request model for text-to-speech conversion"""
    text: str = Field(..., description="Text to convert to speech")
    voice: str = Field(default="uz-UZ-Standard-A", description="Voice to use for speech synthesis")
    speed: float = Field(default=1.0, ge=0.25, le=4.0, description="Speech rate (0.25-4.0)")

    model_config = ConfigDict(
        from_attributes=True,
    )

class SpeechToTextResponse(BaseModel):
    """Response model for speech-to-text conversion"""
    text: str = Field(..., description="Recognized text")
    confidence: float = Field(..., description="Confidence score (0-1)")

    model_config = ConfigDict(
        from_attributes=True,
    )

class TextToSpeechResponse(BaseModel):
    """Response model for text-to-speech conversion"""
    audio_data: str = Field(..., description="Base64 encoded audio data")
    content_type: str = Field(..., description="MIME type of the audio")
    voice: str = Field(..., description="Voice used for synthesis")

    model_config = ConfigDict(
        from_attributes=True,
    )
