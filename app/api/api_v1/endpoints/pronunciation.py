from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.api import deps
from app import crud, models
from app.schemas.speech import (
    PronunciationPhraseCreate,
    PronunciationPhrase,
)
from app.services.ai.pronunciation_service import pronunciation_service

router = APIRouter()

# ---- Phrases ----
@router.post("/phrases/", response_model=PronunciationPhrase)
def create_pronunciation_phrase(
    data: PronunciationPhraseCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    phrase = crud.crud_pronunciation_phrase.create(db, obj_in=data)
    return phrase


@router.get("/phrases/{phrase_id}", response_model=PronunciationPhrase)
def get_pronunciation_phrase(
    phrase_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    phrase = crud.crud_pronunciation_phrase.get(db, id=phrase_id)
    if not phrase:
        raise HTTPException(status_code=404, detail="Pronunciation phrase not found")
    return phrase


@router.get("/phrases/", response_model=List[PronunciationPhrase])
def list_pronunciation_phrases(
    level: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    return crud.crud_pronunciation_phrase.list(db, skip=skip, limit=limit, level=level)


@router.put("/phrases/{phrase_id}", response_model=PronunciationPhrase)
def update_pronunciation_phrase(
    phrase_id: int,
    data: Dict[str, Any],
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    updated = crud.crud_pronunciation_phrase.update(db, id=phrase_id, update_data=data)
    if not updated:
        raise HTTPException(status_code=404, detail="Pronunciation phrase not found")
    return updated


@router.delete("/phrases/{phrase_id}")
def delete_pronunciation_phrase(
    phrase_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    ok = crud.crud_pronunciation_phrase.remove(db, id=phrase_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Pronunciation phrase not found")
    return {"success": True}

# ---- Sessions ----
@router.post("/sessions/")
def create_pronunciation_session(
    payload: Dict[str, Any],
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    level: str = payload.get("level")
    phrase_ids: List[int] = payload.get("phrase_ids") or payload.get("phrases") or []
    if not level:
        raise HTTPException(status_code=422, detail="level is required")
    if not isinstance(phrase_ids, list) or not all(isinstance(x, int) for x in phrase_ids):
        raise HTTPException(status_code=422, detail="phrase_ids must be a list of integers")

    # Create session manually to avoid mismatched schema/DB columns
    session = models.PronunciationSession(user_id=current_user.id, level=level)
    db.add(session)
    db.commit()
    db.refresh(session)

    # Collect phrase objects for response
    phrases = []
    for pid in phrase_ids:
        p = crud.crud_pronunciation_phrase.get(db, id=pid)
        if p:
            phrases.append({"id": p.id, "text": p.text, "level": p.level, "category": p.category})

    return {
        "id": session.id,
        "user_id": current_user.id,
        "level": level,
        "phrases": phrases,
        "created_at": session.created_at.isoformat() if getattr(session, "created_at", None) else None,
    }


@router.get("/sessions/{session_id}")
def get_pronunciation_session(
    session_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    session = crud.crud_pronunciation_session.get(db, id=session_id)
    if not session or session.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Pronunciation session not found")
    return {
        "id": session.id,
        "user_id": session.user_id,
        "level": session.level,
        "completed": getattr(session, "completed", False),
        "created_at": session.created_at.isoformat() if getattr(session, "created_at", None) else None,
        "completed_at": session.completed_at.isoformat() if getattr(session, "completed_at", None) else None,
    }


@router.get("/sessions/")
def list_pronunciation_sessions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    sessions = crud.crud_pronunciation_session.list_by_user(db, user_id=current_user.id, skip=skip, limit=limit)
    return [
        {
            "id": s.id,
            "user_id": s.user_id,
            "level": s.level,
            "completed": getattr(s, "completed", False),
            "created_at": s.created_at.isoformat() if getattr(s, "created_at", None) else None,
            "completed_at": s.completed_at.isoformat() if getattr(s, "completed_at", None) else None,
        }
        for s in sessions
    ]


@router.patch("/sessions/{session_id}/complete")
def complete_pronunciation_session(
    session_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    session = crud.crud_pronunciation_session.get(db, id=session_id)
    if not session or session.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Pronunciation session not found")
    session = crud.crud_pronunciation_session.mark_completed(db, id=session_id)
    return {
        "id": session.id,
        "user_id": session.user_id,
        "level": session.level,
        "completed": getattr(session, "completed", False),
        "created_at": session.created_at.isoformat() if getattr(session, "created_at", None) else None,
        "completed_at": session.completed_at.isoformat() if getattr(session, "completed_at", None) else None,
    }

# ---- Analyze ----
@router.post("/analyze/")
async def analyze_pronunciation(
    session_id: Optional[int] = Form(None),
    phrase_id: int = Form(...),
    audio_file: UploadFile = File(...),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    phrase = crud.crud_pronunciation_phrase.get(db, id=phrase_id)
    if not phrase:
        raise HTTPException(status_code=404, detail="Pronunciation phrase not found")
    # Try AI assessment (gracefully handle unconfigured service)
    recognized_text = ""
    score: Optional[float] = None
    feedback_text: Optional[str] = None
    analysis_data: Optional[Dict[str, Any]] = None
    try:
        result = await pronunciation_service.assess_pronunciation(audio_file=audio_file, reference_text=phrase.text)
        if isinstance(result, dict):
            recognized_text = result.get("text") or ""
            assessment = result.get("assessment") or {}
            if isinstance(assessment, dict):
                score = assessment.get("overall_score")
            feedback = result.get("feedback")
            if isinstance(feedback, dict):
                feedback_text = feedback.get("feedback")
            elif isinstance(feedback, str):
                feedback_text = feedback
            analysis_data = result
    except Exception as e:
        # Fall back to minimal attempt without AI data
        feedback_text = f"Analysis failed: {e}"

    attempt_in = {
        "user_id": current_user.id,
        "session_id": session_id,
        "phrase_id": phrase_id,
        "recognized_text": recognized_text,
        "expected_text": phrase.text,
        "score": score,
        "feedback": feedback_text,
        "analysis_data": analysis_data,
    }
    attempt = crud.crud_pronunciation_attempt.create(db, obj_in=attempt_in)

    # Update aggregated profile
    try:
        level = getattr(phrase, "level", None)
        crud.crud_user_pronunciation_profile.update_on_attempt(db, user_id=current_user.id, level=level, score=score)
    except Exception:
        pass

    return {
        "attempt_id": attempt.id,
        "recognized_text": attempt.recognized_text or "",
        "expected_text": attempt.expected_text,
        "score": attempt.score if attempt.score is not None else 0.0,
        "feedback": attempt.feedback or "",
    }


# ---- History ----
@router.get("/history/")
def get_pronunciation_history(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    q = db.query(models.PronunciationAttempt).filter(models.PronunciationAttempt.user_id == current_user.id).order_by(models.PronunciationAttempt.created_at.desc())
    attempts = q.all()
    results = []
    for a in attempts:
        results.append({
            "id": a.id,
            "user_id": a.user_id,
            "session_id": a.session_id,
            "phrase_id": a.phrase_id,
            "recognized_text": a.recognized_text,
            "expected_text": a.expected_text,
            "score": a.score,
            "feedback": a.feedback,
            "created_at": a.created_at.isoformat() if getattr(a, "created_at", None) else None,
        })
    return results


# ---- Profile ----
@router.get("/profile/")
def get_pronunciation_profile(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    attempts = db.query(models.PronunciationAttempt).filter(models.PronunciationAttempt.user_id == current_user.id).all()
    scores = [a.score for a in attempts if a.score is not None]
    avg = sum(scores) / len(scores) if scores else 0.0
    return {
        "average_score": round(avg, 2),
        "total_attempts": len(attempts),
    }
