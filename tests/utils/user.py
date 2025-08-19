import random
import string
from typing import Dict

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import crud
from app.core.config import settings
from app.core.security import get_password_hash
from app.models import User, Role
from app.schemas import UserCreate


def random_lower_string(length: int = 32) -> str:
    """Generate a random string of fixed length."""
    return "".join(random.choices(string.ascii_lowercase, k=length))

def random_email() -> str:
    """Generate a random email."""
    return f"{random_lower_string()}@{random_lower_string()}.com"

def assign_default_role_to_user(db: Session, user: User):
    """Assigns the default 'free' role to a new user."""
    role = crud.role.get_by_name(db, name="free")
    if not role:
        raise ValueError("Default 'free' role not found. Ensure roles are seeded.")
    crud.user.assign_role_to_user(db=db, user=user, role=role)

def create_random_user(db: Session) -> User:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(username=email, email=email, password=password)
    user = crud.user.create(db=db, obj_in=user_in)
    crud.user.assign_default_role(db=db, user=user)
    return user

def get_user_authentication_headers(
    *, client: TestClient, db: Session, email: str = None, password: str = None
) -> Dict[str, str]:
    if not email or not password:
        user = create_random_user(db)
        email = user.email
        password = user.plain_password

    login_data = {
        "username": email,
        "password": password,
    }
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    response = r.json()
    auth_token = response["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}
    return headers


def user_authentication_headers(client: TestClient, db: Session, email: str, password: str) -> Dict[str, str]:
    """Return user authentication headers after logging in."""
    return get_user_authentication_headers(client=client, db=db, email=email, password=password)

def get_superuser_token_headers(client: TestClient, db: Session) -> Dict[str, str]:
    """Get superuser token headers for testing"""
    user = crud.user.get_by_email(db, email=settings.FIRST_SUPERUSER)
    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        crud.user.create(db, obj_in=user_in)

    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers
