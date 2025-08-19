import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app import crud, schemas, models
from app.core.config import settings
from tests.utils.course import create_test_course
from tests.utils.lesson import create_test_lesson
from tests.utils.homework import create_random_homework


@pytest.fixture  # function scope (default) to match `db` fixture
def homework_setup(db: Session, power_user: models.User):
    """Provides a course, lesson, and homework for tests."""
    course = create_test_course(db, instructor_id=power_user.id)
    lesson = create_test_lesson(db, course_id=course.id)
    homework: models.Homework = create_random_homework(db, lesson_id=lesson.id, course_id=course.id, teacher_id=power_user.id)
    return {"course": course, "lesson": lesson, "homework": homework}


def test_create_homework(
    client: TestClient, power_user_token_headers: dict, db: Session, power_user: models.User
):
    """Test creating a new homework assignment as a teacher."""
    course = create_test_course(db, instructor_id=power_user.id)
    lesson = create_test_lesson(db, course_id=course.id)

    homework_data = {
        "title": "New Written Homework",
        "description": "Write an essay.",
        "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
        "lesson_id": lesson.id,
        "course_id": course.id,
        "homework_type": "written"
    }

    response = client.post(
        f"{settings.API_V1_STR}/homework/",
        headers=power_user_token_headers,
        json=homework_data,
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["title"] == homework_data["title"]
    assert data["lesson_id"] == lesson.id
    assert data["teacher_id"] == power_user.id


def test_get_homework(
    client: TestClient, power_user_token_headers: dict, homework_setup: dict
):
    """Test retrieving a specific homework assignment."""
    homework = homework_setup["homework"]
    response = client.get(
        f"{settings.API_V1_STR}/homework/{homework.id}",
        headers=power_user_token_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == homework.id
    assert data["title"] == homework.title


def test_assign_homework_to_student(
    client: TestClient, db: Session, power_user_token_headers: dict, test_user: models.User, homework_setup: dict
):
    """Test assigning homework to a specific student."""
    homework = homework_setup["homework"]
    assign_data = {"student_ids": [test_user.id]}

    response = client.post(
        f"{settings.API_V1_STR}/homework/{homework.id}/assign",
        headers=power_user_token_headers,
        json=assign_data,
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["student_id"] == test_user.id
    assert data[0]["homework_id"] == homework.id
    assert data[0]["status"] == "assigned"


def test_student_submit_homework(
    client: TestClient, db: Session, test_user_token_headers: dict, test_user: models.User, homework_setup: dict, power_user_token_headers: dict
):
    """Test a student submitting their homework."""
    homework = homework_setup["homework"]
    # First, assign the homework to the student
    client.post(
        f"{settings.API_V1_STR}/homework/{homework.id}/assign",
        headers=power_user_token_headers,
        json={"student_ids": [test_user.id]},
    )

    submission_data = {"text_answer": "This is my completed essay."}
    response = client.post(
        f"{settings.API_V1_STR}/homework/{homework.id}/submit",
        headers=test_user_token_headers,
        json=submission_data,
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["student_id"] == test_user.id
    assert data["status"] == "submitted"
    assert data["text_answer"] == submission_data["text_answer"]


def test_teacher_grade_homework(
    client: TestClient, db: Session, power_user_token_headers: dict, test_user: models.User, test_user_token_headers: dict, homework_setup: dict
):
    """Test a teacher grading a student's submission."""
    homework = homework_setup["homework"]
    # Assign and submit homework
    client.post(f"{settings.API_V1_STR}/homework/{homework.id}/assign", headers=power_user_token_headers, json={"student_ids": [test_user.id]})
    submission_response = client.post(f"{settings.API_V1_STR}/homework/{homework.id}/submit", headers=test_user_token_headers, json={"text_answer": "Submission content"})
    submission_id = submission_response.json()["id"]

    grading_data = {"grade": 95.5, "feedback": "Excellent work!"}
    response = client.post(
        f"{settings.API_V1_STR}/homework/submissions/{submission_id}/grade",
        headers=power_user_token_headers,
        json=grading_data,
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["status"] == "graded"
    assert data["grade"] == grading_data["grade"]
    assert data["feedback"] == grading_data["feedback"]


def test_get_user_homework_submissions(
    client: TestClient, test_user_token_headers: dict, test_user: models.User, homework_setup: dict, power_user_token_headers: dict
):
    """Test retrieving all homework submissions for the current user."""
    homework = homework_setup["homework"]
    # Assign and submit
    client.post(f"{settings.API_V1_STR}/homework/{homework.id}/assign", headers=power_user_token_headers, json={"student_ids": [test_user.id]})
    client.post(f"{settings.API_V1_STR}/homework/{homework.id}/submit", headers=test_user_token_headers, json={"text_answer": "My first submission"})

    response = client.get(
        f"{settings.API_V1_STR}/homework/submissions/me",
        headers=test_user_token_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["student_id"] == test_user.id
