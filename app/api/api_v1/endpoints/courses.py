from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.Course])
def read_courses(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve courses.
    """
    courses = crud.course.get_multi(db, skip=skip, limit=limit)
    return courses


@router.post("/", response_model=schemas.Course)
def create_course(
    *, 
    db: Session = Depends(deps.get_db),
    course_in: schemas.CourseCreate,
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Create new course.
    """
    course = crud.course.create_with_instructor(db=db, obj_in=course_in, instructor_id=current_user.id)
    return course


@router.put("/{id}", response_model=schemas.Course)
def update_course(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    course_in: schemas.CourseUpdate,
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Update a course.
    """
    course = crud.course.get(db=db, id=id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    is_creator = course.instructor_id == current_user.id
    is_superuser = crud.user.is_superuser(current_user)

    if not is_creator and not is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    course = crud.course.update(db=db, db_obj=course, obj_in=course_in)
    return course


@router.get("/{id}", response_model=schemas.Course)
def read_course(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
) -> Any:
    """
    Get course by ID.
    """
    course = crud.course.get(db=db, id=id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.delete("/{id}", response_model=schemas.Course)
def delete_course(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Delete a course.
    """
    course = crud.course.get(db=db, id=id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    is_creator = course.instructor_id == current_user.id
    is_superuser = crud.user.is_superuser(current_user)

    if not is_creator and not is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Prepare sanitized response before deletion to avoid lazy-load on detached instance
    resp = {
        "id": course.id,
        "title": getattr(course, "title", None),
        "description": getattr(course, "description", None),
        "short_description": getattr(course, "short_description", None),
        "thumbnail_url": getattr(course, "thumbnail_url", None),
        "is_published": getattr(course, "is_published", False),
        "is_featured": getattr(course, "is_featured", False),
        "difficulty_level": getattr(course, "difficulty_level", None),
        "estimated_duration": getattr(course, "estimated_duration", None),
        "language": getattr(course, "language", None),
        "price": getattr(course, "price", None),
        "discount_price": getattr(course, "discount_price", None),
        "instructor_id": getattr(course, "instructor_id", None),
        "category": getattr(course, "category", None),
        "tags": getattr(course, "tags", None),
        "requirements": getattr(course, "requirements", None),
        "learning_outcomes": getattr(course, "learning_outcomes", None),
        "created_at": getattr(course, "created_at", None),
        "updated_at": getattr(course, "updated_at", None),
        "instructor": None,
        "lessons": [],
    }

    # Delete and commit
    db.delete(course)
    db.commit()
    return resp
