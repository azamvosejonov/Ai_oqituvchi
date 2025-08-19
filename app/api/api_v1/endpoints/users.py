from datetime import timedelta
from typing import Any, List, Optional
from fastapi.responses import FileResponse
import os

from fastapi import APIRouter, Body, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.core.config import settings
from app.core.security import create_access_token
 

router = APIRouter()


# Temporary stub until email service is integrated
async def send_new_account_email(email_to: str, username: str) -> None:
    """Send a welcome/new account email (stub)."""
    # Integrate real email sending here if/when available.
    return None


@router.get("/", response_model=List[schemas.User])
def read_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve users (Superuser only).
    """
    users = crud.user.get_multi(db, skip=skip, limit=limit)
    return users


@router.get("/me", response_model=schemas.User)
def read_user_me(current_user: models.User = Depends(deps.get_current_active_user)):
    """
    Get current user.
    """
    return current_user


@router.get("/me/premium-data", response_model=schemas.Message)
def read_my_premium_data(
    current_user: models.User = Depends(deps.get_current_active_premium_user),
):
    """
    Fetch premium data for the current user. Requires active subscription.
    (Admins can also access this route)
    """
    return {"msg": f"Hello premium user {current_user.full_name}! Here is your special data."}


@router.get("/me/next-lesson", response_model=schemas.Lesson)
def get_next_lesson(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get the next lesson for the current user to continue learning.
    """
    next_lesson = crud.lesson.get_next_lesson_for_user(db, user_id=current_user.id)
    if not next_lesson:
        raise HTTPException(
            status_code=404,
            detail="No next lesson found. You may have completed all available courses or not started any.",
        )
    return next_lesson


@router.get("/test-superuser", response_model=schemas.Message)
async def test_superuser_endpoint(
    current_user: models.User = Depends(deps.get_current_active_superuser),
):
    """
    Test endpoint that only superusers can access.
    """
    return {"msg": f"Hello superuser {current_user.email}!"}


@router.get("/{user_id}", response_model=schemas.User)
def read_user_by_id(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Get a specific user by ID (Superuser only).
    """
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404, detail="The user with this ID does not exist in the system."
        )
    return user


@router.post("/", response_model=schemas.User)
async def create_user(
    *,
    db: Session = Depends(deps.get_db),
    response: Response,
    user_in: schemas.UserCreate,
) -> Any:
    """
    Create new user.
    """

    user = crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    user = crud.user.create(db, obj_in=user_in)
    
    # Create a 1-day trial subscription for the new user
    crud.subscription.create_trial_subscription(db=db, user_id=user.id)
    
    # Refresh the user object to load the new subscription relationship
    db.refresh(user)

    if settings.EMAILS_ENABLED and user_in.email:
        await send_new_account_email(email_to=user_in.email, username=user_in.email)

    # Auto-authorize newly created user for Swagger and subsequent requests
    try:
        access_token = create_access_token(subject=str(user.id))
        # Set Authorization header in response
        response.headers["Authorization"] = f"Bearer {access_token}"
        # Set HttpOnly cookie so deps.get_current_user can read it
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=True,
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            secure=False,
            samesite="lax",
        )
    except Exception:
        # Do not fail user creation if token setup has an issue
        pass

    return user


@router.put("/{user_id}", response_model=schemas.User)
def update_user_by_admin(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    user_in: schemas.UserUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update a user by ID (Superuser only).
    """
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system",
        )
    # Uniqueness checks to avoid DB IntegrityError
    if user_in.email and user_in.email != user.email:
        existing = crud.user.get_by_email(db, email=user_in.email)
        if existing and existing.id != user.id:
            raise HTTPException(
                status_code=400,
                detail="The user with this email already exists in the system.",
            )

    if user_in.username and user_in.username != user.username:
        existing_u = crud.user.get_by_username(db, username=user_in.username)
        if existing_u and existing_u.id != user.id:
            raise HTTPException(
                status_code=400,
                detail="The user with this username already exists in the system.",
            )

    user = crud.user.update(db, db_obj=user, obj_in=user_in)
    return user

@router.patch("/me", response_model=schemas.User)
async def update_user_me(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update current user's profile.
    """
    user = crud.user.get(db, id=current_user.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if email is being updated and if it's already taken
    if user_in.email and user_in.email != user.email:
        if crud.user.get_by_email(db, email=user_in.email):
            raise HTTPException(
                status_code=400,
                detail="The user with this email already exists in the system.",
            )
    
    # Check if username is being updated and if it's already taken
    if user_in.username and user_in.username != user.username:
        if crud.user.get_by_username(db, username=user_in.username):
            raise HTTPException(
                status_code=400,
                detail="The user with this username already exists in the system.",
            )
    
    # Update the user
    updated_user = crud.user.update(db, db_obj=user, obj_in=user_in)
    return updated_user

@router.delete("/{user_id}", response_model=schemas.User)
def delete_user(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete a user (Superuser only).
    """
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Superusers cannot delete themselves")
    
    deleted_user = crud.user.remove(db, id=user_id)
    return deleted_user


@router.post("/courses/{course_id}/complete", response_model=schemas.Certificate)
def complete_course(
    *,
    db: Session = Depends(deps.get_db),
    course_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """Mark a course as completed and generate a certificate."""
    course = crud.course.get(db, id=course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Check if a certificate already exists
    existing_certificate = crud.certificate.get_by_user_and_course(db, user_id=current_user.id, course_id=course_id)
    if existing_certificate:
        return existing_certificate

    # Verify that the user has completed all lessons in the course
    if not crud.course.is_course_completed(db, user_id=current_user.id, course_id=course_id):
        raise HTTPException(
            status_code=400, 
            detail="You have not completed all lessons in this course yet."
        )

    # Create certificate
    certificate_in = schemas.CertificateCreate(
        title=f"Certificate for {course.title}",
        user_id=current_user.id,
        course_id=course.id,
        course_name=course.title,
        level_completed=course.difficulty_level
    )
    certificate = crud.certificate.create_with_pdf(db, obj_in=certificate_in, user=current_user)

    # Send notification to the user
    if certificate:
        crud.notification.create_certificate_issued_notification(
            db=db,
            user_id=current_user.id,
            course_name=course.title,
            certificate_id=certificate.id
        )

    return certificate


@router.get("/certificates/", response_model=List[schemas.Certificate])
def list_my_certificates(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """Retrieve certificates for the current user."""
    return crud.certificate.get_multi_by_user(db, user_id=current_user.id)


@router.get("/certificates/{certificate_id}")
def download_certificate(
    *,
    db: Session = Depends(deps.get_db),
    certificate_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """Download a certificate PDF."""
    certificate = crud.certificate.get(db, id=certificate_id)
    if not certificate or certificate.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Certificate not found")
    
    if not certificate.file_path or not os.path.exists(certificate.file_path):
        raise HTTPException(status_code=404, detail="Certificate file not available.")

    return FileResponse(certificate.file_path, media_type='application/pdf', filename=f"certificate-{certificate.id}.pdf")
