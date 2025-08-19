"""
Test va mashqlar uchun API endpointlari.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.core.ai.exercise_analyzer import exercise_analyzer
from app.models.user import User
from app.schemas.exercise import (
    ExerciseCreate, 
    ExerciseUpdate, 
    ExerciseInDB,
    ExerciseAttemptCreate,
    ExerciseAttemptInDB,
    ExerciseAnalysisResult
)
from app.services import ai_services

router = APIRouter()

@router.get("/", response_model=List[ExerciseInDB])
async def get_exercises(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    difficulty: Optional[str] = None,
    exercise_type: Optional[str] = None,
    lesson_id: Optional[int] = None,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Test va mashqlar ro'yxatini olish."""
    filters = {}
    if difficulty:
        filters["difficulty"] = difficulty
    if exercise_type:
        filters["exercise_type"] = exercise_type
    if lesson_id:
        filters["lesson_id"] = lesson_id
    
    exercises = crud.exercise.get_multi(
        db, 
        skip=skip, 
        limit=limit,
        **filters
    )
    return exercises

@router.get("/recommendations", response_model=List[ExerciseInDB])
async def get_recommendations(
    db: Session = Depends(deps.get_db),
    limit: int = 10,
    lesson_id: Optional[int] = None,
    difficulty: Optional[str] = None,
    exercise_type: Optional[str] = None,
    tags: Optional[List[str]] = Query(None),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Foydalanuvchi uchun tavsiya etilgan mashqlar ro'yxati.

    Filtrlar ixtiyoriy: lesson_id, difficulty, exercise_type, tags.
    Agar filtrlar berilmasa, mavjud mashqlardan birinchi `limit` tasi qaytariladi.
    """
    exercises = crud.exercise.get_multi_filtered(
        db,
        skip=0,
        limit=limit,
        lesson_id=lesson_id,
        difficulty=difficulty,
        exercise_type=exercise_type,
        is_active=True,
        tags=tags,
    )
    return exercises

@router.get("/{exercise_id}", response_model=ExerciseInDB)
async def get_exercise(
    exercise_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Bitta test yoki mashqni olish."""
    exercise = crud.exercise.get(db, id=exercise_id)
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mashq topilmadi"
        )
    return exercise

class ExerciseAnswer(BaseModel):
    answer: Optional[Dict | List | str | None] = None
    audio_url: Optional[str] = None
    language: Optional[str] = "uz"


class ExerciseFeedback(BaseModel):
    is_correct: bool
    score: float
    feedback: Dict[str, Any]
    explanation: Optional[str] = None


@router.post(
    "/{exercise_id}/check-answer",
    response_model=ExerciseFeedback,
    summary="Check if an answer is correct for an exercise",
    response_description="Detailed feedback about the answer",
)
async def check_exercise_answer(
    *,
    exercise_id: int,
    answer_data: ExerciseAnswer = Body(...),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Validate user's answer for a given exercise and return structured feedback.
    """
    try:
        # Debug traces
        try:
            print(f"[check_answer] exercise_id={exercise_id}, user_id={current_user.id}")
            print(f"[check_answer] DB session id={id(db)}")
            ex = crud.exercise.get(db, id=exercise_id)
            print(f"[check_answer] Exercise exists: {bool(ex)}")
        except Exception as dbg_e:
            print(f"[check_answer] Debug error: {dbg_e}")

        result = crud.exercise.check_answer(
            db=db,
            exercise_id=exercise_id,
            user_answer=answer_data.answer,
            user_id=current_user.id,
            audio_url=answer_data.audio_url,
            language=answer_data.language,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while checking the answer.",
        )

@router.post("/attempt", response_model=ExerciseAnalysisResult)
async def submit_exercise_attempt(
    attempt: ExerciseAttemptCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Test yoki mashq javobini yuborish va natijani olish."""
    # Mashqni olish
    exercise = crud.exercise.get(db, id=attempt.exercise_id)
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mashq topilmadi"
        )
    
    # AI orqali javobni tahlil qilish
    analysis = await exercise_analyzer.analyze_exercise_attempt(
        exercise=exercise,
        user_answer=attempt.user_answer,
        user=current_user
    )
    
    # Javob saqlash
    attempt_in = {
        "user_id": current_user.id,
        "exercise_id": exercise.id,
        "user_answer": attempt.user_answer,
        "is_correct": analysis["is_correct"],
        "score": analysis["score"],
        "feedback": analysis["feedback"],
        "metadata": {
            "feedback_type": analysis["feedback_type"],
            "suggestions": analysis.get("suggestions", []),
            "grammar_issues": analysis.get("grammar_analysis", []),
            "vocabulary_issues": analysis.get("vocabulary_analysis", []),
            "pronunciation_tips": analysis.get("pronunciation_tips", "")
        }
    }
    
    # Javobni ma'lumotlar bazasiga saqlash
    db_attempt = crud.exercise_attempt.create(db, obj_in=attempt_in)
    
    # Tahlil natijasiga saqlangan javob ID sini qo'shamiz
    analysis["attempt_id"] = db_attempt.id
    
    return analysis

