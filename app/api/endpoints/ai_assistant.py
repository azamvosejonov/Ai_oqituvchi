"""
AI yordamchi uchun API endpointlari.
"""
from fastapi import APIRouter, Depends, HTTPException, Body, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session
import io
import difflib

from app.core.deps import get_current_active_user
from app.models.user import User
from app.core import deps
from app.core.ai.gemini_service import gemini_service
from app.services import ai_services

router = APIRouter()

class Message(BaseModel):
    role: str  # "user" yoki "model"
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1000

class AIConversationRequest(BaseModel):
    text: str
    language: str

@router.post("/chat", response_model=Dict[str, Any])
async def chat_with_ai(
    request: ChatRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    AI yordamchi bilan suhbat qilish uchun endpoint.
    
    Foydalanish uchun:
    ```json
    {
        "messages": [
            {"role": "user", "content": "Salom"},
            {"role": "model", "content": "Salom! Sizga qanday yordam bera olaman?"},
            {"role": "user", "content": "Ingliz tilini qanday tez o'rganish mumkin?"}
        ],
        "temperature": 0.7,
        "max_tokens": 1000
    }
    """
    try:
        # Chatga xabarlar ro'yxatini yuborish
        response = await gemini_service.chat(
            [msg.dict() for msg in request.messages],
            temperature=request.temperature,
            max_output_tokens=request.max_tokens
        )
        
        return {
            "success": True,
            "response": response,
            "message": "Xabar muvaffaqiyatli yuborildi"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI xizmatida xatolik: {str(e)}"
        )

@router.post("/generate-text", response_model=Dict[str, Any])
async def generate_text(
    prompt: str,
    temperature: float = 0.7,
    max_tokens: int = 1000,
    current_user: User = Depends(get_current_active_user)
):
    """
    Oddiy matn generatsiya qilish uchun endpoint.
    """
    try:
        response = await gemini_service.generate_text(
            prompt,
            temperature=temperature,
            max_output_tokens=max_tokens
        )
        
        return {
            "success": True,
            "response": response,
            "message": "Matn muvaffaqiyatli generatsiya qilindi"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Matn generatsiyasida xatolik: {str(e)}"
        )

@router.post("/converse", response_class=StreamingResponse)
async def converse_with_ai(
    *, 
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    request_data: AIConversationRequest = Body(...)
):
    """
    Handles a conversation turn with the AI assistant.
    1. Takes user's text input.
    2. Gets a text response from Gemini.
    3. Converts the text response to speech (TTS).
    4. Streams the audio back to the client.
    """
    # 1. Get text response from AI model
    prompt = request_data.text
    try:
        text_response = await ai_services.get_gemini_response(prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI model communication error: {e}")

    # 2. Convert the response to speech
    try:
        audio_content = await ai_services.synthesize_speech(text_response, language_code=request_data.language)
    except ConnectionError as e:
        # This happens if the TTS client isn't configured (e.g., missing credentials)
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Speech synthesis error: {e}")

    # 3. Stream the audio content back
    return StreamingResponse(io.BytesIO(audio_content), media_type="audio/mpeg")

@router.post("/evaluate-pronunciation", response_model=Dict[str, Any])
async def evaluate_pronunciation(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    audio_file: UploadFile = File(...),
    original_text: str = Form(...),
    language_code: str = Form("en-US")
):
    """
    Evaluates the user's pronunciation by comparing their speech to a given text.
    1. Receives an audio file and the original text.
    2. Transcribes the audio to text using STT.
    3. Calculates the similarity between the transcribed text and the original text.
    4. Returns the original text, transcribed text, and a similarity score.
    """
    audio_bytes = await audio_file.read()

    try:
        transcribed_text = await ai_services.transcribe_speech(audio_bytes, language_code=language_code)
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Speech transcription failed: {e}")

    if not transcribed_text:
        raise HTTPException(status_code=400, detail="Could not transcribe audio. The audio might be empty or unclear.")

    # Calculate similarity
    similarity = difflib.SequenceMatcher(None, original_text.lower(), transcribed_text.lower()).ratio()

    return {
        "original_text": original_text,
        "transcribed_text": transcribed_text,
        "similarity_score": similarity
    }

@router.post("/evaluate-answer", response_model=Dict[str, Any])
async def evaluate_answer(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    question: str = Form(...),
    correct_answer: str = Form(...),
    user_answer_text: Optional[str] = Form(None),
    audio_file: Optional[UploadFile] = File(None),
    language_code: str = Form("en-US")
):
    """
    Evaluates a user's answer (text or audio) against a correct answer and provides AI-driven feedback.
    """
    if not user_answer_text and not audio_file:
        raise HTTPException(status_code=400, detail="Either 'user_answer_text' or 'audio_file' must be provided.")

    user_answer = ""
    if audio_file:
        try:
            audio_bytes = await audio_file.read()
            user_answer = await ai_services.transcribe_speech(audio_bytes, language_code=language_code)
            if not user_answer:
                raise HTTPException(status_code=400, detail="Could not transcribe audio.")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Audio processing failed: {e}")
    else:
        user_answer = user_answer_text

    try:
        analysis = await ai_services.analyze_user_answer(question, correct_answer, user_answer)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze answer: {e}")
