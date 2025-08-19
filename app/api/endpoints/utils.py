from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
import io
import os
import tempfile
from app import schemas
from app.api import deps
from app.core.config import settings
from app.services.ai.tts import tts_service

router = APIRouter()

@router.get("/healthcheck", tags=["Utils"])
def healthcheck():
    return {"status": "ok"}

@router.get("/settings")
def get_settings() -> Dict[str, Any]:
    """
    Get public application settings.
    """
    return {
        "app_name": settings.PROJECT_NAME,
        "debug": settings.DEBUG,
        "environment": settings.ENVIRONMENT,
    }

@router.get("/version")
def get_version() -> Dict[str, str]:
    """
    Get the current API version.
    """
    return {"version": settings.API_V1_STR}

@router.get("/tts-preview", tags=["Utils"])
async def tts_preview(
    text: str,
    voice_id: str = "uz-UZ-MadinaNeural",
    language: str = "uz-UZ",
    gender: str = "female"
):
    try:
        audio_data = await tts_service.synthesize(
            text=text, voice_id=voice_id, language=language, gender=gender
        )
        return StreamingResponse(io.BytesIO(audio_data), media_type="audio/mpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/audio/temp/{filename}", tags=["Utils"])
async def get_temp_audio(filename: str):
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Audio file not found")

    return FileResponse(file_path, media_type="audio/mpeg")

# Add more utility endpoints as needed
