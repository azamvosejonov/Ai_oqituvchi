from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List

class AIQuestion(BaseModel):
    """Schema for asking a text-based question to the AI."""
    prompt: str

    class Config:
        from_attributes = True
        model_config = ConfigDict(from_attributes=True)

class STTResponse(BaseModel):
    """Schema for the response from the Speech-to-Text endpoint."""
    text: str

    class Config:
        from_attributes = True
        model_config = ConfigDict(from_attributes=True)

class TTSRequest(BaseModel):
    """Schema for the request to the Text-to-Speech endpoint."""
    text: str
    language: str = "en-US"

    class Config:
        from_attributes = True
        model_config = ConfigDict(from_attributes=True)

class AIPronunciationAssessment(BaseModel):
    """Schema for the AI pronunciation assessment response."""
    accuracy_score: float = Field(..., ge=0, le=100)
    reference_text: str
    transcribed_text: str
    error: Optional[str] = None

    class Config:
        from_attributes = True
        model_config = ConfigDict(from_attributes=True)
