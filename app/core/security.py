from datetime import datetime, timedelta, timezone
from typing import Any, Union, Optional, Generator
import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import SessionLocal
from app import schemas
from app.core import deps

# Exception for invalid credentials
credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

# OAuth2 scheme
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Database dependency
def get_db() -> Generator:
    """Get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta = None, token_type: str = "access"
) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject), "type": token_type}
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def create_refresh_token(subject: Union[str, Any]) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {
        "exp": expire,
        "sub": str(subject),  # Cast subject to string
        "jti": str(uuid.uuid4()),  # Unique identifier for the token
        "type": "refresh"
    }
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def get_current_user(
    db: Session = Depends(deps.get_db), token: str = Depends(reusable_oauth2)
) -> Any:
    """Get the current user from the JWT token."""
    from app import models, crud
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        token_type = payload.get("type", "access")
        if token_type != "access":
            raise credentials_exception
            
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except (jwt.JWTError, ValidationError):
        raise credentials_exception
    
    user = db.query(models.User).filter(models.User.id == user_id).first()

    if user is None:
        raise credentials_exception
    return user


def get_current_active_user(
    current_user: Any = Depends(get_current_user),
) -> Any:
    from app import crud
    if not crud.user.is_active(current_user):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_current_active_superuser(
    current_user: Any = Depends(get_current_user),
) -> Any:
    from app import crud
    if not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user
