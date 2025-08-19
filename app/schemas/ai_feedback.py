from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from datetime import datetime

class FeedbackType(str, Enum):
    """Types of feedback that can be requested"""
    GRAMMAR = "grammar"
    VOCABULARY = "vocabulary"
    PRONUNCIATION = "pronunciation"
    FLUENCY = "fluency"
    CONTENT = "content"
    ALL = "all"

class BaseFeedback(BaseModel):
    """Base feedback model with common fields"""
    score: float = Field(..., ge=0, le=100, description="Score from 0 to 100")
    feedback: str = Field(..., description="Detailed feedback")

    class Config:
        from_attributes = True

class GrammarFeedback(BaseFeedback):
    """Feedback specific to grammar"""
    corrections: List[str] = Field(
        default_factory=list,
        description="List of grammar corrections"
    )
    error_types: Optional[Dict[str, int]] = Field(
        None,
        description="Count of different types of grammar errors"
    )

    model_config = ConfigDict(
        from_attributes=True,
    )

class VocabularyFeedback(BaseFeedback):
    """Feedback specific to vocabulary usage"""
    suggestions: List[str] = Field(
        default_factory=list,
        description="Suggested vocabulary improvements"
    )
    advanced_words: List[str] = Field(
        default_factory=list,
        description="Advanced vocabulary used correctly"
    )
    misused_words: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Words that were misused with suggested corrections"
    )

    model_config = ConfigDict(
        from_attributes=True,
    )

class PronunciationFeedback(BaseFeedback):
    """Feedback specific to pronunciation"""
    tips: List[str] = Field(
        default_factory=list,
        description="Tips for improving pronunciation"
    )
    problem_sounds: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Specific sounds that need improvement"
    )
    stress_patterns: Optional[List[str]] = Field(
        None,
        description="Notes on word/sentence stress patterns"
    )

    model_config = ConfigDict(
        from_attributes=True,
    )

class FluencyFeedback(BaseFeedback):
    """Feedback specific to fluency"""
    suggestions: List[str] = Field(
        default_factory=list,
        description="Suggestions for improving fluency"
    )
    pace: Optional[str] = Field(
        None,
        description="Assessment of speaking pace (too fast, too slow, just right)"
    )
    hesitation_markers: Optional[List[str]] = Field(
        None,
        description="Noted hesitation markers (um, uh, etc.)"
    )

    model_config = ConfigDict(
        from_attributes=True,
    )

class OverallFeedback(BaseFeedback):
    """Overall feedback and next steps"""
    next_steps: List[str] = Field(
        default_factory=list,
        description="Recommended next steps for improvement"
    )
    strengths: List[str] = Field(
        default_factory=list,
        description="Notable strengths in the response"
    )
    areas_for_improvement: List[str] = Field(
        default_factory=list,
        description="Key areas that need improvement"
    )

    model_config = ConfigDict(
        from_attributes=True,
    )

class AIFeedbackRequest(BaseModel):
    """Request model for getting AI feedback"""
    user_response: str = Field(..., description="The user's response to evaluate")
    reference_text: Optional[str] = Field(
        None,
        description="Reference or expected response (if applicable)"
    )
    context: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional context for the feedback"
    )
    feedback_types: List[FeedbackType] = Field(
        default_factory=lambda: [FeedbackType.ALL],
        description="Types of feedback to include"
    )
    language: str = Field(
        "en-US",
        description="Language code for the response"
    )

    model_config = ConfigDict(
        from_attributes=True,
    )

class AIFeedbackResponse(BaseModel):
    """Response model for AI feedback"""
    feedback_id: str = Field(..., description="Unique identifier for this feedback")
    timestamp: datetime = Field(..., description="When the feedback was generated")
    grammar: GrammarFeedback = Field(..., description="Grammar feedback")
    vocabulary: VocabularyFeedback = Field(..., description="Vocabulary feedback")
    pronunciation: PronunciationFeedback = Field(..., description="Pronunciation feedback")
    fluency: FluencyFeedback = Field(..., description="Fluency feedback")
    overall: OverallFeedback = Field(..., description="Overall feedback and next steps")
    audio_feedback_url: Optional[HttpUrl] = Field(
        None,
        description="URL to audio version of the feedback (if available)"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata about the feedback"
    )

    model_config = ConfigDict(
        from_attributes=True,
    )
