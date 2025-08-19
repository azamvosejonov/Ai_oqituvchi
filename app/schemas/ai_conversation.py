from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from enum import Enum
from pydantic import BaseModel, Field, HttpUrl, ConfigDict

class VoiceGender(str, Enum):
    """Gender options for TTS voices"""
    MALE = "male"
    FEMALE = "female"
    NEUTRAL = "neutral"

class AudioFormat(str, Enum):
    """Supported audio formats"""
    MP3 = "mp3"
    WAV = "wav"
    PCM = "pcm"
    OGG = "ogg"
    WEBM = "webm"

class VoiceSettings(BaseModel):
    """Voice settings for TTS"""
    voice_id: Optional[str] = Field(
        None,
        description="Specific voice ID to use (e.g., 'en-US-GuyNeural')"
    )
    language: str = Field(
        "en-US",
        description="Language code (e.g., 'en-US', 'ru-RU')",
        min_length=2,
        max_length=10
    )
    gender: VoiceGender = Field(
        VoiceGender.MALE,
        description="Voice gender"
    )
    speaking_rate: float = Field(
        1.0,
        description="Speaking rate (0.5 to 2.0)",
        ge=0.5,
        le=2.0
    )
    pitch: float = Field(
        1.0,
        description="Voice pitch (0.5 to 2.0)",
        ge=0.5,
        le=2.0
    )
    volume: float = Field(
        1.0,
        description="Volume level (0.0 to 2.0)",
        ge=0.0,
        le=2.0
    )
    audio_format: AudioFormat = Field(
        AudioFormat.MP3,
        description="Output audio format"
    )

    model_config = ConfigDict(
        from_attributes=True,
    )

class ConversationRequest(BaseModel):
    """Request model for continuing a conversation"""
    conversation_id: Optional[str] = Field(
        None,
        description="Existing conversation ID. If not provided, a new conversation will be started."
    )
    audio_data: bytes = Field(
        ...,
        description="Audio data in WAV format containing the user's speech"
    )
    text: Optional[str] = Field(
        None,
        description="Optional text transcription of the audio. If not provided, the audio will be transcribed automatically."
    )
    language: str = Field(
        "en-US",
        description="Language code for speech recognition"
    )
    settings: Optional[VoiceSettings] = Field(
        None,
        description="Voice settings for the AI's response. If not provided, defaults will be used."
    )

    model_config = ConfigDict(
        from_attributes=True,
    )

class PronunciationFeedback(BaseModel):
    """Pronunciation feedback for a word or phrase"""
    text: str = Field(..., description="The word or phrase being analyzed")
    score: float = Field(
        ...,
        description="Pronunciation score (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )
    feedback: str = Field(
        ...,
        description="Human-readable feedback about the pronunciation"
    )
    phonemes: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Detailed phoneme-level analysis"
    )

    model_config = ConfigDict(
        from_attributes=True,
    )

class ConversationResponse(BaseModel):
    """Response model for conversation endpoints"""
    text_response: str = Field(
        ...,
        description="The AI's text response"
    )
    audio_response: Optional[bytes] = Field(
        None,
        description="Audio data of the AI's response in the requested format"
    )
    audio_url: Optional[HttpUrl] = Field(
        None,
        description="URL to the audio file (if not embedded in the response)"
    )
    conversation_id: str = Field(
        ...,
        description="Unique identifier for the conversation"
    )
    settings: VoiceSettings = Field(
        ...,
        description="Voice settings used for the response"
    )
    pronunciation_feedback: Optional[PronunciationFeedback] = Field(
        None,
        description="Feedback on the user's pronunciation (if applicable)"
    )
    suggested_responses: List[str] = Field(
        default_factory=list,
        description="List of suggested responses the user might want to say next"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata about the response"
    )

    model_config = ConfigDict(
        from_attributes=True,
    )

class ConversationHistory(BaseModel):
    """Model representing a past conversation"""
    id: str = Field(..., description="Unique identifier for the conversation")
    title: str = Field(..., description="Title or first few words of the conversation")
    created_at: datetime = Field(..., description="When the conversation started")
    updated_at: datetime = Field(..., description="When the conversation was last updated")
    message_count: int = Field(..., description="Number of messages in the conversation")
    language: str = Field(..., description="Language code of the conversation")
    tags: List[str] = Field(
        default_factory=list,
        description="Tags for categorizing the conversation"
    )

    model_config = ConfigDict(
        from_attributes=True,
    )

class LanguageInfo(BaseModel):
    """Information about a supported language"""
    code: str = Field(..., description="Language code (e.g., 'en-US')")
    name: str = Field(..., description="Full language name (e.g., 'English (United States)')")
    native_name: Optional[str] = Field(
        None,
        description="Name of the language in its own script"
    )

    model_config = ConfigDict(
        from_attributes=True,
    )

class VoiceInfo(BaseModel):
    """Information about an available TTS voice"""
    id: str = Field(..., description="Unique voice ID")
    name: str = Field(..., description="Display name of the voice")
    language: str = Field(..., description="Language code")
    gender: VoiceGender = Field(..., description="Gender of the voice")
    sample_url: Optional[HttpUrl] = Field(
        None,
        description="URL to a sample of the voice"
    )
    is_neural: bool = Field(
        True,
        description="Whether this is a neural voice (if applicable)"
    )

    model_config = ConfigDict(
        from_attributes=True,
    )

class AvailableVoicesResponse(BaseModel):
    """Response model for available voices endpoint"""
    languages: List[LanguageInfo] = Field(
        ...,
        description="List of supported languages"
    )
    voices: List[VoiceInfo] = Field(
        ...,
        description="List of available voices"
    )
    default_language: str = Field(
        "en-US",
        description="Default language code"
    )
    default_voice: str = Field(
        "en-US-GuyNeural",
        description="Default voice ID"
    )

    model_config = ConfigDict(
        from_attributes=True,
    )

class TranscribeResponse(BaseModel):
    """Response model for speech-to-text transcription"""
    text: str = Field(..., description="Transcribed text")
    confidence: float = Field(
        ...,
        description="Confidence score (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )
    language: str = Field(..., description="Detected language code")
    words: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Word-level timing and confidence information"
    )

    model_config = ConfigDict(
        from_attributes=True,
    )

class SynthesizeRequest(BaseModel):
    """Request model for text-to-speech synthesis"""
    text: str = Field(..., description="Text to synthesize")
    voice_id: Optional[str] = Field(
        None,
        description="Voice ID to use. If not provided, a default will be chosen based on the language."
    )
    language: str = Field(
        "en-US",
        description="Language code"
    )
    gender: VoiceGender = Field(
        VoiceGender.MALE,
        description="Voice gender"
    )
    format: AudioFormat = Field(
        AudioFormat.MP3,
        description="Output audio format"
    )
    speaking_rate: Optional[float] = Field(
        None,
        description="Speaking rate (0.5 to 2.0)",
        ge=0.5,
        le=2.0
    )
    pitch: Optional[float] = Field(
        None,
        description="Voice pitch (0.5 to 2.0)",
        ge=0.5,
        le=2.0
    )
    volume: Optional[float] = Field(
        None,
        description="Volume level (0.0 to 2.0)",
        ge=0.0,
        le=2.0
    )

    model_config = ConfigDict(
        from_attributes=True,
    )
