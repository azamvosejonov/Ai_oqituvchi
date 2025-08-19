#!/usr/bin/env python3
import sys
import time
import json
from typing import Dict, List

import requests
import os

# Import project settings to get superuser credentials
from app.core.config import settings
from app.db.session import SessionLocal
from app import crud, schemas
from app.core.security import get_password_hash
from app.schemas import UserRole

BASE_URL = os.environ.get("PROBE_BASE_URL", "http://0.0.0.0:8004")
OPENAPI_URL = f"{BASE_URL}/api/v1/openapi.json"
LOGIN_URL = f"{BASE_URL}/api/v1/login/access-token"
# Default user creds (kept for reference/testing)
USERNAME = "test@example.com"
PASSWORD = "testpassword"

# Admin creds from settings
ADMIN_USERNAME = settings.FIRST_SUPERUSER
ADMIN_PASSWORD = settings.FIRST_SUPERUSER_PASSWORD

# Endpoints we know are safe and important but may require auth; ensure they are included even if spec parsing skips them
PRIORITY_ENDPOINTS = [
    "/api/v1/users/me",
    "/api/v1/interactive-lessons/",
    "/api/v1/statistics/",
    "/api/v1/forum/topics/",
    "/api/v1/homework/",
    "/api/v1/subscriptions/plans",
    "/api/v1/feedback/",
    "/api/v1/payments/",
    # Admin endpoints (read-only where possible)
    "/api/v1/admin/users/",
    "/api/v1/admin/courses/",
    "/api/v1/admin/statistics",
    "/api/v1/admin/subscription-plans",
]

# Some paths in spec might not end with trailing slash; normalize for requests

def normalize_path(p: str) -> str:
    if not p.startswith("/"):
        p = "/" + p
    # Preserve exact forms for known endpoints, but avoid double slashes
    p = p.replace("//", "/")
    return p


def get_token(username: str, password: str) -> str:
    # FastAPI OAuth2PasswordRequestForm expects application/x-www-form-urlencoded
    data = {"username": username, "password": password}
    r = requests.post(LOGIN_URL, data=data, timeout=20)
    if r.status_code != 200:
        raise RuntimeError(f"LOGIN FAILED ({username}): status={r.status_code} body={r.text}")
    try:
        token = r.json().get("access_token")
    except Exception:
        print(f"LOGIN PARSE FAILED: body={r.text}")
        sys.exit(1)
    if not token:
        print(f"LOGIN NO TOKEN: body={r.text}")
        sys.exit(1)
    return token


def fetch_openapi() -> Dict:
    r = requests.get(OPENAPI_URL, timeout=20)
    if r.status_code != 200:
        print(f"FAILED TO FETCH OPENAPI: status={r.status_code} body={r.text}")
        sys.exit(1)
    try:
        return r.json()
    except Exception as e:
        print(f"OPENAPI JSON PARSE ERROR: {e}")
        sys.exit(1)


def should_skip_operation(path: str, method: str, op: Dict) -> bool:
    # Skip non-GET methods for safety in this probe.
    if method.lower() != "get":
        return True
    # Skip if there are path params required (e.g., /items/{id})
    if "{" in path and "}" in path:
        return True
    # If operation has required parameters in query, we can still try without them; most are optional.
    # If a requestBody is required (rare for GET), skip.
    if op.get("requestBody", {}).get("required"):
        return True
    return False


def collect_get_endpoints(spec: Dict) -> List[str]:
    paths = spec.get("paths", {})
    endpoints: List[str] = []
    for path, ops in paths.items():
        for method, op in ops.items():
            if method.lower() not in {"get", "post", "put", "patch", "delete", "options", "head"}:
                continue
            if should_skip_operation(path, method, op):
                continue
            endpoints.append(normalize_path(path))
    # Ensure priority endpoints are included
    for ep in PRIORITY_ENDPOINTS:
        epn = normalize_path(ep)
        if epn not in endpoints:
            endpoints.append(epn)
    # De-duplicate while preserving order
    seen = set()
    ordered = []
    for ep in endpoints:
        if ep not in seen:
            ordered.append(ep)
            seen.add(ep)
    return ordered


