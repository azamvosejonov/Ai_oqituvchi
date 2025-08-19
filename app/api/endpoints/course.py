from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas, crud
from app.api import deps
from app.services import recommendation_service

router = APIRouter()

@router.get("/", response_model=List[schemas.Course])
def get_courses(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Retrieve all courses.
    """
    courses = crud.course.get_multi(db, skip=skip, limit=limit)
    return courses

@router.get("/{course_id}", response_model=schemas.Course)
def get_course(
    course_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Get a specific course by ID.
    """
    course = crud.course.get(db, id=course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    return course

@router.get("/{course_id}/lessons", response_model=List[schemas.Lesson])
def get_course_lessons(
    course_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Get all lessons for a specific course.
    """
    course = crud.course.get(db, id=course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Get lessons for the course
    lessons = crud.lesson.get_multi_by_course(
        db, course_id=course_id, skip=skip, limit=limit
    )
    return lessons

@router.get("/lessons/recommended", response_model=List[schemas.Lesson])
def get_recommended_lessons_endpoint(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    limit: int = 10,
):
    """
    Get recommended lessons for the current user based on their level.
    """
    lessons = recommendation_service.get_recommended_lessons(
        db=db, user=current_user, limit=limit
    )
    if not lessons:
        # Optional: Add fallback logic if no lessons are found at the current level
        pass
    return lessons
