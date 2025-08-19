import logging
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
from pathlib import Path

from app import models, schemas, crud
from app.api import deps
from app.services import ai_service, ai_services
from app.core.config import settings
from gtts import gTTS
from gtts.lang import tts_langs

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/", response_model=List[schemas.InteractiveLesson])
def get_interactive_lessons(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_user_with_free_window)
):
    """
    Get list of interactive lessons available to the user
    """
    lessons = crud.interactive_lesson.get_multi(db, skip=skip, limit=limit)
    return lessons


@router.get("/{lesson_id}", response_model=schemas.InteractiveLesson)
def get_interactive_lesson(
    lesson_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user_with_free_window)
):
    """
    Get a specific interactive lesson by ID
    """
    lesson = crud.interactive_lesson.get(db, id=lesson_id)
    if not lesson:
        raise HTTPException(
            status_code=404,
            detail="Interactive lesson not found"
        )
    
    # Check if user has access to premium lessons
    if getattr(lesson, "is_premium", False) and not current_user.is_premium and not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Premium obuna kerak"
        )
    
    return lesson


@router.post(
    "/start-lesson", 
    response_model=schemas.LessonStartResponse,
    summary="Start a new interactive lesson session",
    description="""
    Start a new interactive lesson session with an AI tutor.
    
    - Creates a new lesson session
    - Initializes AI tutor with selected avatar
    - Returns session details and initial greeting
    """,
    responses={
        200: {"description": "Successfully started lesson session"},
        400: {"description": "Invalid request or missing parameters"},
        401: {"description": "Not authenticated"},
        500: {"description": "Internal server error"}
    }
)
async def start_lesson(
    lesson_data: schemas.LessonStart,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user_with_free_window)
):
    """
    Start a new interactive lesson session
    """
    try:
        # Pick a lesson the user can access (non-premium for free users)
        q = db.query(models.InteractiveLesson)
        if not current_user.is_premium and not current_user.is_superuser:
            q = q.filter(models.InteractiveLesson.is_premium == False)
        lesson_obj = q.order_by(models.InteractiveLesson.order).first()
        if not lesson_obj:
            raise HTTPException(status_code=404, detail="Mavjud dars topilmadi")

        # Create a valid LessonSession (model has only user_id, lesson_id, status)
        db_session = crud.interactive_lesson_session.create(
            db,
            obj_in={
                "user_id": current_user.id,
                "lesson_id": lesson_obj.id,
                "status": "in_progress",
            },
        )
        
        greeting_text = f"Salom! Men sizning {lesson_data.difficulty} darajadagi {lesson_data.lesson_type} darsingizda yordam beraman."
        # Optionally create a greeting TTS file and return its URL (enforce TTS char quota gracefully)
        audio_url = None
        try:
            uploads_root = Path(settings.UPLOAD_DIR)
            tts_dir = uploads_root / "tts"
            tts_dir.mkdir(parents=True, exist_ok=True)
            filename = f"greeting_{current_user.id}_{int(datetime.utcnow().timestamp())}.mp3"
            filepath = tts_dir / filename
            requested = "uz"
            supported_langs = tts_langs()
            fallback_order = [requested, "uz", "tr", "ru", "en"]
            chosen = next((lc for lc in fallback_order if lc in supported_langs), None)
            if not chosen:
                chosen = next(iter(supported_langs.keys()))
            # Check quota
            try:
                usage = crud.user_ai_usage.get_or_create(db, user_id=current_user.id)
                text_len = len(greeting_text or "")
                remaining = getattr(usage, "tts_chars_left", 0)
                if remaining < text_len:
                    # Not enough quota → fallback to text-only, do not raise
                    audio_url = None
                else:
                    # Attempt TTS first; only deduct on success
                    gTTS(text=greeting_text, lang=chosen, slow=False).save(str(filepath))
                    audio_url = f"/uploads/tts/{filename}"
                    # Deduct quota after successful synthesis
                    setattr(usage, "tts_chars_left", remaining - text_len)
                    setattr(usage, "tts_characters", getattr(usage, "tts_characters", 0) + text_len)
                    db.add(usage)
                    db.commit()
                    db.refresh(usage)
            except Exception:
                # If anything goes wrong, do not change quota and just skip audio
                audio_url = None
        except Exception:
            audio_url = None

        crud.interactive_lesson_interaction.create(
            db,
            obj_in={
                "session_id": db_session.id,
                "user_input": "<system_start>",
                "ai_response": greeting_text,
                "audio_url": audio_url,
            },
        )

        # Get avatar name based on avatar_type
        avatar_name = "Default AI Tutor"  # Default name, can be fetched from a database or config
        
        # Create response matching LessonStartResponse schema
        return {
            "id": db_session.id,
            "user_id": current_user.id,
            "lesson_type": lesson_data.lesson_type,
            "started_at": db_session.start_time,
            "status": db_session.status,
            "avatar_type": lesson_data.avatar_type,
            "greeting": greeting_text,
            "avatar_name": avatar_name,
            "audio_url": audio_url,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting lesson: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Darsni boshlashda xatolik yuz berdi: {str(e)}"
        )