def probe_endpoints(headers: Dict[str, str], endpoints: List[str]) -> None:
    total = len(endpoints)
    print(f"Probing {total} endpoints (GET only, fail-fast)...")
    for i, ep in enumerate(endpoints, start=1):
        url = f"{BASE_URL}{ep}"
        try:
            r = requests.get(url, headers=headers, timeout=30)
        except requests.RequestException as e:
            print(f"[{i}/{total}] {ep} -> REQUEST ERROR: {e}")
            sys.exit(1)
        status = r.status_code
        ok = 200 <= status < 300
        print(f"[{i}/{total}] {ep} -> {status}")
        if not ok:
            # Print a short body snippet for diagnostics
            body = r.text
            if len(body) > 500:
                body = body[:500] + "..."
            print(f"FAILED: {ep} returned {status}. Body: {body}")
            sys.exit(1)
    print("All probed endpoints returned 2xx.")


def assert_2xx(resp, label: str):
    status = resp.status_code
    ok = 200 <= status < 300
    if not ok:
        body = resp.text
        if len(body) > 500:
            body = body[:500] + "..."
        raise RuntimeError(f"{label} failed: status={status} body={body}")


def run_write_tests(headers: Dict[str, str]) -> None:
    import time
    ts = int(time.time())

    # --- Admin Subscription Plan CRUD ---
    plan_payload = {
        "name": f"Probe Plan {ts}",
        "price": 9.99,
        "duration_days": 30,
        "description": "probe plan",
        "stripe_price_id": f"price_probe_{ts}",
        "gpt4o_requests_quota": 10,
        "stt_requests_quota": 20,
        "tts_chars_quota": 3000,
        "pronunciation_analysis_quota": 5,
    }
    r = requests.post(f"{BASE_URL}/api/v1/admin/subscription-plans/", json=plan_payload, headers=headers, timeout=30)
    assert_2xx(r, "Create subscription plan")
    plan = r.json()
    plan_id = plan.get("id")

    r = requests.put(
        f"{BASE_URL}/api/v1/admin/subscription-plans/{plan_id}",
        json={"description": "probe plan updated"},
        headers=headers,
        timeout=30,
    )
    assert_2xx(r, "Update subscription plan")

    r = requests.delete(f"{BASE_URL}/api/v1/admin/subscription-plans/{plan_id}", headers=headers, timeout=30)
    assert_2xx(r, "Delete subscription plan")

    # --- Admin Course CRUD ---
    course_payload = {
        "title": f"Probe Course {ts}",
        "description": "probe course",
        "difficulty_level": "beginner",
        "instructor_id": 0,  # will be overridden server-side
        "is_published": False,
    }
    r = requests.post(f"{BASE_URL}/api/v1/admin/courses/", json=course_payload, headers=headers, timeout=30)
    assert_2xx(r, "Create course")
    course = r.json()
    course_id = course.get("id")

    r = requests.put(
        f"{BASE_URL}/api/v1/admin/courses/{course_id}",
        json={
            "title": f"Probe Course {ts} Updated",
            "difficulty_level": "beginner",
            "description": "probe course updated",
        },
        headers=headers,
        timeout=30,
    )
    assert_2xx(r, "Update course")

    r = requests.delete(f"{BASE_URL}/api/v1/admin/courses/{course_id}", headers=headers, timeout=30)
    assert_2xx(r, "Delete course")

    # --- Admin Users CRUD ---
    user_email = f"probe_user_{ts}@example.com"
    user_payload = {
        "username": user_email,
        "email": user_email,
        "password": "ProbePass123!",
        "full_name": "Probe User",
    }
    r = requests.post(f"{BASE_URL}/api/v1/admin/users", json=user_payload, headers=headers, timeout=30)
    assert_2xx(r, "Create admin user")
    user = r.json()
    user_id = user.get("id")

    # PATCH profile
    r = requests.patch(
        f"{BASE_URL}/api/v1/admin/users/{user_id}/profile",
        json={"full_name": "Probe User Updated", "email": user_email},
        headers=headers,
        timeout=30,
    )
    assert_2xx(r, "Patch admin user profile")

    # DELETE user
    r = requests.delete(f"{BASE_URL}/api/v1/admin/users/{user_id}", headers=headers, timeout=30)
    assert_2xx(r, "Delete admin user")

    # --- Admin Interactive Lesson CRUD (optional: requires at least one avatar) ---
    avatars = requests.get(f"{BASE_URL}/api/v1/avatars/", headers=headers, timeout=30)
    if 200 <= avatars.status_code < 300:
        avatars_list = avatars.json() if avatars.text else []
    else:
        avatars_list = []

    if isinstance(avatars_list, list) and avatars_list:
        avatar_id = avatars_list[0].get("id")
        if not isinstance(avatar_id, int):
            print("[WARN] Skipping interactive lesson CRUD (avatar_id is not integer)")
            return
        lesson_payload = {
            "title": f"Probe Lesson {ts}",
            "order": 1,
            "description": "probe lesson",
            "difficulty": "beginner",
            "is_premium": False,
            "is_active": True,
            "content": {"blocks": []},
            "avatar_id": avatar_id,
        }
        r = requests.post(f"{BASE_URL}/api/v1/admin/interactive-lessons/", json=lesson_payload, headers=headers, timeout=30)
        assert_2xx(r, "Create interactive lesson")
        lesson = r.json()
        lesson_id = lesson.get("id")

        r = requests.put(
            f"{BASE_URL}/api/v1/admin/interactive-lessons/{lesson_id}",
            json={
                "title": f"Probe Lesson {ts} Updated",
                "order": 1,
                "difficulty": "beginner",
                "content": {"blocks": ["updated"]},
            },
            headers=headers,
            timeout=30,
        )
        assert_2xx(r, "Update interactive lesson")

        r = requests.delete(f"{BASE_URL}/api/v1/admin/interactive-lessons/{lesson_id}", headers=headers, timeout=30)
        assert_2xx(r, "Delete interactive lesson")
    else:
        print("[WARN] Skipping interactive lesson CRUD (no avatars available)")

    # --- Forum CRUD (categories/topics/posts) ---
    # Create Category
    category_payload = {
        "name": f"Probe Category {ts}",
        "description": "probe category",
    }
    r = requests.post(
        f"{BASE_URL}/api/v1/forum/categories/",
        json=category_payload,
        headers=headers,
        timeout=30,
    )
    assert_2xx(r, "Create forum category")
    category = r.json()
    category_id = category.get("id")

    # Create Topic (requires category_id and first post content)
    topic_payload = {
        "title": f"Probe Topic {ts}",
        "description": "probe topic",
        "category_id": category_id,
        "content": "Initial post content",
    }
    r = requests.post(
        f"{BASE_URL}/api/v1/forum/topics/",
        json=topic_payload,
        headers=headers,
        timeout=30,
    )
    assert_2xx(r, "Create forum topic")
    topic = r.json()
    topic_id = topic.get("id")

    # Update Topic
    r = requests.put(
        f"{BASE_URL}/api/v1/forum/topics/{topic_id}",
        json={"title": f"Probe Topic {ts} Updated"},
        headers=headers,
        timeout=30,
    )
    assert_2xx(r, "Update forum topic")

    # Create Post (reply)
    post_payload = {
        "topic_id": topic_id,
        "content": "Probe reply content",
    }
    r = requests.post(
        f"{BASE_URL}/api/v1/forum/posts/",
        json=post_payload,
        headers=headers,
        timeout=30,
    )
    assert_2xx(r, "Create forum post")
    post = r.json()
    post_id = post.get("id")

    # Update Post
    r = requests.put(
        f"{BASE_URL}/api/v1/forum/posts/{post_id}",
        json={"content": "Probe reply content updated"},
        headers=headers,
        timeout=30,
    )
    assert_2xx(r, "Update forum post")

    # Delete Post
    r = requests.delete(
        f"{BASE_URL}/api/v1/forum/posts/{post_id}", headers=headers, timeout=30
    )
    assert_2xx(r, "Delete forum post")

    # Delete Topic
    r = requests.delete(
        f"{BASE_URL}/api/v1/forum/topics/{topic_id}", headers=headers, timeout=30
    )
    assert_2xx(r, "Delete forum topic")

    # Delete Category
    r = requests.delete(
        f"{BASE_URL}/api/v1/forum/categories/{category_id}",
        headers=headers,
        timeout=30,
    )
    assert_2xx(r, "Delete forum category")

    # --- Feedback CRUD (current user create/list, admin delete) ---
    feedback_payload = {
        "content": "Probe feedback content",
        "rating": 5,
    }
    r = requests.post(
        f"{BASE_URL}/api/v1/feedback/",
        json=feedback_payload,
        headers=headers,
        timeout=30,
    )
    assert_2xx(r, "Create feedback")
    fb = r.json()
    fb_id = fb.get("id")

    # List feedback (as superuser will see all)
    r = requests.get(f"{BASE_URL}/api/v1/feedback/", headers=headers, timeout=30)
    assert_2xx(r, "List feedback")

    # Delete feedback (superuser only)
    r = requests.delete(
        f"{BASE_URL}/api/v1/feedback/{fb_id}", headers=headers, timeout=30
    )
    assert_2xx(r, "Delete feedback")


