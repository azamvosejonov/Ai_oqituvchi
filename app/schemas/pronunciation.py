from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, HttpUrl, ConfigDict

class PronunciationWordAssessment(BaseModel):
    """Detailed assessment for a single word"""
    word: str = Field(..., description="The recognized word")
    accuracy_score: float = Field(..., ge=0, le=100, description="Accuracy score (0-100)")
    error_type: Optional[str] = Field(None, description="Type of error if any")
    syllables: Optional[List[Dict[str, Any]]] = Field(None, description="Syllable-level assessment")

    class Config:
        from_attributes = True

class PronunciationFeedback(BaseModel):
    """Detailed feedback on pronunciation"""
    overall_score: float = Field(..., ge=0, le=100, description="Overall pronunciation score (0-100)")
    feedback: str = Field(..., description="Human-readable feedback")
    areas_for_improvement: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Specific areas that need improvement"
    )

    model_config = ConfigDict(
        from_attributes=True,
    )

class PronunciationAssessmentRequest(BaseModel):
    """Request model for pronunciation assessment"""
    audio: bytes = Field(..., description="Audio file in WAV format")
    reference_text: str = Field(..., description="Expected text for assessment")
    language: str = Field("en-US", description="Language code (e.g., en-US, ru-RU, uz-Latn-UZ)")
    enable_miscue: bool = Field(True, description="Whether to detect miscues (mispronunciations)")

    model_config = ConfigDict(
        from_attributes=True,
    )

class PronunciationAssessmentResponse(BaseModel):
    """Response model for pronunciation assessment"""
    text: str = Field(..., description="Recognized text from speech")
    assessment: Dict[str, Any] = Field(
        ...,
        description="Detailed assessment results including scores and word-level details"
    )
    feedback: PronunciationFeedback = Field(
        ...,
        description="Structured feedback on pronunciation"
    )
    audio_url: Optional[HttpUrl] = Field(
        None,
        description="URL to the processed audio with feedback (if available)"
    )

    model_config = ConfigDict(
        from_attributes=True,
    )

class PronunciationExercise(BaseModel):
    """Model for a pronunciation exercise"""
    id: str = Field(..., description="Unique identifier for the exercise")
    title: str = Field(..., description="Title of the exercise")
    description: Optional[str] = Field(None, description="Description of the exercise")
    reference_text: str = Field(..., description="Text to be pronounced")
    language: str = Field("en-US", description="Language code")
    difficulty: str = Field("beginner", description="Difficulty level (beginner, intermediate, advanced)")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    sample_audio_url: Optional[HttpUrl] = Field(None, description="URL to sample pronunciation")
    min_accuracy: float = Field(70.0, description="Minimum accuracy score to pass")
    min_fluency: float = Field(70.0, description="Minimum fluency score to pass")
    min_completeness: float = Field(70.0, description="Minimum completeness score to pass")

    model_config = ConfigDict(
        from_attributes=True,
    )
