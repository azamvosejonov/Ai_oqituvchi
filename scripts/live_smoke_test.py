import os
import sys
from typing import Dict, List, Tuple

import httpx

BASE = os.getenv("LIVE_BASE_URL", "http://localhost:8000")
API = "/api/v1"
TIMEOUT = 30.0

# Candidate test credentials (will try in order). Prefer values from environment/.env
ENV_FIRST_SUPERUSER = os.getenv("FIRST_SUPERUSER")
ENV_FIRST_SUPERUSER_PASSWORD = os.getenv("FIRST_SUPERUSER_PASSWORD")

CREDENTIALS: List[Tuple[str, str]] = []
if ENV_FIRST_SUPERUSER and ENV_FIRST_SUPERUSER_PASSWORD:
    CREDENTIALS.append((ENV_FIRST_SUPERUSER, ENV_FIRST_SUPERUSER_PASSWORD))

# Common known defaults in this repo
CREDENTIALS.extend([
    ("admin@example.com", "changethis"),  # from .env
    ("test@example.com", "testpassword"),  # from defaults
    ("poweruser@example.com", "powerpassword"),
])

# Endpoint spec: (method, path, requires_auth, payload_type, payload)
# payload_type: "json" | "form" | None
ENDPOINTS: List[Tuple[str, str, bool, str, Dict]] = [
    # Auth
    ("POST", f"{API}/login/access-token", False, "form", {"username": "__CRED_USERNAME__", "password": "__CRED_PASSWORD__"}),
    ("GET", f"{API}/login/test-token", True, None, {}),
    ("POST", f"{API}/logout", True, None, {}),

    # Users (read-only/safe)
    ("GET", f"{API}/users/me", True, None, {}),
    ("GET", f"{API}/users/me/premium-data", True, None, {}),
    ("GET", f"{API}/users/me/next-lesson", True, None, {}),
    ("GET", f"{API}/users/test-superuser", True, None, {}),  # expect 200/403 depending on role
    ("GET", f"{API}/users/", True, None, {}),  # admin-only, 200/403 acceptable
    ("GET", f"{API}/users/certificates/", True, None, {}),

    # Subscription plans (public + admin)
    ("GET", f"{API}/subscription-plans/", False, None, {}),

    # Subscriptions
    ("GET", f"{API}/subscriptions/plans", False, None, {}),
    ("GET", f"{API}/subscriptions/status", True, None, {}),
    ("GET", f"{API}/subscriptions/", True, None, {}),  # admin list
    ("GET", f"{API}/subscriptions/me", True, None, {}),
    ("GET", f"{API}/subscriptions/admin/config-check", True, None, {}),

    # Courses & lessons
    ("GET", f"{API}/courses/", False, None, {}),
    ("GET", f"{API}/lessons/", False, None, {}),
    ("GET", f"{API}/lessons/categories", False, None, {}),
    ("GET", f"{API}/lessons/videos", False, None, {}),
    ("GET", f"{API}/lessons/continue", True, None, {}),

    # Words
    ("GET", f"{API}/words/", False, None, {}),

    # Statistics
    ("GET", f"{API}/statistics/", True, None, {}),
    ("GET", f"{API}/statistics/top-users", True, None, {}),
    ("GET", f"{API}/statistics/payment-stats", True, None, {}),

    # User progress (read-only safe)
    ("GET", f"{API}/user-progress/", True, None, {}),
    ("GET", f"{API}/user-progress/last", True, None, {}),

    # Certificates (read-safe)
    ("GET", f"{API}/certificates/my-certificates", True, None, {}),

    # Feedback (read)
    ("GET", f"{API}/feedback/", True, None, {}),

    # Forum (read)
    ("GET", f"{API}/forum/categories/", False, None, {}),
    ("GET", f"{API}/forum/topics/", False, None, {}),

    # AI basic
    ("GET", f"{API}/ai/tts/voices", False, None, {}),
    ("GET", f"{API}/ai/stt/languages", False, None, {}),
    ("POST", f"{API}/ai/analyze-answer", False, "json", {"user_response": "hello", "reference_text": "hello", "language": "en"}),
    ("GET", f"{API}/ai/usage", True, None, {}),

    # AI sessions (read lists)
    ("GET", f"{API}/ai-sessions/sessions", True, None, {}),

    # Notifications (read)
    ("GET", f"{API}/notifications/", True, None, {}),
    ("GET", f"{API}/notifications/unread-count", True, None, {}),

    # Tests (public/read)
    ("GET", f"{API}/tests/ielts", False, None, {}),
    ("GET", f"{API}/tests/toefl", False, None, {}),
    ("GET", f"{API}/tests/", False, None, {}),

    # Admin (read-only; expect 200/403)
    ("GET", f"{API}/admin/statistics", True, None, {}),
    ("GET", f"{API}/admin/users", True, None, {}),
    ("GET", f"{API}/admin/subscription-plans/", True, None, {}),
    ("GET", f"{API}/admin/courses/", True, None, {}),
    ("GET", f"{API}/admin/interactive-lessons/", True, None, {}),

    # Content (read)
    ("GET", f"{API}/content/lessons/validate", True, None, {}),
    ("GET", f"{API}/content/lessons-json", True, None, {}),
    ("GET", f"{API}/content/lessons", True, None, {}),
    ("GET", f"{API}/content/media", True, None, {}),

    # Profile
    ("GET", f"{API}/profile/me", True, None, {}),
    ("GET", f"{API}/profile/stats", True, None, {}),

    # Pronunciation (read)
    ("GET", f"{API}/pronunciation/phrases/", True, None, {}),
    ("GET", f"{API}/pronunciation/sessions/", True, None, {}),
    ("GET", f"{API}/pronunciation/history/", True, None, {}),
    ("GET", f"{API}/pronunciation/profile/", True, None, {}),

    # Interactive lessons (read)
    ("GET", f"{API}/interactive-lessons/", False, None, {}),
    ("GET", f"{API}/interactive-lessons/1", False, None, {}),  # lesson id 1 likely exists

    # Lesson sessions (read)
    ("GET", f"{API}/lesson-sessions/user/me", True, None, {}),

    # Homework (read-only safe)
    ("GET", f"{API}/homework/", True, None, {}),
    ("GET", f"{API}/homework/user/me", True, None, {}),
    ("GET", f"{API}/homework/submissions/me", True, None, {}),

    # Payments (read)
    ("GET", f"{API}/payments/", True, None, {}),

    # Avatars & metrics (mixed)
    ("GET", f"{API}/avatars/", True, None, {}),  # auth required on this instance
    ("GET", f"{API}/metrics", True, None, {}),   # requires auth → send token
    ("GET", f"{API}/metrics/health", False, None, {}),  # public healthcheck
    ("GET", f"{API}/metrics/status", True, None, {}),   # requires auth → send token

    # Recommendations (read)
    ("GET", f"{API}/recommendations/next-lessons", True, None, {}),
    ("GET", f"{API}/recommendations/personalized", True, None, {}),
    ("GET", f"{API}/recommendations/for-you", True, None, {}),

    # Exercises (read)
    ("GET", f"{API}/exercises/", False, None, {}),
]