def ensure_superuser(db_session):
    # Ensure roles exist
    for role_name in [UserRole.superadmin, UserRole.admin, UserRole.free]:
        role = crud.role.get_by_name(db_session, name=role_name.value)
        if not role:
            role_in = schemas.RoleCreate(name=role_name.value, description=f"{role_name.value.capitalize()} Role")
            crud.role.create(db_session, obj_in=role_in)

    superadmin_role = crud.role.get_by_name(db_session, name=UserRole.superadmin.value)
    user = crud.user.get_by_email(db_session, email=settings.FIRST_SUPERUSER)
    if not user:
        user_in = schemas.UserCreate(
            username=settings.FIRST_SUPERUSER,
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            full_name="Super Admin",
            is_superuser=True,
        )
        user = crud.user.create(db_session, obj_in=user_in)
        user.roles.append(superadmin_role)
        db_session.commit()
    else:
        # Ensure password and role
        user.hashed_password = get_password_hash(settings.FIRST_SUPERUSER_PASSWORD)
        if superadmin_role not in user.roles:
            user.roles.append(superadmin_role)
        if not user.is_superuser:
            user.is_superuser = True
        db_session.add(user)
        db_session.commit()


def main():
    # Prefer admin token to access both user and admin endpoints
    try:
        admin_token = get_token(ADMIN_USERNAME, ADMIN_PASSWORD)
    except Exception as e:
        # Ensure superuser exists, then retry
        print(f"Admin login failed, ensuring superuser exists... ({e})")
        db = SessionLocal()
        try:
            ensure_superuser(db)
        finally:
            db.close()
        admin_token = get_token(ADMIN_USERNAME, ADMIN_PASSWORD)

    headers = {"Authorization": f"Bearer {admin_token}"}
    spec = fetch_openapi()
    endpoints = collect_get_endpoints(spec)
    probe_endpoints(headers, endpoints)
    # After GET probe, run write-operation tests
    run_write_tests(headers)


if __name__ == "__main__":
    main()
