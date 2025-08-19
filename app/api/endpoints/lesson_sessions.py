from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.core.config import settings
from app.schemas.lesson_session import LessonSession, LessonSessionCreate, LessonSessionUpdate, LessonSessionBase

router = APIRouter()


@router.post("/", response_model=LessonSession)
def create_lesson_session(
    *,
    db: Session = Depends(deps.get_db),
    session_in: LessonSessionBase,
    current_user: models.User = Depends(deps.get_current_user_with_free_window),
):
    """
    Create new lesson session.
    """
    # Check if user already has an active session for this lesson
    active_session = crud.lesson_session.get_active_session(
        db, user_id=current_user.id, lesson_id=session_in.lesson_id
    )
    if active_session:
        return active_session
    
    # Create new session
    create_in = LessonSessionCreate(**session_in.model_dump(), user_id=current_user.id)
    return crud.lesson_session.create(db, obj_in=create_in)


@router.get("/{session_id}", response_model=LessonSession)
def read_lesson_session(
    *,
    db: Session = Depends(deps.get_db),
    session_id: int,
    current_user: models.User = Depends(deps.get_current_user_with_free_window),
):
    """
    Get lesson session by ID.
    """
    session = crud.lesson_session.get(db, id=session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Check if user owns this session
    if session.user_id != current_user.id and not crud.user.is_superuser(current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return session


@router.get("/user/me", response_model=List[LessonSession])
def read_user_lesson_sessions(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_user_with_free_window),
):
    """
    Retrieve lesson sessions for current user.
    """
    return crud.lesson_session.get_multi_by_user(
        db, user_id=current_user.id, skip=skip, limit=limit
    )


@router.put("/{session_id}", response_model=LessonSession)
def update_lesson_session(
    *,
    db: Session = Depends(deps.get_db),
    session_id: int,
    session_in: LessonSessionUpdate,
    current_user: models.User = Depends(deps.get_current_user_with_free_window),
):
    """
    Update a lesson session.
    """
    session = crud.lesson_session.get(db, id=session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Check if user owns this session
    if session.user_id != current_user.id and not crud.user.is_superuser(current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return crud.lesson_session.update(db, db_obj=session, obj_in=session_in)


@router.post("/{session_id}/complete", response_model=LessonSession)
def complete_lesson_session(
    *,
    db: Session = Depends(deps.get_db),
    session_id: int,
    current_user: models.User = Depends(deps.get_current_user_with_free_window),
):
    """
    Mark a lesson session as completed.
    """
    session = crud.lesson_session.get(db, id=session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Check if user owns this session
    if session.user_id != current_user.id and not crud.user.is_superuser(current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Mark as completed
    return crud.lesson_session.complete_session(db, db_obj=session)
