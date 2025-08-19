from typing import Any, Dict, Optional, Union
from datetime import datetime, timedelta

from sqlalchemy.orm import Session, joinedload

from app.models import User, Role
from app.schemas import UserRole as UserRoleSchema
from app.schemas.user import UserCreate, UserUpdate
from app.crud.base import CRUDBase
from app import models, schemas
from app.crud import crud_subscription
from app.crud.crud_role import role as crud_role
from app.crud.crud_user_ai_usage import user_ai_usage
import logging
from app.schemas import UserRole

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        return db.query(self.model).options(joinedload(self.model.roles)).filter(self.model.email == email).first()

    def get_by_username(self, db: Session, *, username: str) -> Optional[User]:
        return db.query(User).options(joinedload(User.roles)).filter(User.username == username).first()

    def authenticate(
        self, db: Session, *, email: str, password: str
    ) -> User | None:
        """
        Authenticate a user by email/username and password.
        """
        from app.core.security import verify_password

        # Try to get user by email first
        logger.info(f"authenticate() called with identifier={email}")
        user = self.get_by_email(db, email=email)
        logger.info(f"Lookup by email -> {'found' if user else 'not found'}")
        
        # If not found by email, try by username
        if not user:
            user = db.query(models.User).options(joinedload(models.User.roles)).filter(models.User.username == email).first()
            logger.info(f"Lookup by username -> {'found' if user else 'not found'}")

        if not user:
            logger.info("No user found during authentication")
            return None
        is_valid = verify_password(password, user.hashed_password)
        logger.info(f"Password verify -> {'ok' if is_valid else 'failed'}")
        if not is_valid:
            return None
        return user

    def is_admin(self, user: models.User) -> bool:
        """Checks if a user is an admin or superadmin."""
        admin_roles = {UserRoleSchema.admin.value, UserRoleSchema.superadmin.value}
        user_roles = {role.name for role in user.roles}
        return not admin_roles.isdisjoint(user_roles)

    def get_multi_by_role(
        self, db: Session, *, skip: int = 0, limit: int = 100, role_name: Optional[str] = None
    ) -> list[User]:
        query = db.query(self.model)
        if role_name:
            query = query.join(models.User.roles).filter(models.Role.name == role_name)
        return query.offset(skip).limit(limit).all()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100, role: Optional[UserRoleSchema] = None
    ) -> list[User]:
        query = db.query(self.model)
        if role:
            query = query.join(User.roles).filter(Role.name == role.value)
        return query.offset(skip).limit(limit).all()

    def get_multi_filtered(
        self, db: Session, *, skip: int = 0, limit: int = 100, is_premium: bool | None = None
    ) -> list[User]:
        query = db.query(self.model)
        if is_premium is not None:
            query = query.filter(self.model.is_premium == is_premium)
        return query.offset(skip).limit(limit).all()

    def assign_role_to_user(self, db: Session, *, user: User, role: Role):
        """Assign a role to a user."""
        user.roles.append(role)
        db.add(user)
        db.commit()
        db.refresh(user)

    def assign_default_role(self, db: Session, *, user: User) -> None:
        """Assign the default 'free' role to a user."""
        role = crud_role.get_by_name(db, name="free")
        if role:
            user.roles.append(role)
            db.add(user)
            db.commit()
            db.refresh(user)

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        from app.core.security import get_password_hash

        # Ensure username fits DB constraints (VARCHAR(50))
        username = obj_in.username or (obj_in.email.split('@')[0] if obj_in.email else None)
        if username is None or username.strip() == "":
            username = f"user{datetime.utcnow().timestamp():.0f}"
        if len(username) > 50:
            username = username[:50]

        db_obj = User(
            email=obj_in.email,
            username=username,
            hashed_password=get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
            is_superuser=obj_in.is_superuser,
            is_teacher=obj_in.is_teacher,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        # Attach transient plain password for tests (not persisted)
        try:
            db_obj.plain_password = obj_in.password  # type: ignore[attr-defined]
        except Exception:
            pass
        return db_obj

    def update(
        self, db: Session, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        if "password" in update_data and update_data["password"] is not None:
            from app.core.security import get_password_hash
            hashed_password = get_password_hash(update_data["password"])
            db_obj.hashed_password = hashed_password
            # Mirror transient plain password for tests
            try:
                db_obj.plain_password = update_data["password"]  # type: ignore[attr-defined]
            except Exception:
                pass

        # Handle role updates separately
        if "roles" in update_data and update_data["roles"] is not None:
            role_names = update_data.pop("roles", [])
            db_obj.roles = [crud_role.get_or_create(db, name=name) for name in role_names]

        # Manually update the user object's attributes
        for field, value in update_data.items():
            if value is not None:
                setattr(db_obj, field, value)

        # Now, call the super().update with the remaining data
        return super().update(db, db_obj=db_obj, obj_in={})

    def update_refresh_token(self, db: Session, *, user: User, refresh_token: str):
        user.refresh_token = refresh_token

    def is_active(self, user: User) -> bool:
        return user.is_active

    def is_superuser(self, user: User) -> bool:
        return user.is_superuser

    def has_role(self, user: User, role_name: str) -> bool:
        return any(role.name == role_name for role in user.roles)

    def is_premium(self, user: User) -> bool:
        return self.has_role(user, "premium")

    def get_count(self, db: Session) -> int:
        return db.query(self.model).count()


user = CRUDUser(User)
