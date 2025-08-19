from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.models.user import Role as UserRole

router = APIRouter()


@router.get("/", response_model=List[schemas.Word])
def read_words(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve words.
    """
    words = crud.word.get_multi(db, skip=skip, limit=limit)
    return words


@router.post("/", response_model=schemas.Word)
def create_word(
    *, 
    db: Session = Depends(deps.get_db),
    word_in: schemas.WordCreate,
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Create new word.
    """
    lesson = crud.lesson.get(db=db, id=word_in.lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    course = crud.course.get(db=db, id=lesson.course_id)

    is_creator = course.instructor_id == current_user.id
    is_superuser = crud.user.is_superuser(current_user)

    if not is_creator and not is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    word = crud.word.create(db=db, obj_in=word_in)
    return word


@router.put("/{id}", response_model=schemas.Word)
def update_word(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    word_in: schemas.WordUpdate,
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Update a word.
    """
    word = crud.word.get(db=db, id=id)
    if not word:
        raise HTTPException(status_code=404, detail="Word not found")
    # Determine permissions safely even if lesson or course is missing
    is_superuser = crud.user.is_superuser(current_user)
    lesson = crud.lesson.get(db=db, id=word.lesson_id) if getattr(word, "lesson_id", None) is not None else None
    course = (
        crud.course.get(db=db, id=lesson.course_id)
        if lesson is not None and getattr(lesson, "course_id", None) is not None
        else None
    )

    is_creator = bool(course and course.instructor_id == current_user.id)

    if not is_superuser and not is_creator:
        # If we can't resolve course/creator and user is not superuser, forbid
        raise HTTPException(status_code=403, detail="Not enough permissions")

    word = crud.word.update(db=db, db_obj=word, obj_in=word_in)
    return word


@router.patch("/{id}", response_model=schemas.Word)
def partial_update_word(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    word_in: schemas.WordUpdate,
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Partially update a word.
    """
    word = crud.word.get(db=db, id=id)
    if not word:
        raise HTTPException(status_code=404, detail="Word not found")
    # Determine permissions safely even if lesson or course is missing
    is_superuser = crud.user.is_superuser(current_user)
    lesson = crud.lesson.get(db=db, id=word.lesson_id) if getattr(word, "lesson_id", None) is not None else None
    course = (
        crud.course.get(db=db, id=lesson.course_id)
        if lesson is not None and getattr(lesson, "course_id", None) is not None
        else None
    )

    is_creator = bool(course and course.instructor_id == current_user.id)

    if not is_superuser and not is_creator:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    word = crud.word.update(db=db, db_obj=word, obj_in=word_in)
    return word


@router.get("/{id}", response_model=schemas.Word)
def read_word(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
) -> Any:
    """
    Get word by ID.
    """
    word = crud.word.get(db=db, id=id)
    if not word:
        raise HTTPException(status_code=404, detail="Word not found")
    return word


@router.delete("/{id}", response_model=schemas.Word)
def delete_word(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Delete a word.
    """
    word = crud.word.get(db=db, id=id)
    if not word:
        raise HTTPException(status_code=404, detail="Word not found")
    # Determine permissions safely even if lesson or course is missing
    is_superuser = crud.user.is_superuser(current_user)
    lesson = crud.lesson.get(db=db, id=word.lesson_id) if getattr(word, "lesson_id", None) is not None else None
    course = (
        crud.course.get(db=db, id=lesson.course_id)
        if lesson is not None and getattr(lesson, "course_id", None) is not None
        else None
    )

    is_creator = bool(course and course.instructor_id == current_user.id)

    if not is_superuser and not is_creator:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    word = crud.word.remove(db=db, id=id)
    return word
