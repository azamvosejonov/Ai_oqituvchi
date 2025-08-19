"""
Talaffuzni baholash uchun API endpointlari.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import Optional, Dict, Any

from app.api.deps import get_current_active_user
from app.models.user import User
from app.services.ai.pronunciation_service import pronunciation_service
from app.schemas.pronunciation import PronunciationAssessmentResponse

router = APIRouter()

@router.post("/assess", response_model=PronunciationAssessmentResponse)
async def assess_pronunciation_endpoint(
    reference_text: str = Form(..., description="To'g'ri talaffuz qilinishi kerak bo'lgan matn"),
    audio_file: UploadFile = File(..., description="Tekshirish uchun audio fayl (WAV, MP3, etc.)"),
    current_user: User = Depends(get_current_active_user)
):
    """Audio fayl orqali talaffuzni baholash.
    
    Foydalanuvchi tomonidan yuborilgan audio faylni mos yozuv matni bilan solishtirib,
    talaffuzni baholaydi.
    """
    if not audio_file.content_type.startswith('audio/'):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an audio file.")

    try:
        # To'g'ridan-to'g'ri servisga audio faylni yuborish
        assessment_result = await pronunciation_service.assess_pronunciation(
            audio_file=audio_file,
            reference_text=reference_text
        )
        
        if assessment_result.get("error"):
            raise HTTPException(status_code=503, detail=assessment_result["error"])

        return assessment_result

    except Exception as e:
        # Log the exception here
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.post("/evaluate-text", response_model=Dict[str, Any])
async def evaluate_pronunciation_from_text(
    reference_text: str = Form(..., description="To'g'ri talaffuz qilinishi kerak bo'lgan matn"),
    recognized_text: str = Form(..., description="Foydalanuvchi tomonidan yozilgan yoki aytilgan matn"),
    current_user: User = Depends(get_current_active_user)
):
    """Matn orqali talaffuzni baholash.
    
    Bu endpoint audio fayl orqali emas, balki to'g'ridan-to'g'ri matn orqali
    talaffuzni baholash uchun ishlatiladi.
    """
    try:
        # Talaffuzni baholash
        result = pronunciation_service.evaluate_pronunciation(
            reference_text=reference_text,
            recognized_text=recognized_text
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Talaffuz muvaffaqiyatli baholandi"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Talaffuzni baholashda xatolik: {str(e)}"
        )
