import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from typing import Dict

from app import crud
from app.core.config import settings
from tests.utils.user import create_random_user, get_user_authentication_headers
from tests.utils.utils import random_email, random_lower_string


# Basic test to ensure the file is picked up by pytest
def test_initialization():
    assert True


# Test Login Endpoints
def test_login_for_access_token(client: TestClient, db_session: Session) -> None:
    user = create_random_user(db_session)
    login_data = {"username": user.email, "password": user.plain_password}
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    assert r.status_code == 200, r.text
    tokens = r.json()
    assert "access_token" in tokens
    assert tokens["access_token"]


def test_test_token(client: TestClient, db_session: Session) -> None:
    headers = get_user_authentication_headers(client=client, db=db_session)
    r = client.get(f"{settings.API_V1_STR}/login/test-token", headers=headers)
    assert r.status_code == 200
    assert "email" in r.json()


# Test Users Endpoints
def test_read_users(superuser_token_headers: Dict[str, str], client: TestClient) -> None:
    r = client.get(f"{settings.API_V1_STR}/admin/users/", headers=superuser_token_headers)
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_create_user(client: TestClient, superuser_token_headers: dict) -> None:
    email = random_email()
    password = random_lower_string()
    data = {"email": email, "password": password, "full_name": "Test New User", "username": email.split('@')[0]}
    r = client.post(f"{settings.API_V1_STR}/users/", headers=superuser_token_headers, json=data)
    assert r.status_code == 200, r.text
    created_user = r.json()
    assert created_user["email"] == email
    assert created_user["is_active"] is True


def test_read_user_me(client: TestClient, db_session: Session) -> None:
    headers = get_user_authentication_headers(client=client, db=db_session)
    r = client.get(f"{settings.API_V1_STR}/users/me", headers=headers)
    assert r.status_code == 200, r.text
    assert "email" in r.json()


def test_update_user_me(client: TestClient, db_session: Session) -> None:
    headers = get_user_authentication_headers(client=client, db=db_session)
    new_full_name = "Updated Test User"
    data = {"full_name": new_full_name}
    r = client.patch(f"{settings.API_V1_STR}/users/me", json=data, headers=headers)
    assert r.status_code == 200, r.text
    assert r.json()["full_name"] == new_full_name


def test_read_user_by_id(client: TestClient, superuser_token_headers: dict, db_session: Session) -> None:
    user = create_random_user(db_session)
    r = client.get(f"{settings.API_V1_STR}/admin/users/{user.id}", headers=superuser_token_headers)
    assert r.status_code == 200
    assert r.json()["email"] == user.email


def test_update_user_by_admin(client: TestClient, superuser_token_headers: dict, db_session: Session) -> None:
    user = create_random_user(db_session)
    new_email = "new_test@example.com"
    data = {"email": new_email, "full_name": "Updated Name"}
    r = client.patch(f"{settings.API_V1_STR}/admin/users/{user.id}", json=data, headers=superuser_token_headers)
    assert r.status_code == 200
    assert r.json()["email"] == new_email


def test_delete_user(client: TestClient, superuser_token_headers: dict, db_session: Session) -> None:
    user = create_random_user(db_session)
    response = client.delete(f"{settings.API_V1_STR}/users/{user.id}", headers=superuser_token_headers)
    assert response.status_code == 200
    deleted_user = response.json()
    assert deleted_user
    assert deleted_user['id'] == user.id

    # Verify the user is actually deleted from the db
    deleted_db_user = crud.user.get(db=db_session, id=user.id)