ALLOWED_STATUSES_WITH_AUTH = {200, 204}
ALLOWED_STATUSES_PUBLIC = {200, 204}
# For endpoints that might need elevated privileges, accept 401/403 as non-fatal
ALSO_OK_FOR_PROTECTED = {401, 403}


def try_login(client: httpx.Client) -> Dict[str, str]:
    for username, password in CREDENTIALS:
        try:
            resp = client.post(
                f"{BASE}{API}/login/access-token",
                data={"username": username, "password": password},
                timeout=TIMEOUT,
            )
            if resp.status_code == 200:
                token = resp.json().get("access_token")
                if token:
                    print(f"[AUTH] Logged in as {username}")
                    return {"Authorization": f"Bearer {token}"}
        except Exception as e:
            print(f"[AUTH] Error logging in with {username}: {e}")
    print("[AUTH] Could not obtain token. Protected endpoints may return 401/403.")
    return {}


def main() -> int:
    print(f"[INFO] Live smoke test targeting: {BASE}")

    ok = 0
    fail = 0
    results = []

    with httpx.Client(base_url=BASE, timeout=TIMEOUT, follow_redirects=True) as client:
        auth_headers = try_login(client)

        for method, path, requires_auth, payload_type, payload in ENDPOINTS:
            url = path
            headers = auth_headers.copy() if requires_auth else {}

            # If this is the login endpoint spec in the list, fill credentials dynamically
            if path.endswith("/login/access-token") and payload_type == "form":
                # Use first successful credential if we have token
                if auth_headers:
                    # Skip re-login when already authenticated
                    status = 200
                    results.append((method, url, status, "SKIPPED (already authed)"))
                    ok += 1
                    continue
                else:
                    # Try first candidate, otherwise will fail
                    username, password = CREDENTIALS[0]
                    payload = {"username": username, "password": password}

            try:
                if method == "GET":
                    resp = client.get(url, headers=headers)
                elif method == "POST":
                    if payload_type == "json":
                        resp = client.post(url, json=payload, headers=headers)
                    elif payload_type == "form":
                        resp = client.post(url, data=payload, headers=headers)
                    else:
                        resp = client.post(url, headers=headers)
                elif method == "PUT":
                    resp = client.put(url, json=payload or {}, headers=headers)
                elif method == "PATCH":
                    resp = client.patch(url, json=payload or {}, headers=headers)
                elif method == "DELETE":
                    resp = client.delete(url, headers=headers)
                else:
                    results.append((method, url, -1, f"Unsupported method"))
                    fail += 1
                    continue

                status = resp.status_code
                body_preview = None
                try:
                    body = resp.json()
                    body_preview = str(body)[:300]
                except Exception:
                    body_preview = resp.text[:300]

                # Special-case fallback: interactive lesson detail may not be ID 1
                if path == f"{API}/interactive-lessons/1" and status == 404:
                    try:
                        lst = client.get(f"{API}/interactive-lessons/")
                        if lst.status_code in ALLOWED_STATUSES_PUBLIC:
                            items = []
                            try:
                                items = lst.json()
                            except Exception:
                                items = []
                            if isinstance(items, list) and items:
                                first_id = items[0].get("id")
                                if first_id:
                                    det = client.get(f"{API}/interactive-lessons/{first_id}")
                                    status = det.status_code
                                    try:
                                        body_preview = str(det.json())[:300]
                                    except Exception:
                                        body_preview = det.text[:300]
                    except Exception:
                        pass

                # Determine pass/fail
                if requires_auth:
                    if status in ALLOWED_STATUSES_WITH_AUTH or status in ALSO_OK_FOR_PROTECTED:
                        ok += 1
                        results.append((method, url, status, body_preview))
                    else:
                        fail += 1
                        results.append((method, url, status, body_preview))
                else:
                    if status in ALLOWED_STATUSES_PUBLIC:
                        ok += 1
                        results.append((method, url, status, body_preview))
                    else:
                        fail += 1
                        results.append((method, url, status, body_preview))

            except Exception as e:
                fail += 1
                results.append((method, url, -1, f"Exception: {e}"))

    # Print summary
    print("\n=== Live Smoke Test Results ===")
    for method, url, status, preview in results:
        print(f"{method} {url} -> {status}\n  {preview}\n")
    print(f"Summary: OK={ok}, FAIL={fail}, TOTAL={ok+fail}")

    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
