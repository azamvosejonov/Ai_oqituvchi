import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.core.config import settings
from tests.utils.course import create_test_course
from tests.utils.lesson import create_test_lesson


# --- Test API Endpoints ---

def test_check_answer_endpoint(
    client: TestClient, db: Session, power_user: models.User, power_user_token_headers: dict
) -> None:
    """Test checking a user's answer via the API endpoint."""
    # A course and lesson are needed for an exercise
    course = create_test_course(db, instructor_id=power_user.id)
    lesson = create_test_lesson(db, course_id=course.id)

    # Create an exercise
    exercise_in = schemas.ExerciseCreate(
        lesson_id=lesson.id,
        exercise_type="multiple_choice",
        question="What is 2+2?",
        options={"A": "3", "B": "4", "C": "5"},
        correct_answer="B"
    )
    exercise = crud.exercise.create(db, obj_in=exercise_in)
    assert exercise

    # 1. Test correct answer
    correct_payload = {"answer": "B"}
    response_correct = client.post(
        f"{settings.API_V1_STR}/exercises/{exercise.id}/check-answer",
        headers=power_user_token_headers,
        json=correct_payload,
    )
    assert response_correct.status_code == 200, response_correct.text
    data_correct = response_correct.json()
    assert data_correct["is_correct"] is True
    assert data_correct["score"] == 1.0

    # 2. Test incorrect answer
    incorrect_payload = {"answer": "A"}
    response_incorrect = client.post(
        f"{settings.API_V1_STR}/exercises/{exercise.id}/check-answer",
        headers=power_user_token_headers,
        json=incorrect_payload,
    )
    assert response_incorrect.status_code == 200, response_incorrect.text
    data_incorrect = response_incorrect.json()
    assert data_incorrect["is_correct"] is False
    assert data_incorrect["score"] == 0.0
    assert "To'g'ri javob" in data_incorrect["feedback"]

    # 3. Test invalid answer (not in options)
    invalid_payload = {"answer": "D"}
    response_invalid = client.post(
        f"{settings.API_V1_STR}/exercises/{exercise.id}/check-answer",
        headers=power_user_token_headers,
        json=invalid_payload,
    )
    # The CRUD function raises a ValueError for invalid options, which should result in a 400 or 404 error.
    assert response_invalid.status_code in [400, 404]


def test_check_answer_endpoint_unauthorized(client: TestClient, db: Session, power_user: models.User) -> None:
    """Test that checking an answer requires authentication."""
    course = create_test_course(db, instructor_id=power_user.id)
    lesson = create_test_lesson(db, course_id=course.id)
    exercise_in = schemas.ExerciseCreate(
        lesson_id=lesson.id, exercise_type="multiple_choice", question="What is 2+2?", options={"A": "3", "B": "4"}, correct_answer="B"
    )
    exercise = crud.exercise.create(db, obj_in=exercise_in)

    # Attempt to check answer without authentication headers
    response = client.post(f"{settings.API_V1_STR}/exercises/{exercise.id}/check-answer", json={"answer": "B"})
    assert response.status_code == 401  # Expect Unauthorized
