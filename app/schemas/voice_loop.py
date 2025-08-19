from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

from .ai_feedback import AIFeedbackResponse


class VoiceLoopResponse(BaseModel):
    """Unified response for the voice loop orchestration (STT → AI → feedback → TTS)."""
    transcript: str = Field(..., description="Recognized text from user's audio (STT)")
    ai_text: str = Field(..., description="AI assistant's text response")
    corrections: List[str] = Field(default_factory=list, description="Grammar corrections suggested for user's response")
    advice: List[str] = Field(default_factory=list, description="Actionable next steps/advice for the user")
    audio_url: Optional[str] = Field(None, description="URL to the generated TTS audio for the AI response")
    feedback: Optional[AIFeedbackResponse] = Field(None, description="Full structured feedback payload")
    quotas: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Remaining relevant quotas after this request (stt, tts, ai)"
    )
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the orchestration was completed")

    model_config = ConfigDict(
        from_attributes=True,
    )
