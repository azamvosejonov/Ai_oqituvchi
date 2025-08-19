from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.post("/", response_model=schemas.Lesson, status_code=201)
def create_lesson(
    *, 
    db: Session = Depends(deps.get_db),
    lesson_in: schemas.LessonCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser)
) -> Any:
    """
    Create new lesson. (Superuser only)
    """
    # Check if course exists
    course = crud.course.get(db, id=lesson_in.course_id)
    if not course:
        raise HTTPException(status_code=404, detail=f"Course with id {lesson_in.course_id} not found")
    lesson = crud.lesson.create(db=db, obj_in=lesson_in)
    return lesson


@router.get("/", response_model=List[schemas.InteractiveLesson])
def read_lessons(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve lessons. (Superuser only)
    """
    try:
        lessons = crud.lesson.get_multi(db, skip=skip, limit=limit)
        return lessons
    except Exception as e:
        # Fallback to empty list if there's an error
        return []


@router.get("/{lesson_id}", response_model=schemas.InteractiveLesson)
def read_lesson(
    *,
    db: Session = Depends(deps.get_db),
    lesson_id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Get lesson by ID. (Superuser only)
    """
    lesson = crud.lesson.get(db, id=lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return lesson


@router.put("/{lesson_id}", response_model=schemas.InteractiveLesson)
def update_lesson(
    *,
    db: Session = Depends(deps.get_db),
    lesson_id: int,
    lesson_in: schemas.LessonUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update a lesson. (Superuser only)
    """
    lesson = crud.lesson.get(db, id=lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    lesson = crud.lesson.update(db, db_obj=lesson, obj_in=lesson_in)
    return lesson


@router.delete("/{lesson_id}", response_model=schemas.InteractiveLesson)
def delete_lesson(
    *,
    db: Session = Depends(deps.get_db),
    lesson_id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete a lesson. (Superuser only)
    """
    lesson = crud.lesson.get(db, id=lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    lesson = crud.lesson.remove(db, id=lesson_id)
    return lesson
