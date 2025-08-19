from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import JSONResponse, StreamingResponse
from typing import Optional, Dict, Any, List
import logging
import io
import json

from app.core.security import get_current_active_user
from app.models.user import User
from app.schemas.ai_conversation import (
    ConversationRequest,
    ConversationResponse,
    PronunciationFeedback,
    ConversationHistory,
    VoiceSettings
)
from app.services.ai.conversation_service import conversation_service
from app.services.ai.stt import stt_service
from app.services.ai.tts import tts_service, AudioFormat, VoiceGender

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/conversation/start", response_model=ConversationResponse)
async def start_conversation(
    settings: Optional[VoiceSettings] = None,
    current_user: User = Depends(get_current_active_user)
):
    """
    Start a new conversation with the AI tutor.
    
    Args:
        settings: Optional voice and language settings
        current_user: The authenticated user
        
    Returns:
        Initial conversation response with welcome message
    """
    try:
        # Default settings if not provided
        if not settings:
            settings = VoiceSettings()
        
        # Generate welcome message
        welcome_text = (
            f"Hello {current_user.full_name or 'there'}! I'm your English tutor. "
            "How can I help you practice today?"
        )
        
        # Convert text to speech
        audio_data = await tts_service.synthesize(
            text=welcome_text,
            voice_id=settings.voice_id,
            language=settings.language,
            gender=settings.gender,
            format=settings.audio_format
        )
        
        # Create response
        response = ConversationResponse(
            text_response=welcome_text,
            audio_response=audio_data,
            conversation_id=f"conv_{current_user.id}_{int(time.time())}",
            settings=settings,
            suggested_responses=[
                "Let's practice introductions",
                "Can you help me with pronunciation?",
                "I want to talk about travel"
            ]
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error starting conversation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not start conversation"
        )

@router.post("/conversation/continue", response_model=ConversationResponse)
async def continue_conversation(
    request: ConversationRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Continue an existing conversation with the AI tutor.
    
    Args:
        request: The conversation request with user input
        current_user: The authenticated user
        
    Returns:
        AI response with text and audio
    """
    try:
        # Process the user's message
        response = await conversation_service.process_audio_input(
            user_id=str(current_user.id),
            audio_data=request.audio_data,
            conversation_id=request.conversation_id
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error continuing conversation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not process conversation"
        )

@router.post("/conversation/transcribe", response_model=Dict[str, str])
async def transcribe_audio(
    audio_file: UploadFile = File(...),
    language: str = "en-US",
    current_user: User = Depends(get_current_active_user)
):
    """
    Transcribe audio to text.
    
    Args:
        audio_file: The audio file to transcribe
        language: The language of the audio
        current_user: The authenticated user
        
    Returns:
        The transcribed text
    """
    try:
        # Read audio file
        audio_data = await audio_file.read()
        
        # Transcribe
        text, confidence = await stt_service.transcribe(
            audio_data=audio_data,
            language=language
        )
        
        return {
            "text": text,
            "confidence": confidence,
            "language": language
        }
        
    except Exception as e:
        logger.error(f"Error transcribing audio: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not transcribe audio"
        )

@router.post("/conversation/synthesize", response_class=StreamingResponse)
async def synthesize_speech(
    text: str,
    voice_id: Optional[str] = None,
    language: str = "en-US",
    gender: VoiceGender = VoiceGender.MALE,
    format: AudioFormat = AudioFormat.MP3,
    current_user: User = Depends(get_current_active_user)
):
    """
    Convert text to speech.
    
    Args:
        text: The text to convert to speech
        voice_id: Optional specific voice ID
        language: The language of the text
        gender: The gender of the voice
        format: The audio format
        current_user: The authenticated user
        
    Returns:
        Audio data in the specified format
    """
    try:
        # Synthesize speech
        audio_data = await tts_service.synthesize(
            text=text,
            voice_id=voice_id,
            language=language,
            gender=gender,
            format=format
        )
        
        # Determine content type based on format
        content_type = f"audio/{format.value}"
        
        # Return as streaming response
        return StreamingResponse(
            io.BytesIO(audio_data),
            media_type=content_type,
            headers={
                "Content-Disposition": f"attachment; filename=speech.{format.value}",
                "Content-Length": str(len(audio_data))
            }
        )
        
    except Exception as e:
        logger.error(f"Error synthesizing speech: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not synthesize speech"
        )

@router.get("/conversation/history", response_model=List[ConversationHistory])
async def get_conversation_history(
    limit: int = 10,
    offset: int = 0,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get the user's conversation history.
    
    Args:
        limit: Maximum number of conversations to return
        offset: Number of conversations to skip
        current_user: The authenticated user
        
    Returns:
        List of past conversations
    """
    try:
        # In a real implementation, this would query the database
        # For now, return an empty list as a placeholder
        return []
        
    except Exception as e:
        logger.error(f"Error fetching conversation history: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not fetch conversation history"
        )

@router.get("/voices", response_model=Dict[str, Any])
async def get_available_voices():
    """
    Get a list of available voices and languages.
    
    Returns:
        Dictionary of available voices and languages
    """
    try:
        # Get supported languages from STT
        stt_languages = stt_service.get_supported_languages()
        
        # In a real implementation, you might want to combine this with
        # available TTS voices from your TTS service
        
        return {
            "stt_languages": stt_languages,
            "tts_voices": {
                "en-US": ["en-US-GuyNeural", "en-US-JennyNeural", "en-US-AriaNeural"],
                "ru-RU": ["ru-RU-DmitryNeural", "ru-RU-SvetlanaNeural"],
                "uz-UZ": ["uz-UZ-SardorNeural", "uz-UZ-MadinaNeural"],
                "tr-TR": ["tr-TR-AhmetNeural", "tr-TR-EmelNeural"]
            },
            "default_language": "en-US",
            "default_voice": "en-US-GuyNeural"
        }
        
    except Exception as e:
        logger.error(f"Error fetching available voices: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not fetch available voices"
        )
