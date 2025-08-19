from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
import io

from app import models, schemas
from app.api import deps
from app.schemas import AIChatResponse, AIChatInput
from app.services import ai_service
from app.core.config import settings

router = APIRouter()

@router.post("/chat", response_model=AIChatResponse)
async def chat_with_ai(
    chat_input:AIChatInput,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """Chat with the AI assistant"""
    try:
        response = ""
        async for chunk in ai_service.ask_llm(
            prompt=chat_input.message,
            db=db,
            lesson_id=chat_input.lesson_id,
            user=current_user
        ):
            response += chunk
            
        return {"response": response}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/analyze-answer", response_model=schemas.AIFeedbackResponse)
async def analyze_answer(
    req: schemas.AIFeedbackRequest,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """Analyze user's answer vs reference and return structured AI feedback.

    This is a lightweight, on-device heuristic implementation to avoid paid APIs.
    """
    try:
        import uuid
        from datetime import datetime

        user_text = (req.user_response or "").strip()
        ref_text = (req.reference_text or "").strip()

        # Basic tokenization
        def tokenize(s: str) -> List[str]:
            return [t.lower().strip(".,!?;:") for t in s.split() if t]

        user_tokens = tokenize(user_text)
        ref_tokens = tokenize(ref_text)

        # Overlap score as a proxy for content correctness
        overlap = 0.0
        if user_tokens and ref_tokens:
            inter = set(user_tokens) & set(ref_tokens)
            union = set(user_tokens) | set(ref_tokens)
            overlap = (len(inter) / max(1, len(union))) * 100.0

        # Very simple heuristics for other scores
        length_penalty = 0.0 if len(user_tokens) >= max(3, int(len(ref_tokens) * 0.5)) else 15.0
        grammar_score = max(0.0, min(100.0, overlap + 20.0 - length_penalty))
        vocab_score = max(0.0, min(100.0, overlap + 10.0))
        pronunciation_score = 70.0  # textual proxy (true score needs audio)
        fluency_score = max(0.0, min(100.0, 60.0 + (len(user_tokens) > 6) * 10 - ("," in user_text) * 5))

        def mk_feedback(score: float, base_feedback: str) -> Dict[str, Any]:
            return {
                "score": round(score, 2),
                "feedback": base_feedback,
            }

        grammar = {
            **mk_feedback(grammar_score, "Grammar looks decent. Watch basic sentence structure and agreement."),
            "corrections": [],
            "error_types": None,
        }

        # Suggest simple vocabulary improvements by spotting repeated words
        repeats = []
        seen = set()
        for tok in user_tokens:
            if tok in seen and tok not in repeats:
                repeats.append(tok)
            seen.add(tok)
        vocabulary = {
            **mk_feedback(vocab_score, "Try to diversify vocabulary and match key terms from the reference."),
            "suggestions": repeats[:5],
            "advanced_words": [],
            "misused_words": [],
        }

        pronunciation = {
            **mk_feedback(pronunciation_score, "Without audio we estimate pronunciation; try clear stress and pacing."),
            "tips": [
                "Speak slowly and clearly",
                "Emphasize key content words",
                "Practice difficult sounds using minimal pairs",
            ],
            "problem_sounds": [],
            "stress_patterns": None,
        }

        fluency = {
            **mk_feedback(fluency_score, "Aim for natural rhythm and avoid long pauses."),
            "suggestions": [
                "Use linking words (however, therefore, moreover)",
                "Keep sentences concise",
            ],
            "pace": "just right" if fluency_score >= 70 else "too slow",
            "hesitation_markers": None,
        }

        overall_score = round((grammar_score + vocab_score + pronunciation_score + fluency_score) / 4.0, 2)
        overall = {
            **mk_feedback(overall_score, "Good effort. Focus on aligning content with the reference and clarity."),
            "next_steps": [
                "Re-read the reference, note 3 key terms, and include them in your answer",
                "Record a 30s response focusing on clarity and grammar",
            ],
            "strengths": ["Relevant content" if overlap > 30 else "Basic attempt"],
            "areas_for_improvement": ["Content alignment", "Sentence structure", "Vocabulary range"],
        }

        resp: Dict[str, Any] = {
            "feedback_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow(),
            "grammar": grammar,
            "vocabulary": vocabulary,
            "pronunciation": pronunciation,
            "fluency": fluency,
            "audio_feedback_url": None,
            "metadata": {
                "overlap": round(overlap, 2),
                "user_token_count": len(user_tokens),
                "ref_token_count": len(ref_tokens),
                "language": req.language,
            },
        }
        return resp
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
@router.post("/transcribe", response_model=schemas.STTResponse)
async def transcribe_audio(
    file: UploadFile = File(...),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser)
):
    """Transcribe audio to text"""
    try:
        contents = await file.read()
        transcription = await ai_service.transcribe_audio_file(contents)
        return {"text": transcription}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/pronunciation/score", response_model=schemas.AIPronunciationAssessment)
async def score_pronunciation(
    file: UploadFile = File(...),
    target_text: str = "",
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """Score pronunciation from audio"""
    try:
        contents = await file.read()
        result = await ai_service.pronunciation_assessment(
            file_content=contents,
            reference_text=target_text
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/suggest-lesson", response_model=schemas.InteractiveLesson)
async def suggest_next_lesson(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """Get suggested next lesson based on user progress"""
    try:
        suggestion = await ai_service.suggest_lesson(db, current_user)
        return suggestion
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