@router.post(
    "/send-message", 
    response_model=schemas.AIResponse,
    summary="Send a message to the AI tutor",
    description="""
    Send a message to the AI tutor and get a response.
    
    - Processes user message
    - Generates AI response
    - Returns text and optional audio response
    """,
    responses={
        200: {"description": "Successfully processed message"},
        400: {"description": "Invalid message or session"},
        401: {"description": "Not authenticated"},
        404: {"description": "Session not found"},
        500: {"description": "Error processing message"}
    }
)
async def send_message(
    message_data: schemas.UserMessage,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user_with_free_window)
):
    """
    Send a message to the AI tutor and get response
    """
    try:
        # Get the active session
        session = crud.interactive_lesson_session.get(db, id=message_data.session_id)
        if not session or session.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dars sessiyasi topilmadi yoki sizga tegishli emas"
            )
        
        # Build a short history: last few exchanges for context
        interactions = crud.interactive_lesson_interaction.get_by_session(db, session_id=session.id, skip=0, limit=6)
        history: List[Dict[str, Any]] = []
        for it in reversed(interactions):  # oldest to newest
            history.append({"role": "user", "parts": [{"text": getattr(it, "user_input", "") or ""}]})
            history.append({"role": "model", "parts": [{"text": it.ai_response or ""}]})
        history.append({"role": "user", "parts": [{"text": message_data.message}]})

        # Get assistant response via Gemini
        assistant_chunks: List[str] = []
        try:
            async for chunk in ai_service.get_chat_completion(history):
                if chunk:
                    assistant_chunks.append(chunk)
        except Exception:
            pass
        ai_text_response = ("".join(assistant_chunks)).strip() or "Qabul qilindi. Xabaringiz uchun rahmat."

        # Optionally synthesize TTS and save to file (enforce TTS char quota gracefully)
        audio_url = None
        try:
            uploads_root = Path(settings.UPLOAD_DIR)
            tts_dir = uploads_root / "tts"
            tts_dir.mkdir(parents=True, exist_ok=True)
            filename = f"reply_{current_user.id}_{int(datetime.utcnow().timestamp())}.mp3"
            filepath = tts_dir / filename
            supported_langs = tts_langs()
            fallback_order = ["uz", "tr", "ru", "en"]
            chosen = next((lc for lc in fallback_order if lc in supported_langs), None)
            if not chosen:
                chosen = next(iter(supported_langs.keys()))
            # Check quota and deduct on success only
            try:
                usage = crud.user_ai_usage.get_or_create(db, user_id=current_user.id)
                text_len = len(ai_text_response or "")
                remaining = getattr(usage, "tts_chars_left", 0)
                if remaining < text_len:
                    audio_url = None
                else:
                    gTTS(text=ai_text_response, lang=chosen, slow=False).save(str(filepath))
                    audio_url = f"/uploads/tts/{filename}"
                    setattr(usage, "tts_chars_left", remaining - text_len)
                    setattr(usage, "tts_characters", getattr(usage, "tts_characters", 0) + text_len)
                    db.add(usage)
                    db.commit()
                    db.refresh(usage)
            except Exception:
                audio_url = None
        except Exception:
            audio_url = None

        crud.interactive_lesson_interaction.create(
            db,
            obj_in={
                "session_id": session.id,
                "user_input": message_data.message,
                "ai_response": ai_text_response,
                "audio_url": audio_url,
            },
        )

        avatar_name = "Default AI Tutor"
        return {
            "text": ai_text_response,
            "audio_url": audio_url,
            "avatar_type": "default",
            "avatar_name": avatar_name,
            "suggestions": None,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Xabar yuborishda xatolik yuz berdi: {str(e)}"
        )