@router.get("/attempts/me", response_model=List[ExerciseAttemptInDB])
async def get_my_attempts(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    exercise_id: Optional[int] = None,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Mening test va mashq urinishlarim ro'yxati."""
    filters = {"user_id": current_user.id}
    if exercise_id:
        filters["exercise_id"] = exercise_id
    
    attempts = crud.exercise_attempt.get_multi(
        db,
        skip=skip,
        limit=limit,
        **filters
    )
    return attempts

@router.get("/attempts/me/wrong", response_model=List[ExerciseAttemptInDB])
async def get_my_wrong_attempts(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Mening noto'g'ri urinishlarim (AI feedback bilan)."""
    q = db.query(models.ExerciseAttempt).filter(
        models.ExerciseAttempt.user_id == current_user.id,
        models.ExerciseAttempt.is_correct == False,
    )
    # Try to order by created_at if available
    try:
        q = q.order_by(models.ExerciseAttempt.created_at.desc())
    except Exception:
        pass
    wrong_attempts = q.offset(skip).limit(limit).all()
    return wrong_attempts

@router.get("/attempts/{attempt_id}", response_model=ExerciseAttemptInDB)
async def get_attempt(
    attempt_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Bitta urinish haqida ma'lumot olish."""
    attempt = crud.exercise_attempt.get(db, id=attempt_id)
    if not attempt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ushbu urinish topilmadi"
        )
    
    # Faqat o'z urinishlarini ko'rish mumkin
    if attempt.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Siz bu urinishni ko'rish huquqiga egasiz"
        )
    
    return attempt

@router.post("/attempts/{attempt_id}/analyze", response_model=schemas.ExerciseAttempt)
async def analyze_exercise_attempt_endpoint(
    attempt_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """Analyzes a specific exercise attempt using AI and returns the updated attempt with feedback."""
    attempt = crud.exercise_attempt.get(db, id=attempt_id)
    if not attempt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attempt not found",
        )

    # Ensure the user is analyzing their own attempt or is a superuser
    if attempt.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to analyze this attempt",
        )

    if attempt.is_correct:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Analysis is only available for incorrect attempts.",
        )

    feedback = await ai_services.analyze_exercise_attempt(db=db, exercise_attempt_id=attempt_id)

    if feedback is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze the exercise attempt.",
        )
    
    # Re-fetch the attempt to get the updated feedback
    updated_attempt = crud.exercise_attempt.get(db, id=attempt_id)
    return updated_attempt

@router.get("/recommendations", response_model=List[ExerciseInDB])
async def get_recommended_exercises(
    db: Session = Depends(deps.get_db),
    limit: int = 5,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Foydalanuvchi uchun tavsiya etilgan mashqlar ro'yxati."""
    # Foydalanuvchi darajasi va progressi bo'yicha tavsiyalar
    user_level = current_user.get_current_level()
    
    # Oddiy misol: foydalanuvchi darajasiga mos mashqlarni qaytarish
    recommended = crud.exercise.get_multi(
        db,
        skip=0,
        limit=limit,
        difficulty=user_level.value,
        is_active=True
    )
    
    # Agar mos mashq topilmasa, undan past darajadagi mashqlarni taklif qilish
    if not recommended:
        recommended = crud.exercise.get_multi(
            db,
            skip=0,
            limit=limit,
            is_active=True
        )
    
    return recommended
