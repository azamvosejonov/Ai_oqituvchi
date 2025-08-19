from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.post("/", response_model=schemas.Course, status_code=201)
def create_course(
    *, 
    db: Session = Depends(deps.get_db),
    course_in: schemas.CourseCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser)
) -> Any:
    """
    Create new course. (Superuser only)
    """
    course = crud.course.create_with_instructor(db=db, obj_in=course_in, instructor_id=current_user.id)
    return course


@router.get("/", response_model=List[schemas.Course])
def read_courses(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve courses. (Superuser only)
    """
    courses = crud.course.get_multi(db, skip=skip, limit=limit)
    return courses


@router.get("/{course_id}", response_model=schemas.Course)
def read_course(
    *,
    db: Session = Depends(deps.get_db),
    course_id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Get course by ID. (Superuser only)
    """
    course = crud.course.get(db, id=course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.put("/{course_id}", response_model=schemas.Course)
def update_course(
    *,
    db: Session = Depends(deps.get_db),
    course_id: int,
    course_in: schemas.CourseUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update a course. (Superuser only)
    """
    course = crud.course.get(db, id=course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    course = crud.course.update(db, db_obj=course, obj_in=course_in)
    return course


@router.delete("/{course_id}", response_model=schemas.Course)
def delete_course(
    *,
    db: Session = Depends(deps.get_db),
    course_id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete a course. (Superuser only)
    """
    course = crud.course.get(db, id=course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    course = crud.course.remove(db, id=course_id)
    return course
