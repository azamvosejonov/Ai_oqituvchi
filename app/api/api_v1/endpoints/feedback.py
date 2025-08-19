from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.post("/", response_model=schemas.Feedback, status_code=201)
def create_feedback(
    *,
    db: Session = Depends(deps.get_db),
    feedback_in: schemas.FeedbackCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new feedback.
    """
    feedback = crud.feedback.create_with_owner(
        db=db, obj_in=feedback_in, user_id=current_user.id
    )
    return feedback


@router.get("/", response_model=List[schemas.Feedback])
def read_feedback(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve feedback.
    - Regular users can see their own feedback.
    - Admins can see all feedback.
    """
    if crud.user.is_superuser(current_user):
        feedback = crud.feedback.get_multi(db)
    else:
        feedback = crud.feedback.get_multi_by_user(
            db=db, user_id=current_user.id
        )
    return feedback


@router.delete("/{id}", response_model=schemas.Feedback)
def delete_feedback(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete a feedback by ID. Only for superusers.
    """
    feedback = crud.feedback.get(db=db, id=id)
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    feedback = crud.feedback.remove(db=db, id=id)
    return feedback
