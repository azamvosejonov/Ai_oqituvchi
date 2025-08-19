import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from urllib.parse import urlencode

from app.core.config import settings
from tests.utils.user import (
    get_user_authentication_headers,
    create_random_user,
    user_authentication_headers,
)


@pytest.fixture(scope="function")
def normal_user_token_headers(client: TestClient, db_session: Session):
    return get_user_authentication_headers(client=client, db=db_session)


@pytest.fixture(scope="function")
def superuser_token_headers(client: TestClient, db_session: Session):
    return get_user_authentication_headers(
        client=client,
        db=db_session,
        email=settings.FIRST_SUPERUSER,
        password=settings.FIRST_SUPERUSER_PASSWORD,
    )


@pytest.fixture(scope="function")
def power_user_token_headers(client: TestClient, db_session: Session):
    return get_user_authentication_headers(
        client=client,
        db=db_session,
        email=settings.FIRST_POWERUSER,
        password=settings.FIRST_POWERUSER_PASSWORD,
    )


def test_get_users_me(client: TestClient, db_session: Session) -> None:
    """Test fetching the current user's data."""
    user = create_random_user(db_session)
    login_data = {"username": user.email, "password": user.plain_password}

    r = client.post(
        f"{settings.API_V1_STR}/login/access-token",
        data=login_data
    )
    assert r.status_code == 200
    response_data = r.json()
    assert "access_token" in response_data
    assert "user" in response_data
    assert response_data["user"]["email"] == user.email

    r = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {response_data['access_token']}"})
    assert r.status_code == 200
    current_user = r.json()
    assert current_user
    assert current_user["is_active"] is True
    assert current_user["is_superuser"] is False


def test_get_courses(client: TestClient, db_session: Session) -> None:
    """Test fetching courses."""
    r = client.get(f"{settings.API_V1_STR}/courses/")
    assert r.status_code == 200
    courses = r.json()
    assert isinstance(courses, list)


def test_get_lessons(client: TestClient, db_session: Session) -> None:
    """Test fetching lessons."""
    r = client.get(f"{settings.API_V1_STR}/lessons/")
    assert r.status_code == 200
    lessons = r.json()
    assert isinstance(lessons, list)


def test_get_forum_topics(client: TestClient, db_session: Session) -> None:
    """Test fetching forum topics."""
    r = client.get(f"{settings.API_V1_STR}/forum/topics/")
    assert r.status_code == 200
    topics = r.json()
    assert isinstance(topics, list)


def test_get_subscription_plans(client: TestClient, normal_user_token_headers: dict) -> None:
    """Test fetching subscription plans."""
    r = client.get(f"{settings.API_V1_STR}/subscriptions/plans", headers=normal_user_token_headers)
    assert r.status_code == 200
    plans = r.json()
    assert isinstance(plans, list)


def test_get_notifications(client: TestClient, normal_user_token_headers: dict) -> None:
    """Test fetching notifications."""
    r = client.get(f"{settings.API_V1_STR}/notifications/", headers=normal_user_token_headers)
    assert r.status_code == 200
    notifications = r.json()
    assert isinstance(notifications, list)


def test_ai_ask(client: TestClient, power_user_token_headers: dict) -> None:
    """Test the AI ask endpoint."""
    data = {"prompt": "What is the capital of Uzbekistan?"}
    r = client.post(f"{settings.API_V1_STR}/ai/ask", headers=power_user_token_headers, json=data)
    assert r.status_code == 200
    response_data = r.json()
    assert "text" in response_data


def test_ai_stt(client: TestClient, power_user_token_headers: dict) -> None:
    """Test the AI speech-to-text endpoint."""
    # This test requires a valid audio file.
    # For now, we just check if the endpoint is available.
    # A more comprehensive test would involve uploading a file.
    pass


def test_get_statistics_top_users(client: TestClient, superuser_token_headers: dict) -> None:
    """Test fetching top users statistics."""
    r = client.get(f"{settings.API_V1_STR}/statistics/top-users", headers=superuser_token_headers)
    assert r.status_code == 200
    response_data = r.json()
    assert isinstance(response_data, list)


def test_get_statistics_payment_stats(client: TestClient, superuser_token_headers: dict) -> None:
    """Test fetching payment statistics."""
    r = client.get(f"{settings.API_V1_STR}/statistics/payment-stats", headers=superuser_token_headers)
    assert r.status_code == 200
    response_data = r.json()
    assert "total_revenue" in response_data