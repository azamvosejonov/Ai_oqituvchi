import random
import string
from typing import Any, Dict
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app import crud, schemas
from app.core.config import settings

def random_lower_string() -> str:
    """Generate a random string in lowercase"""
    return "".join(random.choices(string.ascii_lowercase, k=10))

def random_email() -> str:
    """Generate a random email"""
    return f"{random_lower_string()}@{random_lower_string()}.com"

def random_phone() -> str:
    """Generate a random phone number"""
    return f"+998{random.randint(90, 99)}{random.randint(1000000, 9999999)}"

def authentication_token_from_email(
    *, client: TestClient, email: str, db: Session
) -> Dict[str, str]:
    """
    Return a valid token for the user with given email.

    If the user doesn't exist it is created first.
    """
    password = "planned-obsolescence"
    user = crud.user.get_by_email(db, email=email)
    if not user:
        user_in_create = schemas.UserCreate(email=email, password=password, full_name="Test User")
        user = crud.user.create(db, obj_in=user_in_create)

    data = {"username": email, "password": password}
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=data)
    response = r.json()
    return {"access_token": response["access_token"], "token_type": "bearer"}

def get_superuser_token_headers(client: TestClient, db: Session) -> Dict[str, str]:
    """Get superuser token headers for testing"""
    user = crud.user.get_by_email(db, email=settings.FIRST_SUPERUSER)
    if not user:
        user_in = schemas.UserCreate(
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
