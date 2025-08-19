from pydantic import BaseModel, EmailStr, ConfigDict
from app.schemas import UserRole
from typing import Optional


class UserUpdateAdmin(BaseModel):
    """Schema for updating a user's role by an admin."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None

    model_config = ConfigDict(
        from_attributes=True,
    )
