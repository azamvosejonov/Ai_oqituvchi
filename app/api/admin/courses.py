from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas, crud
from app.api import deps

router = APIRouter()

@router.post("/", response_model=schemas.Course)
def create_course(
    *, 
    db: Session = Depends(deps.get_db),
    course_in: schemas.CourseCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
):
    """
    Create a new course. (Admin only)
    """
    course = crud.course.create_with_instructor(db=db, obj_in=course_in, instructor_id=current_user.id)
    return course

@router.put("/{course_id}", response_model=schemas.Course)
def update_course(
    *, 
    db: Session = Depends(deps.get_db),
    course_id: int,
    course_in: schemas.CourseUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
):
    """
    Update a course. (Admin only)
    """
    course = crud.course.get(db, id=course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )
    course = crud.course.update(db, db_obj=course, obj_in=course_in)
    return course

@router.delete("/{course_id}", response_model=schemas.Course)
def delete_course(
    *, 
    db: Session = Depends(deps.get_db),
    course_id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
):
    """
    Delete a course. (Admin only)
    """
    course = crud.course.get(db, id=course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )
    course = crud.course.remove(db, id=course_id)
    return course
