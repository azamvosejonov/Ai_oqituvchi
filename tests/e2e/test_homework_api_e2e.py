from datetime import datetime, timedelta
from pathlib import Path

import pytest
from app.core.config import settings

BASE = f"{settings.API_V1_STR}/homework"
COURSES_BASE = f"{settings.API_V1_STR}/courses"


def _make_course_payload(instructor_id: int) -> dict:
    return {
        "title": "E2E Test Course",
        "difficulty_level": "beginner",
        # CourseCreate requires instructor_id in schema, even if route overrides it
        "instructor_id": instructor_id,
    }


def _make_homework_payload(course_id: int) -> dict:
    return {
        "title": "E2E Homework",
        "description": "Write a short paragraph.",
        "instructions": "Please write 2-3 sentences about your day.",
        "due_date": (datetime.utcnow() + timedelta(days=7)).isoformat(),
        "course_id": course_id,
        # homework_type omitted -> defaults to written per schema
    }


def test_homework_end_to_end(
    client,
    power_user_token_headers,
    test_user,
    test_user_token_headers,
):
    # 1) Create a course as power user
    course_payload = _make_course_payload(instructor_id=0)
    r = client.post(COURSES_BASE + "/", json=course_payload, headers=power_user_token_headers)
    assert r.status_code == 200, r.text
    course = r.json()
    assert "id" in course

    # 2) Create a homework (written) as power user
    hw_payload = _make_homework_payload(course_id=course["id"])
    r = client.post(BASE + "/", json=hw_payload, headers=power_user_token_headers)
    assert r.status_code == 200, r.text
    hw = r.json()
    assert "id" in hw
    hw_id = hw["id"]

    # 3) Assign homework to a single user (compat endpoint)
    r = client.post(f"{BASE}/assign/{hw_id}", params={"user_id": test_user.id}, headers=power_user_token_headers)
    assert r.status_code == 200, r.text
    assign_resp = r.json()
    assert isinstance(assign_resp, dict)
    assert assign_resp.get("homework_id") == hw_id

    # 4) Submit homework as the test user
    submit_payload = {"text_answer": "Today I studied FastAPI testing. It was productive."}
    r = client.post(f"{BASE}/{hw_id}/submit", json=submit_payload, headers=test_user_token_headers)
    assert r.status_code == 200, r.text
    submission_resp = r.json()
    assert submission_resp.get("status") == "submitted"
    submission_id = submission_resp.get("id")
    assert submission_id is not None

    # 5) Grade the submission (compat endpoint) as power user
    grade_payload = {"score": 95, "feedback": "Excellent job!"}
    r = client.post(f"{BASE}/grade/{submission_id}", json=grade_payload, headers=power_user_token_headers)
    assert r.status_code == 200, r.text
    graded = r.json()
    assert graded.get("status") == "graded"
    assert graded.get("feedback") == "Excellent job!"

    # 6) The student should see their submissions in /user/me
    r = client.get(f"{BASE}/user/me", headers=test_user_token_headers)
    assert r.status_code == 200
    items = r.json()
    assert isinstance(items, list)
    assert any(it.get("homework_id") == hw_id for it in items)

    # 7) Fetch homework by ID and list endpoint
    r = client.get(f"{BASE}/{hw_id}", headers=test_user_token_headers)
    assert r.status_code == 200
    r = client.get(f"{BASE}/", headers=test_user_token_headers)
    assert r.status_code == 200
    assert isinstance(r.json(), list)
