from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("/users", response_model=List[schemas.User])
def read_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    is_premium: bool = Query(None, description="Filter users by premium status"),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve users. Superuser can filter by premium status.
    """
    users = crud.user.get_multi_filtered(db, skip=skip, limit=limit, is_premium=is_premium)
    return users


@router.post("/users", response_model=schemas.User, status_code=201)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create new user (Admin only).
    """
    user = crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    user = crud.user.create(db, obj_in=user_in)
    return user


@router.get("/users/{user_id}", response_model=schemas.User)
def read_user(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Get a specific user by ID (Admin only).
    """
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404, detail="The user with this ID does not exist in the system."
        )
    return user


@router.put("/users/{user_id}", response_model=schemas.User)
def update_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    user_in: schemas.UserUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update a user by ID (Admin only).
    """
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404, detail="The user with this ID does not exist in the system."
        )
    user = crud.user.update(db, db_obj=user, obj_in=user_in)
    return user


@router.delete("/users/{user_id}", response_model=schemas.User)
def delete_user(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete a user (Admin only).
    """
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404, detail="The user with this ID does not exist in the system."
        )
    user = crud.user.remove(db, id=user_id)
    return user
