from typing import Optional, List, TYPE_CHECKING
from pydantic import BaseModel, ConfigDict

# Forward reference to break circular import
if TYPE_CHECKING:
    from .user import User

# Shared properties
class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True,
    )

# Properties to receive on role creation
class RoleCreate(RoleBase):
    pass

# Properties to receive on role update
class RoleUpdate(RoleBase):
    pass

# Properties shared by models stored in DB
class RoleInDBBase(RoleBase):
    id: int

    model_config = ConfigDict(
        from_attributes=True,
    )

# Properties to return to client
class Role(RoleInDBBase):
    pass

    model_config = ConfigDict(
        from_attributes=True,
    )

# Properties properties stored in DB
class RoleInDB(RoleInDBBase):
    model_config = ConfigDict(
        from_attributes=True,
    )
