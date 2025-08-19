from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.crud.crud_ai_avatar import interactive_lesson

router = APIRouter()


@router.post("/", response_model=schemas.Exercise, status_code=201)
def create_exercise(
    *, 
    db: Session = Depends(deps.get_db),
    exercise_in: schemas.ExerciseCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser)
) -> Any:
    """
    Create new exercise. (Superuser only)
    """
    # Check if interactive lesson exists
    lesson = interactive_lesson.get(db, id=exercise_in.lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail=f"Interactive lesson with id {exercise_in.lesson_id} not found")
    exercise = crud.exercise.create(db=db, obj_in=exercise_in)
    return exercise


@router.get("/", response_model=List[schemas.Exercise])
def read_exercises(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve exercises. (Superuser only)
    """
    exercises = crud.exercise.get_multi(db, skip=skip, limit=limit)
    return exercises


@router.get("/{exercise_id}", response_model=schemas.Exercise)
def read_exercise(
    *,
    db: Session = Depends(deps.get_db),
    exercise_id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Get exercise by ID. (Superuser only)
    """
    exercise = crud.exercise.get(db, id=exercise_id)
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return exercise


@router.put("/{exercise_id}", response_model=schemas.Exercise)
def update_exercise(
    *,
    db: Session = Depends(deps.get_db),
    exercise_id: int,
    exercise_in: schemas.ExerciseUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update an exercise. (Superuser only)
    """
    exercise = crud.exercise.get(db, id=exercise_id)
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    exercise = crud.exercise.update(db, db_obj=exercise, obj_in=exercise_in)
    return exercise


@router.delete("/{exercise_id}", response_model=schemas.Exercise)
def delete_exercise(
    *,
    db: Session = Depends(deps.get_db),
    exercise_id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete an exercise. (Superuser only)
    """
    exercise = crud.exercise.get(db, id=exercise_id)
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    exercise = crud.exercise.remove(db, id=exercise_id)
    return exercise
