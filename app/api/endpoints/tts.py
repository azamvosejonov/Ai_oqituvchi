import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import io

from app import models
from app.api import deps
from app.core.config import settings
from app.services.tts_service import tts_service
from app.crud import crud_user_ai_usage
from app.models.ai_usage import AIFeatureType

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/synthesize")
async def synthesize_speech(
    text: str = Query(..., min_length=1, max_length=5000, description="Text to convert to speech"),
    language_code: str = Query("uz-UZ", description="Language code (e.g., uz-UZ, en-US)"),
    voice_name: Optional[str] = Query(None, description="Specific voice name to use"),
    speaking_rate: float = Query(1.0, ge=0.25, le=4.0, description="Speaking rate/speed (0.25 to 4.0)"),
    pitch: float = Query(0.0, ge=-20.0, le=20.0, description="Pitch adjustment (-20.0 to 20.0)"),
    volume_gain_db: float = Query(0.0, ge=-96.0, le=16.0, description="Volume gain in dB (-96.0 to 16.0)"),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    Convert text to speech and return the audio file.
    
    This endpoint uses Google Cloud Text-to-Speech to convert the provided text
    into natural-sounding speech in the specified language and voice.
    """
    # Check if TTS service is available
    if not tts_service.is_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Text-to-speech service is currently unavailable"
        )
    
    # Check user's TTS quota if not admin
    if not current_user.is_superuser:
        # Check if user has exceeded their TTS quota
        usage = crud_user_ai_usage.user_ai_usage.get_usage(
            db, 
            user_id=current_user.id, 
            feature_type=AIFeatureType.TTS
        )
        
        if usage.remaining_quota <= 0:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="You have exceeded your TTS quota. Please upgrade to premium for more."
            )
    
    try:
        # Configure voice parameters
        voice_config = {
            "language_code": language_code,
            "speaking_rate": speaking_rate,
            "pitch": pitch,
            "volume_gain_db": volume_gain_db
        }
        
        if voice_name:
            voice_config["name"] = voice_name
        
        # Generate speech
        audio_content = tts_service.synthesize_speech(text, **voice_config)
        
        # Log the usage if not admin
        if not current_user.is_superuser:
            crud_user_ai_usage.user_ai_usage.increment_usage(
                db,
                user_id=current_user.id,
                feature_type=AIFeatureType.TTS,
                characters_used=len(text)
            )
        
        # Return the audio file
        return StreamingResponse(
            io.BytesIO(audio_content),
            media_type="audio/mp3",
            headers={
                "Content-Disposition": f"attachment; filename=speech.mp3",
                "X-Characters-Used": str(len(text)),
                "X-Remaining-Quota": str(usage.remaining_quota - len(text)) if not current_user.is_superuser else "unlimited"
            }
        )
        
    except Exception as e:
        logger.error(f"Error synthesizing speech: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to synthesize speech: {str(e)}"
        )

@router.get("/voices")
async def list_available_voices(
    language_code: Optional[str] = Query(None, description="Filter voices by language code (e.g., 'uz', 'en')"),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    List available voices for text-to-speech.
    
    Returns a list of available voices that can be used for text-to-speech synthesis.
    """
    if not tts_service.is_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Text-to-speech service is currently unavailable"
        )
    
    try:
        voices = tts_service.list_voices(language_code=language_code)
        return {"voices": voices}
    except Exception as e:
        logger.error(f"Error listing available voices: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve available voices"
        )
