from enum import Enum
from pydantic import BaseModel, EmailStr, ConfigDict, Field, computed_field
from typing import Optional, List
from datetime import date, datetime

from app.schemas.role import Role
from app.schemas.subscription import Subscription


# Shared properties
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False
    full_name: Optional[str] = None
    username: Optional[str] = None
    current_level: Optional[str] = "A1"
    last_viewed_lesson_id: Optional[int] = None

    model_config = ConfigDict(
        from_attributes=True,
    )


# Properties to receive via API on creation
class UserCreate(UserBase):
    email: EmailStr
    username: str
    password: str
    is_teacher: bool = False
    is_superuser: bool = False
    full_name: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True,
    )


# Properties to receive via API on update
class UserUpdate(UserBase):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    current_level: Optional[str] = None
    password: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True,
    )


# Schema for updating user roles
class UserRoleUpdate(BaseModel):
    role_id: int

    model_config = ConfigDict(
        from_attributes=True,
    )


# Schema for updating user profile by admin
class UserUpdateProfile(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None

    model_config = ConfigDict(
        from_attributes=True,
    )


class UserInDBBase(UserBase):
    id: Optional[int] = None
    roles: List[Role] = []

    model_config = ConfigDict(
        from_attributes=True,
    )


# Additional properties to return via API
class User(UserInDBBase):
    roles: List["Role"] = []

    @computed_field
    @property
    def is_premium(self) -> bool:
        # This will need to be adjusted if we don't have roles loaded.
        # For now, this logic might fail. A better approach is needed.
        # Let's assume not premium if roles are not available.
        return False

    model_config = ConfigDict(
        from_attributes=True,
    )


# Additional properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str
    roles: List["Role"] = []

    model_config = ConfigDict(
        from_attributes=True,
    )


# Simple login schema with only username and password
class UserLogin(BaseModel):
    username: str
    password: str

    model_config = ConfigDict(
        from_attributes=True,
    )


class UserWithLessonCount(User):
    lesson_count: int

    model_config = ConfigDict(
        from_attributes=True,
    )


class PasswordChange(BaseModel):
    old_password: str
    new_password: str

    model_config = ConfigDict(
        from_attributes=True,
    )
