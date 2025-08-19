import sys
import os

from app.schemas import UserRole

# Add project root to the Python path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)

import asyncio
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app import crud, schemas, models
from app.core.config import settings
from app.core.security import get_password_hash

def create_superuser(db: Session) -> None:
    print("Ensuring roles exist...")
    # Ensure superadmin, admin, and free roles exist
    for role_name in [UserRole.superadmin, UserRole.admin, UserRole.free]:
        role = crud.role.get_by_name(db, name=role_name.value)
        if not role:
            role_in = schemas.RoleCreate(name=role_name.value, description=f"{role_name.value.capitalize()} Role")
            crud.role.create(db, obj_in=role_in)
            print(f"Role '{role_name.value}' created.")

    print("Creating/Updating superuser...")
    superadmin_role = crud.role.get_by_name(db, name=UserRole.superadmin.value)

    user_in = schemas.UserCreate(
        username=settings.FIRST_SUPERUSER,
        email=settings.FIRST_SUPERUSER,
        password=settings.FIRST_SUPERUSER_PASSWORD,
        full_name="Super Admin",
        is_superuser=True, # Keep for compatibility
    )
    user = crud.user.get_by_email(db, email=user_in.email)
    if not user:
        user = crud.user.create(db, obj_in=user_in)
        user.roles.append(superadmin_role)
        db.commit()
        print(f"Superuser '{user.email}' created successfully with 'superadmin' role.")
    else:
        print(f"User '{user.email}' already exists. Ensuring superuser status and role.")
        # Update password to ensure it's in sync with settings
        user.hashed_password = get_password_hash(settings.FIRST_SUPERUSER_PASSWORD)

        # Ensure user is superuser
        if not user.is_superuser:
            user.is_superuser = True
        
        # Ensure user has the superadmin role
        if superadmin_role not in user.roles:
            user.roles.append(superadmin_role)

        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"User '{user.email}' is now a superuser with 'superadmin' role.")
        print(f"User '{settings.FIRST_SUPERUSER_PASSWORD}' is now a superuser with 'superadmin' role.")

if __name__ == "__main__":
    print("Running superuser creation/update script...")
    db = SessionLocal()
    create_superuser(db)
    db.close()
    print("Script finished.")
