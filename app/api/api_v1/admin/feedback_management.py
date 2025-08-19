from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.Feedback])
def read_feedback(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve user feedback. (Superuser only)
    """
    feedback_list = crud.feedback.get_multi(db, skip=skip, limit=limit)
    return feedback_list


@router.delete("/{feedback_id}", response_model=schemas.Feedback)
def delete_feedback(
    *,
    db: Session = Depends(deps.get_db),
    feedback_id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete user feedback. (Superuser only)
    """
    feedback = crud.feedback.get(db, id=feedback_id)
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    feedback = crud.feedback.remove(db, id=feedback_id)
    return feedback
