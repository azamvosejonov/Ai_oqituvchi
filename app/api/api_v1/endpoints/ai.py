from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from sqlalchemy.sql.functions import current_user
from starlette.responses import StreamingResponse
import logging
import os
from pathlib import Path
from datetime import datetime
from typing import Optional

from app import models, schemas, settings
from app.api import deps
from app.services import ai_service
from app.core.limiter import limiter
from app.crud import crud_user_ai_usage
from gtts import gTTS
from gtts.lang import tts_langs

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/tts/voices")
async def list_tts_voices():
    """Return a static list of available TTS voices/languages (gTTS supports language codes)."""
    return {
        "voices": [
            {"code": "en", "name": "English"},
            {"code": "en-uk", "name": "English (UK)"},
            {"code": "en-us", "name": "English (US)"},
            {"code": "ru", "name": "Russian"},
            {"code": "uz", "name": "Uzbek"},
            {"code": "tr", "name": "Turkish"},
        ]
    }

@router.get("/stt/languages")
async def list_stt_languages():
    """Return a static list of languages supported by our Whisper-based STT pipeline."""
    return {
        "languages": [
            {"code": "en", "name": "English"},
            {"code": "ru", "name": "Russian"},
            {"code": "uz", "name": "Uzbek"},
            {"code": "tr", "name": "Turkish"},
        ]
    }

@router.post("/ask", response_model=schemas.AIResponse)
@limiter.limit("30/minute")
async def ask_question(
    request: Request,
    payload: schemas.AIQuestion,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.AIQuotaChecker('gpt4o_requests_left', 1)),
    speak: bool = False,
    language: str = "uz",
):
    """
    Receives a text prompt and returns a text-based answer from the AI.
    """
    # In testing mode, bypass external AI and quota to keep tests deterministic
    if settings.TESTING:
        # Optional TTS in testing mode as well (free gTTS)
        audio_url = None
        if speak:
            try:
                uploads_root = Path(settings.UPLOAD_DIR)
                tts_dir = uploads_root / "tts"
                tts_dir.mkdir(parents=True, exist_ok=True)
                filename = f"ask_{current_user.id}_{int(datetime.utcnow().timestamp())}.mp3"
                filepath = tts_dir / filename
                # Resolve language with fallback based on supported gTTS langs
                requested = language.split('-')[0]
                supported_langs = tts_langs()
                fallback_order = [requested, "uz", "tr", "ru", "en"]
                chosen = next((lc for lc in fallback_order if lc in supported_langs), None)
                if not chosen:
                    # last resort: any supported language key
                    chosen = next(iter(supported_langs.keys()))
                tts = gTTS(text=f"Echo: {payload.prompt}", lang=chosen, slow=False)
                tts.save(str(filepath))
                audio_url = f"/uploads/tts/{filename}"
            except Exception as e:
                logger.error(f"Testing TTS generation failed: {e}")
        return {
            "text": f"Echo: {payload.prompt}",
            "avatar_type": "default",
            "avatar_name": "assistant",
            "audio_url": audio_url,
        }
    if not settings.AI_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="AI service is not configured. Missing AI_API_KEY.",
        )

    try:
        # Increment usage counter (quota decrement handled by dependency)
        crud_user_ai_usage.user_ai_usage.increment(
            db, user_id=current_user.id, field="gemini_requests", amount=1
        )

        # The service returns a generator, so we need to concatenate the chunks.
        response_generator = ai_service.ask_llm(db=db, prompt=payload.prompt, user=current_user)
        full_response = "".join([chunk async for chunk in response_generator])
        
        audio_url = None
        if speak and full_response:
            try:
                uploads_root = Path(settings.UPLOAD_DIR)
                tts_dir = uploads_root / "tts"
                tts_dir.mkdir(parents=True, exist_ok=True)
                filename = f"ask_{current_user.id}_{int(datetime.utcnow().timestamp())}.mp3"
                filepath = tts_dir / filename
                # Resolve language with fallback based on supported gTTS langs
                requested = language.split('-')[0]
                supported_langs = tts_langs()
                fallback_order = [requested, "uz", "tr", "ru", "en"]
                chosen = next((lc for lc in fallback_order if lc in supported_langs), None)
                if not chosen:
                    chosen = next(iter(supported_langs.keys()))
                tts = gTTS(text=full_response, lang=chosen, slow=False)
                tts.save(str(filepath))
                audio_url = f"/uploads/tts/{filename}"
            except Exception as e:
                logger.error(f"TTS generation failed: {e}")

        return {
            "text": full_response,
            "avatar_type": "default",
            "avatar_name": "assistant",
            "audio_url": audio_url,
        }
    except Exception as e:
        logger.error(f"AI ask endpointida xatolik: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/lessons/suggested", response_model=list[schemas.InteractiveLesson])
