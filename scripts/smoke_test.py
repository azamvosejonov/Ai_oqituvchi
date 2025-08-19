import os
import sys
from pathlib import Path
from typing import Dict, Any

# Ensure project root is on sys.path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Make tests fast/non-blocking
os.environ.setdefault("DISABLE_WHISPER", "1")
os.environ.setdefault("DISABLE_GEMINI", "1")
os.environ.setdefault("DISABLE_TTS", "1")
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("TESTING", "1")

from fastapi.testclient import TestClient

from app.core.config import settings
from main import app


def auth_headers(client: TestClient) -> Dict[str, str]:
    login_url = f"{settings.API_V1_STR}/login/access-token"
    data = {
        "username": settings.EMAIL_TEST_USER,
        "password": settings.EMAIL_TEST_USER_PASSWORD,
    }
    r = client.post(login_url, data=data)
    if r.status_code != 200:
        print(f"[AUTH] Failed to login: {r.status_code} {r.text}")
        return {}
    token = r.json().get("access_token")
    if not token:
        print(f"[AUTH] No access_token in response: {r.text}")
        return {}
    return {"Authorization": f"Bearer {token}"}


def run_smoke():
    results = []
    with TestClient(app) as client:
        headers = auth_headers(client)

        # Collect simple GET endpoints (no path params) from OpenAPI
        openapi: Dict[str, Any] = app.openapi()
        for path, ops in openapi.get("paths", {}).items():
            # Skip endpoints with path params
            if "{" in path or "}" in path:
                continue
            for method, meta in ops.items():
                if method.lower() != "get":
                    continue
                url = path
                # Prefer authorized call if we have headers
                try:
                    r = client.get(url, headers=headers or None)
                except Exception as e:
                    results.append((method.upper(), url, 0, f"REQUEST ERROR: {e}"))
                    continue
                status = r.status_code
                ok = 200 <= status < 300
                results.append((method.upper(), url, status, "OK" if ok else r.text[:200]))

        # Print summary
        total = len(results)
        passed = sum(1 for _, _, s, _ in results if 200 <= s < 300)
        failed = total - passed
        print("\n=== API SMOKE TEST RESULTS ===")
        print(f"Total checked: {total} | Passed: {passed} | Failed: {failed}")
        for method, url, status, note in results:
            print(f"{status:>3} {method:>4} {url} - {note}")


if __name__ == "__main__":
    run_smoke()
