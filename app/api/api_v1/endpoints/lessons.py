from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.models.user import Role as UserRole

router = APIRouter()


@router.get("/", response_model=List[schemas.Lesson])
def read_lessons(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve lessons.
    """
    lessons = crud.lesson.get_multi(db, skip=skip, limit=limit)
    return lessons

@router.get("/categories")
def get_lesson_categories() -> Any:
    """Return a static list of lesson categories.
    Placed before the dynamic /{id} route to avoid routing conflicts.
    """
    return [
        "general",
        "grammar",
        "vocabulary",
        "listening",
        "speaking",
        "reading",
        "writing",
    ]


@router.post("/", response_model=schemas.Lesson)
def create_lesson(
    *, 
    db: Session = Depends(deps.get_db),
    lesson_in: schemas.LessonCreate,
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Create new lesson.
    """
    course = crud.course.get(db=db, id=lesson_in.course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    is_creator = course.instructor_id == current_user.id
    is_superuser = crud.user.is_superuser(current_user)

    if not is_creator and not is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    lesson = crud.lesson.create(db=db, obj_in=lesson_in)
    return lesson

@router.get("/videos", response_model=List[schemas.Lesson])
def read_video_lessons(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_user_with_free_window),
) -> Any:
    """Retrieve lessons that have video_url set (limited video lessons)."""
    lessons = crud.lesson.get_multi(db, skip=skip, limit=limit)
    return [l for l in lessons if getattr(l, "video_url", None)]

@router.get("/continue", response_model=schemas.Lesson)
def continue_last_lesson(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user_with_free_window),
) -> Any:
    """Return the user's last viewed lesson, or the first available lesson as fallback."""
    last_id = getattr(current_user, "last_viewed_lesson_id", None)
    if last_id:
        lesson = crud.lesson.get(db=db, id=last_id)
        if lesson:
            return lesson
    # Fallback: first non-premium lesson
    lessons = crud.lesson.get_multi(db, skip=0, limit=1)
    if lessons:
        return lessons[0]
    raise HTTPException(status_code=404, detail="No lessons available")


@router.put("/{id}", response_model=schemas.Lesson)
def update_lesson(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    lesson_in: schemas.LessonUpdate,
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Update a lesson.
    """
    lesson = crud.lesson.get(db=db, id=id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    course = crud.course.get(db=db, id=lesson.course_id)
    
    is_creator = course.instructor_id == current_user.id
    is_superuser = crud.user.is_superuser(current_user)

    if not is_creator and not is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    lesson = crud.lesson.update(db=db, db_obj=lesson, obj_in=lesson_in)
    return lesson


@router.get("/{id}", response_model=schemas.Lesson)
def read_lesson(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_user_with_free_window),
) -> Any:
    """Get lesson by ID."""
    lesson = crud.lesson.get(db=db, id=id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    # Check if the lesson is for premium users only
    if lesson.is_premium:
        is_premium = crud.user.is_premium(current_user)
        is_superuser = crud.user.is_superuser(current_user)
        if not is_premium and not is_superuser:
            raise HTTPException(
                status_code=403,
                detail="This lesson is only available for premium users."
            )

    # Update last viewed lesson for the user
    crud.user.update(db, db_obj=current_user, obj_in={"last_viewed_lesson_id": id})

    return lesson


@router.delete("/{id}", response_model=schemas.Lesson)
def delete_lesson(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Delete a lesson.
    """
    lesson = crud.lesson.get(db=db, id=id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    course = crud.course.get(db=db, id=lesson.course_id)

    is_creator = course.instructor_id == current_user.id
    is_superuser = crud.user.is_superuser(current_user)

    if not is_creator and not is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    lesson = crud.lesson.remove(db=db, id=id)
    return lesson