async def get_suggested_lessons(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user_with_free_window),
    limit: int = 5,
):
    """
    Returns a list of suggested interactive lessons based on user's level and tags.
    Excludes completed lessons and premium-locked lessons for non-premium users.
    """
    try:
        lessons = await ai_service.get_suggested_lessons_by_level_tags(db=db, user=current_user, limit=limit)
        return lessons
    except Exception as e:
        logger.error(f"Suggested lessons endpointida xatolik: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tts")
@limiter.limit("60/minute")
async def text_to_speech(
    request: Request,
    payload: schemas.TTSRequest,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user_with_free_window),
):
    """
    Converts text to speech and streams the audio back.
    """
    try:
        text_length = len(payload.text or "")
        # Endpoint-level TTS character quota enforcement
        usage = crud_user_ai_usage.user_ai_usage.get_or_create(db, user_id=current_user.id)
        remaining = getattr(usage, "tts_chars_left", 0)
        if remaining < text_length:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="TTS character quota exceeded. Please upgrade your plan."
            )
        # Decrement remaining chars and increment consumed counter atomically
        setattr(usage, "tts_chars_left", remaining - text_length)
        usage.tts_characters = (usage.tts_characters or 0) + text_length
        db.add(usage)
        db.commit()
        db.refresh(usage)

        return StreamingResponse(
            ai_service.text_to_speech_stream(text=payload.text, language_code=payload.language),
            media_type="audio/mpeg"
        )
    except HTTPException as e:
        # Return HTTPExceptions (e.g., 403 quota exceeded) as-is instead of wrapping into 500
        raise e
    except Exception as e:
        logger.error(f"TTS endpointida xatolik: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/analyze-answer", response_model=schemas.AIFeedbackResponse)
async def analyze_answer(
    payload: schemas.AIFeedbackRequest,
):
    """
    Analyzes a user's textual answer and returns structured feedback.
    """
    try:
        result = await ai_service.analyze_answer(
            user_response=payload.user_response,
            reference_text=payload.reference_text,
            language=payload.language,
        )
        return result
    except Exception as e:
        logger.error(f"Analyze-answer endpointida xatolik: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stt", response_model=schemas.STTResponse)
@limiter.limit("60/minute")
async def speech_to_text(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.AIQuotaChecker('stt_requests_left', 1))
):
    """
    Transcribes audio to text using the Whisper model.
    """
    if not file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an audio file.")
    
    try:
        content = await file.read()
        transcribed_text = await ai_service.transcribe_audio_file(content)
        # Increment usage counter
        crud_user_ai_usage.user_ai_usage.increment(
            db, user_id=current_user.id, field="stt_requests", amount=1
        )
        return {"text": transcribed_text}
    except Exception as e:
        logger.error(f"STT endpointida xatolik: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/pronunciation", response_model=schemas.AIPronunciationAssessment)
async def assess_pronunciation(
    *, 
    file: UploadFile = File(...),
    reference_text: str = Form(...),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.AIQuotaChecker('pronunciation_analysis_left', 1))
):
    """
    Assesses the pronunciation of an audio file against a reference text using a free, local model.
    """
    try:
        file_content = await file.read()
        if not file_content:
            raise HTTPException(status_code=400, detail="Audio file is empty.")

        result = await ai_service.pronunciation_assessment(
            file_content=file_content, 
            reference_text=reference_text
        )

        if result.get("error"):
            raise HTTPException(status_code=500, detail=result["error"])

        return result
    except Exception as e:
        logger.error(f"Talaffuzni baholash endpointida xatolik: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pronunciation/history")
async def pronunciation_history(
    limit: int = 20,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user_with_free_window),
):
    """Return recent pronunciation attempts for the current user."""
    q = (
        db.query(models.PronunciationAttempt)
        .filter(models.PronunciationAttempt.user_id == current_user.id)
        .order_by(desc(models.PronunciationAttempt.created_at))
        .limit(limit)
    )
    attempts = q.all()
    return [
        {
            "id": a.id,
            "recognized_text": a.recognized_text,
            "expected_text": a.expected_text,
            "score": a.score,
            "feedback": a.feedback,
            "created_at": a.created_at,
        }
        for a in attempts
    ]


@router.get("/pronunciation/summary")
async def pronunciation_summary(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user_with_free_window),
):
    """Return pronunciation profile summary for the current user."""
    profile = (
        db.query(models.UserPronunciationProfile)
        .filter(models.UserPronunciationProfile.user_id == current_user.id)
        .first()
    )
    if not profile:
        return {
            "overall_score": 0.0,
            "total_attempts": 0,
            "last_practice": None,
        }
    return {
        "overall_score": profile.overall_score,
        "total_attempts": profile.total_attempts,
        "last_practice": profile.last_practice,
        "beginner_score": profile.beginner_score,
        "intermediate_score": profile.intermediate_score,
        "advanced_score": profile.advanced_score,
        "common_errors": profile.common_errors,
    }


