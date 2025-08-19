from typing import Any, Dict
import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.core.config import settings
from app.core.security import verify_password

router = APIRouter()


@router.get("/me", response_model=schemas.User)
def get_me(current_user: models.User = Depends(deps.get_current_active_user)) -> Any:
    """Get current user's profile"""
    return current_user


@router.patch("/me", response_model=schemas.User)
def update_me(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """Update current user's profile (full_name/email/username)"""
    # Email uniqueness check
    if user_in.email and user_in.email != current_user.email:
        if crud.user.get_by_email(db, email=user_in.email):
            raise HTTPException(status_code=400, detail="Email is already taken")
    # Username uniqueness check
    if user_in.username and user_in.username != current_user.username:
        if crud.user.get_by_username(db, username=user_in.username):
            raise HTTPException(status_code=400, detail="Username is already taken")
    updated = crud.user.update(db, db_obj=current_user, obj_in=user_in)
    return updated


@router.get("/stats", response_model=Dict[str, Any])
def my_stats(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """Return self statistics: completed lessons, certificates, premium, unread notifications."""
    completed = crud.user_lesson_completion.get_completed_lessons_count_for_user(db, user_id=current_user.id)
    cert_count = len(crud.certificate.get_multi_by_user(db, user_id=current_user.id))
    unread = crud.notification.get_unread_count(db, user_id=current_user.id)
    return {
        "completed_lessons": completed,
        "certificates": cert_count,
        "is_premium": crud.user.is_premium(current_user),
        "level": getattr(current_user, "current_level", "A1"),
        "unread_notifications": unread,
    }


@router.post("/change-password", response_model=schemas.Message)
def change_password(
    *,
    db: Session = Depends(deps.get_db),
    payload: schemas.PasswordChange,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """Change current user's password (verify old, set new)."""
    if not verify_password(payload.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Old password is incorrect")
    crud.user.update(db, db_obj=current_user, obj_in={"password": payload.new_password})
    return {"msg": "Password changed successfully"}


@router.post("/avatar", response_model=Dict[str, Any])
async def upload_avatar(
    *,
    file: UploadFile = File(...),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Upload profile image and return its URL.
    Note: User model currently has no avatar field; persistence can be added later via migration.
    """
    # Ensure directory
    base_dir = settings.UPLOAD_DIR if hasattr(settings, "UPLOAD_DIR") else "uploads"
    profile_dir = os.path.join(base_dir, "profile")
    os.makedirs(profile_dir, exist_ok=True)

    ext = os.path.splitext(file.filename or "")[1].lower() or ".jpg"
    fname = f"{current_user.id}_{uuid.uuid4().hex}{ext}"
    path = os.path.join(profile_dir, fname)

    content = await file.read()
    with open(path, "wb") as f:
        f.write(content)

    url = f"/uploads/profile/{fname}"
    return {"url": url}
