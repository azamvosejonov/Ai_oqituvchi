from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session

from app import models, schemas, crud
from app.api import deps
from app.models.user import Role as UserRole

router = APIRouter()


@router.get("/users", response_model=List[schemas.User])
def read_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    role_name: Optional[str] = None,
    current_user: models.User = Depends(deps.get_current_active_superuser),
):
    """
    Retrieve users. (Superuser only)
    """
    users = crud.user.get_multi_by_role(db, skip=skip, limit=limit, role_name=role_name)
    return users


@router.post("/users", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def create_user(
    *, 
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
):
    """
    Create new user. (Superuser only)
    """
    user = crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists in the system.",
        )
    user = crud.user.create(db, obj_in=user_in)
    return user


@router.get("/users/{user_id}", response_model=schemas.User)
def read_user_by_id(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
):
    """
    Get a specific user by ID. (Superuser only)
    """
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.put("/users/{user_id}", response_model=schemas.User)
def update_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    user_in: schemas.UserUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
):
    """
    Update a user. (Superuser only)
    """
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    user = crud.user.update(db, db_obj=user, obj_in=user_in)
    return user


@router.delete("/users/{user_id}", response_model=schemas.User)
def delete_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
):
    """
    Delete a user. (Superuser only)
    """
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    # You can't delete your own superuser account
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Super users can't delete themselves."
        )
    user = crud.user.remove(db, id=user_id)
    return user
