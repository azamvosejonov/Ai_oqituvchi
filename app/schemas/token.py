from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime
from .user import User

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    sub: int | None = None
    user: User

    model_config = ConfigDict(
        from_attributes=True,
    )


class TokenWithUser(BaseModel):
    access_token: str
    token_type: str
    user: User


class TokenPayload(BaseModel):
    sub: Optional[int] = None

    model_config = ConfigDict(
        from_attributes=True,
    )


class LoginRequest(BaseModel):
    username: str
    password: str

    model_config = ConfigDict(
        from_attributes=True,
    )


class UserSimple(BaseModel):
    id: int
    username: str
    email: EmailStr
    phone_number: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True,
    )


class LocationInfo(BaseModel):
    ip: str
    country: str
    region: str
    city: str
    timezone: str
    current_time: str
    utc_offset: str
    display_time: str
    login_time: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class UserInResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    phone_number: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True,
    )


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    user: UserInResponse  # bu yerda User — Pydantic schema bo‘lishi kerak

    model_config = ConfigDict(
        from_attributes=True,
    )
