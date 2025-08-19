import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.user import User


def check_user_roles(user_id: int):
    engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            print(f"User with ID {user_id} not found.")
            return

        print(f"Checking roles for User ID: {user.id}, Email: {user.email}")
        print(f"Is Superuser: {user.is_superuser}")

        if user.roles:
            role_names = [role.name for role in user.roles]
            print(f"Assigned roles: {role_names}")
        else:
            print("No roles assigned to this user.")

    finally:
        db.close()

if __name__ == "__main__":
    # Check roles for the superuser (ID=1)
    check_user_roles(1)
