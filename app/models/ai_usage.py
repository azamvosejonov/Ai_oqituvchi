from enum import Enum

class AIFeatureType(str, Enum):
    """Enum for different types of AI features that consume user quotas."""
    CHAT = "chat"
    VOICE_CHAT = "voice_chat"
    TTS = "tts"
    STT = "stt"
    PRONUNCIATION_ASSESSMENT = "pronunciation_assessment"
    WRITING_FEEDBACK = "writing_feedback"