@router.post(
    "/send-audio-message",
    response_model=schemas.AIResponse,
    summary="Send an audio message to the AI tutor",
    description="Handles the full voice-to-voice interaction cycle."
)
async def send_audio_message(
    session_id: int = Form(...),
    audio_file: UploadFile = File(...),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user_with_free_window)
):
    """
    Accepts an audio message, processes it, and returns an audio response.
    """
    # 1. Get the active session
    session = crud.interactive_lesson_session.get(db, id=session_id)
    if not session or session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aktiv dars sessiyasi topilmadi"
        )

    try:
        audio_bytes = await audio_file.read()
        if not audio_bytes:
            raise HTTPException(status_code=400, detail="Audio file is empty.")

        # 2. Transcribe user's speech to text (STT)
        transcribed_text = await ai_service.transcribe_audio_file(audio_bytes)
        if not transcribed_text:
            raise HTTPException(status_code=400, detail="Could not understand the audio.")

        # Build minimal history and get response
        history = [
            {"role": "user", "parts": [{"text": transcribed_text}]}
        ]
        assistant_chunks: List[str] = []
        try:
            async for chunk in ai_service.get_chat_completion(history):
                if chunk:
                    assistant_chunks.append(chunk)
        except Exception:
            pass
        ai_text_response = ("".join(assistant_chunks)).strip() or "Qabul qilindi. Xabaringiz uchun rahmat."

        # Optionally synthesize TTS and save to file
        audio_url = None
        try:
            uploads_root = Path(settings.UPLOAD_DIR)
            tts_dir = uploads_root / "tts"
            tts_dir.mkdir(parents=True, exist_ok=True)
            filename = f"reply_{current_user.id}_{int(datetime.utcnow().timestamp())}.mp3"
            filepath = tts_dir / filename
            supported_langs = tts_langs()
            fallback_order = ["uz", "tr", "ru", "en"]
            chosen = next((lc for lc in fallback_order if lc in supported_langs), None)
            if not chosen:
                chosen = next(iter(supported_langs.keys()))
            gTTS(text=ai_text_response, lang=chosen, slow=False).save(str(filepath))
            audio_url = f"/uploads/tts/{filename}"
        except Exception:
            audio_url = None

        crud.interactive_lesson_interaction.create(
            db,
            obj_in={
                "session_id": session.id,
                "user_input": transcribed_text,
                "ai_response": ai_text_response,
                "audio_url": audio_url,
            },
        )

        avatar_name = "Default AI Tutor"
        return {
            "text": ai_text_response,
            "audio_url": audio_url,
            "avatar_type": "default",
            "avatar_name": avatar_name,
            "suggestions": None,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing audio message: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Audio xabarni qayta ishlashda xatolik: {str(e)}"
        )

@router.post(
    "/assess-pronunciation", 
    response_model=schemas.PronunciationAssessment,
    summary="Assess user's pronunciation",
    description="""
    Analyze and assess user's pronunciation.
    
    - Accepts audio recording
    - Compares with expected text
    - Returns detailed pronunciation feedback
    """,
    responses={
        200: {"description": "Successfully assessed pronunciation"},
        400: {"description": "Invalid audio or text"},
        401: {"description": "Not authenticated"},
        500: {"description": "Error processing pronunciation"}
    }
)
async def assess_pronunciation(
    expected_text: str = Form(...),
    audio_file: UploadFile = File(...),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user_with_free_window)
):
    """
    Assess user's pronunciation and provide feedback
    """
    try:
        # Validate audio file
        if not audio_file.content_type.startswith('audio/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Noto'g'ri audio format. Iltimos, audio fayl yuboring."
            )
        
        audio_bytes = await audio_file.read()
        user_text = await ai_services.transcribe_speech(audio_bytes)

        if not user_text:
            raise HTTPException(status_code=400, detail="Could not understand the audio for assessment.")

        analysis = await ai_services.analyze_user_answer(
            question=f"Please say: '{expected_text}'",
            correct_answer=expected_text,
            user_answer=user_text
        )

        # In a real app, you would save this attempt to the database
        # crud.pronunciation_attempt.create(...)

        return {
            "is_correct": analysis.get('is_correct', False),
            "feedback": analysis.get('feedback', 'Could not analyze.'),
            "score": analysis.get('score', 0.0) # Assuming analyze_user_answer returns a score
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in pronunciation assessment: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Talaffuzni baholashda xatolik yuz berdi: {str(e)}"
        )