@router.post("/voice-loop", response_model=schemas.VoiceLoopResponse)
@limiter.limit("20/minute")
async def voice_loop(
    request: Request,
    file: UploadFile = File(...),
    language: str = Form("uz"),
    reference_text: Optional[str] = Form(None),
    db: Session = Depends(deps.get_db),
    _stt_quota_guard: models.User = Depends(deps.AIQuotaChecker('stt_requests_left', 1)),
    _ai_quota_guard: models.User = Depends(deps.AIQuotaChecker('gpt4o_requests_left', 1)),
    current_user: models.User = Depends(deps.get_current_user_with_free_window),
):
    """
    Unified voice loop orchestration:
    1) Transcribe uploaded audio (STT)
    2) Generate structured AI feedback for the transcribed text
    3) Synthesize TTS for the AI textual response

    Returns transcript, AI text, corrections, advice, and TTS audio URL.
    """
    if not file.content_type or not file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an audio file.")

    try:
        # 1) STT
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Audio file is empty.")

        transcript = await ai_service.transcribe_audio_file(content)
        # Track usage counters (STT)
        crud_user_ai_usage.user_ai_usage.increment(
            db, user_id=current_user.id, field="stt_requests", amount=1
        )

        # 2) AI feedback (deterministic heuristic in tests, external otherwise)
        feedback = await ai_service.analyze_answer(
            user_response=transcript,
            reference_text=reference_text,
            language=language,
        )
        # Track usage counters (AI text gen)
        crud_user_ai_usage.user_ai_usage.increment(
            db, user_id=current_user.id, field="gemini_requests", amount=1
        )

        # Extract concise AI text, corrections and advice from structured feedback
        ai_text = (feedback.get("overall", {}) or {}).get("feedback", "")
        corrections = (feedback.get("grammar", {}) or {}).get("corrections", []) or []
        advice = (feedback.get("overall", {}) or {}).get("next_steps", []) or []

        # 3) TTS for the AI text with character-based quota enforcement
        audio_url: Optional[str] = None
        if ai_text:
            usage = crud_user_ai_usage.user_ai_usage.get_or_create(db, user_id=current_user.id)
            remaining_chars = getattr(usage, "tts_chars_left", 0) or 0
            needed = len(ai_text)
            if remaining_chars < needed:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="TTS character quota exceeded. Please upgrade your plan."
                )

            # Decrement remaining and increment consumed counters
            setattr(usage, "tts_chars_left", remaining_chars - needed)
            usage.tts_characters = (usage.tts_characters or 0) + needed
            db.add(usage)
            db.commit()
            db.refresh(usage)

            # Generate MP3 via gTTS and store under uploads/tts
            uploads_root = Path(settings.UPLOAD_DIR)
            tts_dir = uploads_root / "tts"
            tts_dir.mkdir(parents=True, exist_ok=True)
            filename = f"voice_loop_{current_user.id}_{int(datetime.utcnow().timestamp())}.mp3"
            filepath = tts_dir / filename

            # Resolve TTS language with fallbacks
            try:
                requested = language.split('-')[0]
                supported_langs = tts_langs()
                fallback_order = [requested, "uz", "tr", "ru", "en"]
                chosen = next((lc for lc in fallback_order if lc in supported_langs), None)
                if not chosen:
                    chosen = next(iter(supported_langs.keys()))
                tts = gTTS(text=ai_text, lang=chosen, slow=False)
                tts.save(str(filepath))
                audio_url = f"/uploads/tts/{filename}"
            except Exception as e:
                logger.error(f"Voice loop TTS generation failed: {e}")
                audio_url = None

        # Collect remaining quotas snapshot
        usage_final = crud_user_ai_usage.user_ai_usage.get_or_create(db, user_id=current_user.id)
        quotas = {
            "stt_requests_left": getattr(usage_final, "stt_requests_left", 0),
            "gpt4o_requests_left": getattr(usage_final, "gpt4o_requests_left", 0),
            "tts_chars_left": getattr(usage_final, "tts_chars_left", 0),
        }

        return {
            "transcript": transcript,
            "ai_text": ai_text,
            "corrections": corrections,
            "advice": advice,
            "audio_url": audio_url,
            "feedback": feedback,
            "quotas": quotas,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Voice loop endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/suggest-lesson", response_model=schemas.InteractiveLesson)
async def suggest_lesson_endpoint(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user_with_free_window),
):
    """
    Suggests a new lesson for the user based on their progress.
    """
    suggested_lesson = await ai_service.suggest_lesson(db=db, user=current_user)
    if not suggested_lesson:
        raise HTTPException(
            status_code=404,
            detail="Could not suggest a lesson. You may have completed all available lessons.",
        )
    return suggested_lesson


@router.get("/usage", response_model=schemas.UserAIUsage)
async def get_ai_usage(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """Return current user's AI usage and remaining quotas."""
    usage = crud_user_ai_usage.user_ai_usage.get_or_create(db, user_id=current_user.id)
    return usage


@router.post("/usage/reset", response_model=schemas.UserAIUsage)
async def reset_ai_usage_for_user(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_admin: models.User = Depends(deps.get_current_active_admin),
):
    """Admin-only: reset AI usage/quotas for a given user."""
    usage = crud_user_ai_usage.user_ai_usage.reset(db, user_id=user_id)
    return usage
