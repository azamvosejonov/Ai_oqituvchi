from typing import Any, List, Optional, Union, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from app import crud, models, schemas
from app.api.deps import get_db, get_current_active_superuser, get_current_active_user
from app.core.config import settings

router = APIRouter()

# Exercise endpoints
@router.get("/recommendations", response_model=List[schemas.Exercise])
def recommend_exercises(
    *,
    db: Session = Depends(get_db),
    limit: int = 10,
    lesson_id: Optional[int] = None,
    difficulty: Optional[schemas.DifficultyLevel] = None,
    exercise_type: Optional[schemas.ExerciseType] = None,
    tags: Optional[List[str]] = Query(None),
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Foydalanuvchi uchun tavsiya etilgan mashqlar ro'yxati.

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
@router.post("/", response_model=schemas.Exercise, status_code=status.HTTP_201_CREATED)
def create_exercise(
    *,
    db: Session = Depends(get_db),
    exercise_in: schemas.ExerciseCreate,
    current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """
    Create new exercise.
    """
    exercise = crud.exercise.create(db, obj_in=exercise_in)
    return exercise

@router.get("/", response_model=List[schemas.Exercise])
def read_exercises(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    lesson_id: Optional[int] = None,
    difficulty: Optional[schemas.DifficultyLevel] = None,
    exercise_type: Optional[schemas.ExerciseType] = None,
    is_active: Optional[bool] = None,
    tags: Optional[List[str]] = Query(None),
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve exercises with optional filtering.
    """
    exercises = crud.exercise.get_multi_filtered(
        db,
        skip=skip,
        limit=limit,
        lesson_id=lesson_id,
        difficulty=difficulty,
        exercise_type=exercise_type,
        is_active=is_active,
        tags=tags
    )
    return exercises

@router.get("/{exercise_id}", response_model=schemas.Exercise)
def read_exercise(
    *,
    db: Session = Depends(get_db),
    exercise_id: int,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Get exercise by ID.
    """
    exercise = crud.exercise.get(db, id=exercise_id)
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found",
        )
    return exercise

@router.put("/{exercise_id}", response_model=schemas.Exercise)
def update_exercise(
    *,
    db: Session = Depends(get_db),
    exercise_id: int,
    exercise_in: schemas.ExerciseUpdate,
    current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """
    Update an exercise.
    """
    exercise = crud.exercise.get(db, id=exercise_id)
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found",
        )
    exercise = crud.exercise.update(db, db_obj=exercise, obj_in=exercise_in)
    return exercise

@router.delete("/{exercise_id}", response_model=schemas.Exercise)
def delete_exercise(
    *,
    db: Session = Depends(get_db),
    exercise_id: int,
    current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """
    Delete an exercise.
    """
    exercise = crud.exercise.get(db, id=exercise_id)
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found",
        )
    exercise = crud.exercise.remove(db, id=exercise_id)
    return exercise

class ExerciseAnswer(BaseModel):
    answer: Union[str, List, Dict, None] = None
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
    response_description="Detailed feedback about the answer"
)
async def check_exercise_answer(
    *,
    db: Session = Depends(get_db),
    exercise_id: int,
    answer_data: ExerciseAnswer = Body(...),
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Check if the provided answer is correct for the given exercise.
    
    Supports various exercise types including multiple choice, true/false, fill-in-blank,
    matching, short answer, essay, listening, speaking, translation, and dictation.
    
    - **exercise_id**: The ID of the exercise to check
    - **answer**: The user's answer (can be text, list, or dict depending on exercise type)
    - **audio_url**: URL of recorded audio (for speaking/dictation exercises)
    - **language**: Language code for feedback (default: 'uz')
    
    Returns detailed feedback including:
    - is_correct: Whether the answer is completely correct
    - score: A score between 0.0 and 1.0
    - feedback: Detailed feedback on the answer
    - explanation: Explanation of the correct answer (if applicable)
    """
    try:
        result = crud.exercise.check_answer(
            db=db,
            exercise_id=exercise_id,
            user_answer=answer_data.answer,
            user_id=current_user.id,
            audio_url=answer_data.audio_url,
            language=answer_data.language
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        # Log the exception for debugging
        # logger.error(f"Error checking answer for exercise {exercise_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while checking the answer.",
        )


# Exercise Set endpoints
@router.post("/exercise-sets/", response_model=schemas.ExerciseSet, status_code=status.HTTP_201_CREATED)
def create_exercise_set(
    *,
    db: Session = Depends(get_db),
    exercise_set_in: schemas.ExerciseSetCreate,
    current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """
    Create a new exercise set.
    """
    exercise_set = crud.exercise_set.create_with_exercises(
        db, 
        obj_in=exercise_set_in,
        exercise_ids=exercise_set_in.exercise_ids
    )
    return exercise_set

@router.get("/exercise-sets/", response_model=List[schemas.ExerciseSet])
def read_exercise_sets(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve exercise sets.
    """
    exercise_sets = crud.exercise_set.get_multi(db, skip=skip, limit=limit)
    return exercise_sets

@router.get("/exercise-sets/{set_id}", response_model=schemas.ExerciseSet)
def read_exercise_set(
    *,
    db: Session = Depends(get_db),
    set_id: int,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Get exercise set by ID.
    """
    exercise_set = crud.exercise_set.get(db, id=set_id)
    if not exercise_set:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise set not found",
        )
    return exercise_set

@router.put("/exercise-sets/{set_id}", response_model=schemas.ExerciseSet)
def update_exercise_set(
    *,
    db: Session = Depends(get_db),
    set_id: int,
    exercise_set_in: schemas.ExerciseSetUpdate,
    current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """
    Update an exercise set.
    """
    exercise_set = crud.exercise_set.get(db, id=set_id)
    if not exercise_set:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise set not found",
        )
    exercise_set = crud.exercise_set.update(db, db_obj=exercise_set, obj_in=exercise_set_in)
    return exercise_set

@router.delete("/exercise-sets/{set_id}", response_model=schemas.ExerciseSet)
def delete_exercise_set(
    *,
    db: Session = Depends(get_db),
    set_id: int,
    current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """
    Delete an exercise set.
    """
    exercise_set = crud.exercise_set.get(db, id=set_id)
    if not exercise_set:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise set not found",
        )
    exercise_set = crud.exercise_set.remove(db, id=set_id)
    return exercise_set

# Test Session endpoints
@router.post("/test-sessions/", response_model=schemas.TestSession, status_code=status.HTTP_201_CREATED)
def create_test_session(
    *,
    db: Session = Depends(get_db),
    test_session_in: schemas.TestSessionCreate,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Create a new test session.
    """
    test_session = crud.test_session.create_with_exercise_set(
        db,
        obj_in=test_session_in,
        user_id=current_user.id
    )
    return test_session

@router.get("/test-sessions/", response_model=List[schemas.TestSession])
def read_test_sessions(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve test sessions for the current user.
    """
    test_sessions = db.query(models.TestSession).filter(
        models.TestSession.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    return test_sessions

@router.get("/test-sessions/{session_id}", response_model=schemas.TestSession)
def read_test_session(
    *,
    db: Session = Depends(get_db),
    session_id: int,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Get test session by ID.
    """
    test_session = db.query(models.TestSession).filter(
        models.TestSession.id == session_id,
        models.TestSession.user_id == current_user.id
    ).first()
    
    if not test_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test session not found or access denied",
        )
    return test_session

@router.post("/test-sessions/{session_id}/submit-response", response_model=schemas.TestResponse)
def submit_test_response(
    *,
    db: Session = Depends(get_db),
    session_id: int,
    response_in: schemas.TestResponseCreate,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Submit a response for a test question.
    """
    try:
        response = crud.test_session.submit_response(
            db,
            test_session_id=session_id,
            response_in=response_in,
            user_id=current_user.id
        )
        return response
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

@router.post("/test-sessions/{session_id}/submit", response_model=schemas.TestSession)
def submit_test(
    *,
    db: Session = Depends(get_db),
    session_id: int,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Submit a test for grading.
    """
    try:
        test_session = crud.test_session.grade_test(db, test_session_id=session_id)
        return test_session
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

# User Progress endpoints
@router.get("/user-progress/", response_model=List[schemas.UserProgress])
def read_user_progress(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Get progress for the current user.
    """
    progress = db.query(models.UserProgress).filter(
        models.UserProgress.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    return progress

@router.get("/user-progress/{exercise_id}", response_model=schemas.UserProgress)
def read_user_exercise_progress(
    *,
    db: Session = Depends(get_db),
    exercise_id: int,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Get user's progress for a specific exercise.
    """
    progress = db.query(models.UserProgress).filter(
        models.UserProgress.user_id == current_user.id,
        models.UserProgress.exercise_id == exercise_id
    ).first()
    
    if not progress:
        progress = models.UserProgress(
            user_id=current_user.id,
            exercise_id=exercise_id,
            score=0.0,
            completed=False,
            attempts=0
        )
        db.add(progress)
        db.commit()
        db.refresh(progress)
    
    return progress
