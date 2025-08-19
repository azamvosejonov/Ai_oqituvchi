import logging
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import json

from app import models
from app.api import deps
from app.core.config import settings
from app.services.stt_service import stt_service
from app.crud import crud_user_ai_usage
from app.models.ai_usage import AIFeatureType

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/transcribe")
async def transcribe_audio(
    audio_file: UploadFile = File(..., description="Audio file to transcribe"),
    language_code: str = Form("uz-UZ", description="Language code (e.g., uz-UZ, en-US)"),
    enable_automatic_punctuation: bool = Form(True, description="Whether to automatically add punctuation"),
    enable_speaker_diarization: bool = Form(False, description="Whether to include speaker diarization"),
    speaker_count: Optional[int] = Form(None, description="Number of speakers in the audio (if known)"),
    model: str = Form("default", description="STT model to use (e.g., 'default', 'video', 'phone_call')"),
    use_enhanced: bool = Form(False, description="Whether to use enhanced model (may improve accuracy but costs more)"),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    Transcribe speech from an audio file to text.
    
    This endpoint uses Google Cloud Speech-to-Text to convert the provided audio
    into text in the specified language.
    """
    # Check if STT service is available
    if not stt_service.is_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Speech-to-text service is currently unavailable"
        )
    
    # Check user's STT quota if not admin
    if not current_user.is_superuser:
        # Check if user has exceeded their STT quota
        usage = crud_user_ai_usage.user_ai_usage.get_usage(
            db, 
            user_id=current_user.id, 
            feature_type=AIFeatureType.STT
        )
        
        if usage.remaining_quota <= 0:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="You have exceeded your STT quota. Please upgrade to premium for more."
            )
    
    try:
        # Configure recognition settings
        config = {
            "language_code": language_code,
            "enable_automatic_punctuation": enable_automatic_punctuation,
            "enable_speaker_diarization": enable_speaker_diarization,
            "model": model,
            "use_enhanced": use_enhanced
        }
        
        if enable_speaker_diarization and speaker_count:
            config["speaker_count"] = speaker_count
        
        # Transcribe the audio
        result = await stt_service.transcribe_audio(audio_file, **config)
        
        # Log the usage if not admin
        if not current_user.is_superuser:
            # Estimate characters processed (approximate)
            characters_used = len(result.get("transcript", ""))
            crud_user_ai_usage.user_ai_usage.increment_usage(
                db,
                user_id=current_user.id,
                feature_type=AIFeatureType.STT,
                characters_used=characters_used
            )
            
            # Add remaining quota to response
            result["remaining_quota"] = usage.remaining_quota - characters_used
        else:
            result["remaining_quota"] = "unlimited"
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Error transcribing audio: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to transcribe audio: {str(e)}"
        )

@router.post("/pronunciation-assessment")
async def assess_pronunciation(
    audio_file: UploadFile = File(..., description="Audio file to assess"),
    reference_text: str = Form(..., description="Reference text for pronunciation assessment"),
    language_code: str = Form("uz-UZ", description="Language code (e.g., uz-UZ, en-US)"),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    Assess pronunciation quality from an audio file.
    
    This endpoint evaluates the pronunciation of the provided audio against
    the reference text and provides a detailed assessment.
    """
    # Check if STT service is available
    if not stt_service.is_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Speech-to-text service is currently unavailable"
        )
    
    # Check user's STT quota if not admin
    if not current_user.is_superuser:
        # Check if user has exceeded their STT quota
        usage = crud_user_ai_usage.user_ai_usage.get_usage(
            db, 
            user_id=current_user.id, 
            feature_type=AIFeatureType.PRONUNCIATION_ASSESSMENT
        )
        
        if usage.remaining_quota <= 0:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="You have exceeded your pronunciation assessment quota. Please upgrade to premium for more."
            )
    
    try:
        # Configure pronunciation assessment
        config = {
            "language_code": language_code,
            "reference_text": reference_text
        }
        
        # Assess pronunciation
        result = await stt_service.assess_pronunciation(audio_file, **config)
        
        # Log the usage if not admin
        if not current_user.is_superuser:
            # Estimate characters processed (approximate)
            characters_used = len(reference_text)
            crud_user_ai_usage.user_ai_usage.increment_usage(
                db,
                user_id=current_user.id,
                feature_type=AIFeatureType.PRONUNCIATION_ASSESSMENT,
                characters_used=characters_used
            )
            
            # Add remaining quota to response
            result["remaining_quota"] = usage.remaining_quota - characters_used
        else:
            result["remaining_quota"] = "unlimited"
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Error assessing pronunciation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to assess pronunciation: {str(e)}"
        )

@router.get("/languages")
async def list_supported_languages(
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    List supported languages for speech-to-text.
    
    Returns a list of language codes and their corresponding language names
    that are supported for speech recognition.
    """
    if not stt_service.is_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Speech-to-text service is currently unavailable"
        )
    
    try:
        languages = stt_service.list_supported_languages()
        return {"languages": languages}
    except Exception as e:
        logger.error(f"Error listing supported languages: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve supported languages"
        )
