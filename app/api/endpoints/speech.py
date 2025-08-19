from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from datetime import datetime
import os
import uuid

from app import crud, models, schemas
from app.api import deps
from app.services.pronunciation_service import pronunciation_analyzer
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

# Create uploads directory if it doesn't exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

@router.post("/pronunciation/analyze", response_model=schemas.PronunciationAnalysisResult)
async def analyze_pronunciation(
    *,
    audio_file: UploadFile = File(...),
    expected_text: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    Analyze pronunciation of spoken text
    
    - **audio_file**: Audio file containing speech (WAV format, max 10MB)
    - **expected_text**: The text that should have been spoken
    """
    # Check user's pronunciation analysis quota
    if not crud.user_ai_usage.has_quota(db, user_id=current_user.id, feature='pronunciation_analysis'):
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Pronunciation analysis quota exceeded. Please upgrade your plan."
        )
    
    try:
        # Validate file type
        if not audio_file.filename.lower().endswith('.wav'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only WAV audio files are supported"
            )
        
        # Save audio file temporarily
        file_ext = os.path.splitext(audio_file.filename)[1]
        filename = f"pronunciation_{current_user.id}_{int(datetime.utcnow().timestamp())}{file_ext}"
        file_path = os.path.join(settings.UPLOAD_DIR, filename)
        
        with open(file_path, "wb") as buffer:
            buffer.write(await audio_file.read())
        
        # Read the saved file
        with open(file_path, "rb") as f:
            audio_data = f.read()
        
        # Analyze pronunciation
        result = await pronunciation_analyzer.analyze_pronunciation(
            audio_data=audio_data,
            expected_text=expected_text,
            language='uz-UZ'
        )
        
        # Log the analysis
        crud.user_ai_usage.increment_usage(
            db, 
            user_id=current_user.id, 
            feature='pronunciation_analysis',
            amount=-1
        )
        
        # Clean up the temporary file
        try:
            os.remove(file_path)
        except Exception as e:
            logger.warning(f"Failed to delete temporary file {file_path}: {e}")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in pronunciation analysis: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing pronunciation: {str(e)}"
        )

@router.post("/pronunciation/practice", response_model=schemas.PronunciationPracticeSession)
async def create_practice_session(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    level: str = "beginner"
):
    """
    Create a new pronunciation practice session
    """
    # Get practice phrases based on user level
    phrases = crud.pronunciation_phrase.get_by_level(db, level=level, limit=5)
    
    if not phrases:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No practice phrases found for level: {level}"
        )
    
    # Create a new practice session
    session = crud.pronunciation_session.create_with_user(
        db=db,
        user_id=current_user.id,
        level=level,
        phrases=[p.id for p in phrases]
    )
    
    return {
        "session_id": session.id,
        "phrases": [{"id": p.id, "text": p.text} for p in phrases],
        "level": level,
        "created_at": session.created_at.isoformat()
    }

@router.get("/pronunciation/history", response_model=List[schemas.PronunciationHistoryItem])
async def get_pronunciation_history(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    skip: int = 0,
    limit: int = 10
):
    """
    Get user's pronunciation practice history
    """
    history = crud.pronunciation_history.get_by_user(
        db, 
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )
    
    return [
        {
            "id": item.id,
            "text": item.text,
            "score": item.score,
            "date": item.created_at.isoformat(),
            "feedback": item.feedback
        }
        for item in history
    ]
