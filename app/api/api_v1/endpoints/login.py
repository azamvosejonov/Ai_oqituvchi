from datetime import datetime, timezone, timedelta
from typing import Any

import pytz
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette import status

from app import crud, models, schemas
from app.api import deps
from app.core.config import settings
from app.core.security import create_access_token
from app.models import User
from app.schemas.token import TokenWithUser

router = APIRouter()

# Tokenning amal qilish muddati (daqiqalarda)
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


@router.post("/login/access-token", response_model=TokenWithUser)
def login_for_access_token(
    response: Response,
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    # Authenticate using email or username
    user = crud.user.authenticate(
        db=db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    # Use the user's ID as the JWT subject; ensure it is a string
    access_token = create_access_token(
        subject=str(user.id), expires_delta=access_token_expires
    )

    # Make Swagger "Try it out" authorized automatically by setting cookie and header
    # 1) Set Authorization header in the HTTP response (for clients that read it)
    response.headers["Authorization"] = f"Bearer {access_token}"
    # 2) Set cookie so our deps.get_current_user can read it on subsequent requests
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        secure=False,
        samesite="lax",
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user,
    }


@router.get("/login/test-token", response_model=schemas.User)
def test_token(current_user: models.User = Depends(deps.get_current_user)) -> Any:
    """
    Test access token
    """
    return current_user


@router.post("/logout")
def logout(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Logout the current user by clearing server-side refresh token data.
    Note: Access tokens are stateless; clients should discard them on logout.
    """
    try:
        crud.user.update(
            db,
            db_obj=current_user,
            obj_in={
                "hashed_refresh_token": None,
                "refresh_token_expires_at": None,
            },
        )
        return {"detail": "Successfully logged out"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Logout failed: {str(e)}")
