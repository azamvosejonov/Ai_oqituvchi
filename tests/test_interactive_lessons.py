from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import crud
from app.core.config import settings
from tests.utils.course import create_test_course
from tests.utils.lesson import create_test_lesson
from tests.utils.user import create_random_user


def test_create_lesson_session(
    client: TestClient, db: Session, superuser_token_headers: dict[str, str]
) -> None:
    """
    Test creating, fetching, and completing a lesson session.
    """
    # Create a test course and lesson
    user = create_random_user(db)
    course = create_test_course(db, instructor_id=user.id)
    lesson = create_test_lesson(db, course_id=course.id)

    # Test creating a new session
    data = {"lesson_id": lesson.id, "status": "in_progress"}
    r = client.post(
        f"{settings.API_V1_STR}/lesson-sessions/",
        headers=superuser_token_headers,
        json=data,
    )
    assert r.status_code == 200
    session = r.json()
    assert session["lesson_id"] == lesson.id
    assert session["status"] == "in_progress"
    assert "id" in session

    # Test getting the session
    r = client.get(
        f"{settings.API_V1_STR}/lesson-sessions/{session['id']}",
        headers=superuser_token_headers,
    )
    assert r.status_code == 200
    assert r.json()["id"] == session["id"]

    # Test completing the session
    r = client.post(
        f"{settings.API_V1_STR}/lesson-sessions/{session['id']}/complete",
        headers=superuser_token_headers,
    )
    assert r.status_code == 200
    completed_session = r.json()
    assert completed_session["status"] == "completed"
    assert completed_session["end_time"] is not None


def test_lesson_interaction(
    client: TestClient, db: Session, superuser_token_headers: dict[str, str]
) -> None:
    """
    Test creating and retrieving lesson interactions.
    """
    # Create a test course and lesson
    user = create_random_user(db)
    course = create_test_course(db, instructor_id=user.id)
    lesson = create_test_lesson(db, course_id=course.id)

    # Create a session first
    session_data = {"lesson_id": lesson.id, "status": "in_progress"}
    r = client.post(
        f"{settings.API_V1_STR}/lesson-sessions/",
        headers=superuser_token_headers,
        json=session_data,
    )
    assert r.status_code == 200
    session = r.json()

    # Test creating an interaction
    interaction_data = {
        "user_input": "Hello, how are you?",
        "ai_response": "I'm an AI, I don't have feelings, but thanks for asking!",
    }
    r = client.post(
        f"{settings.API_V1_STR}/lesson-interactions/{session['id']}/interact",
        headers=superuser_token_headers,
        json=interaction_data,
    )
    assert r.status_code == 200
    interaction = r.json()
    assert interaction["user_input"] == interaction_data["user_input"]
    assert interaction["session_id"] == session["id"]

    # Test getting interactions
    r = client.get(
        f"{settings.API_V1_STR}/lesson-interactions/{session['id']}/interactions",
        headers=superuser_token_headers,
    )
    assert r.status_code == 200
    interactions = r.json()
    assert len(interactions) > 0
    assert interactions[0]["id"] == interaction["id"]


def test_homework_workflow(
    client: TestClient, db: Session, superuser_token_headers: dict[str, str], user_token_headers: dict[str, str]
) -> None:
    """
    Test creating, assigning, submitting, and grading homework.
    """
    # Create a test course and lesson
    user = create_random_user(db)
    course = create_test_course(db, instructor_id=user.id)
    lesson = create_test_lesson(db, course_id=course.id)

    # Create homework (as admin)
    homework_data = {
        "title": "Test Homework",
        "description": "This is a test homework assignment",
        "due_date": (datetime.utcnow() + timedelta(days=7)).isoformat(),
        "difficulty": "medium",
        "content": {"instructions": "Write a short essay"},
        "lesson_id": lesson.id
    }
    
    r = client.post(
        f"{settings.API_V1_STR}/homework/",
        headers=superuser_token_headers,
        json=homework_data
    )
    assert r.status_code == 200
    homework = r.json()
    
    # Assign homework to user (as admin)
    r = client.post(
        f"{settings.API_V1_STR}/homework/assign/{homework['id']}?user_id={user.id}",
        headers=superuser_token_headers
    )
    assert r.status_code == 200
    user_homework = r.json()
    assert user_homework["user_id"] == user.id
    assert user_homework["homework_id"] == homework["id"]
    
    # User submits homework
    submission_data = {
        "submission": {
            "essay": "This is my test submission.",
            "files": ["essay.txt"]
        }
    }
    
    r = client.post(
        f"{settings.API_V1_STR}/homework/submit/{homework['id']}",
        headers=user_token_headers,
        json=submission_data
    )
    assert r.status_code == 200
    updated_homework = r.json()
    assert updated_homework["status"] == "submitted"
    assert updated_homework["submission"] == submission_data["submission"]
    
    # Teacher grades the homework
    grade_data = {
        "feedback": "Good job!",
        "score": 90
    }
    
    r = client.post(
        f"{settings.API_V1_STR}/homework/grade/{updated_homework['id']}",
        headers=superuser_token_headers,
        json=grade_data
    )
    assert r.status_code == 200
    graded_homework = r.json()
    assert graded_homework["status"] == "graded"
    assert graded_homework["feedback"] == grade_data["feedback"]
    assert graded_homework["score"] == grade_data["score"]
    assert graded_homework["graded_at"] is not None
