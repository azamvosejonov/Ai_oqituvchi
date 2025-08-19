from typing import List

from fastapi import Depends, HTTPException

from app import models
from app.api import deps


class RoleChecker:
    def __init__(self, allowed_roles: List):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: models.User = Depends(deps.get_current_active_user)):
        if not current_user.role:
            raise HTTPException(status_code=403, detail="User has no role assigned")

        if current_user.role.name not in self.allowed_roles:
            raise HTTPException(status_code=403, detail="The user does not have adequate privileges")

        return current_user
