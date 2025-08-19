from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

# Shared properties
class CertificateBase(BaseModel):
    title: str
    user_id: int
    course_id: Optional[int] = None
    course_name: str
    level_completed: Optional[str] = None
    description: Optional[str] = None
    verification_code: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True,
    )

# Properties to receive on item creation
class CertificateCreate(CertificateBase):
    model_config = ConfigDict(
        from_attributes=True,
    )

# Properties to receive on item update
class CertificateUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    expiry_date: Optional[datetime] = None
    is_valid: Optional[bool] = None
    file_path: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True,
    )

# Properties shared by models stored in DB
class CertificateInDBBase(CertificateBase):
    id: int
    issue_date: datetime
    verification_code: str
    is_valid: bool
    file_path: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True,
    )

# Properties to return to client
class Certificate(CertificateInDBBase):
    model_config = ConfigDict(
        from_attributes=True,
    )

# Properties stored in DB
class CertificateInDB(CertificateInDBBase):
    model_config = ConfigDict(
        from_attributes=True,
    )
