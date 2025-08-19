from typing import Optional

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models import Role
from app.schemas import RoleCreate, RoleUpdate


class CRUDRole(CRUDBase[Role, RoleCreate, RoleUpdate]):
    @staticmethod
    def get_by_name(db: Session, *, name: str) -> Optional[Role]:
        return db.query(Role).filter(Role.name == name).first()

    def get_or_create(self, db: Session, *, name: str) -> Role:
        role = CRUDRole.get_by_name(db, name=name)
        if not role:
            role_in = RoleCreate(name=name, description=f"{name.capitalize()} Role")
            role = self.create(db, obj_in=role_in)
        return role

role = CRUDRole(Role)
