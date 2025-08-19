import os
import sys
import argparse
from typing import Dict, Any, List, Tuple
import requests
from pathlib import Path

DEFAULT_BASE = os.environ.get("BASE_URL", "http://0.0.0.0:8002")
OPENAPI_PATH = "/api/v1/openapi.json"
LOGIN_PATH = "/api/v1/login/access-token"
EMAIL = os.environ.get("SMOKE_EMAIL", os.environ.get("EMAIL_TEST_USER", "test@example.com"))
PASSWORD = os.environ.get("SMOKE_PASSWORD", os.environ.get("EMAIL_TEST_USER_PASSWORD", "testpassword"))

TEST_AUDIO = Path("tests/test_data/test_audio.wav")


def get_openapi(base_url: str) -> Dict[str, Any]:
    url = base_url.rstrip("/") + OPENAPI_PATH
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r.json()


def try_login(base_url: str) -> Dict[str, str]:
    url = base_url.rstrip("/") + LOGIN_PATH
    # First try form-encoded (OAuth2PasswordRequestForm style)
    data = {"username": EMAIL, "password": PASSWORD}
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    try:
        r = requests.post(url, data=data, headers=headers, timeout=30)
        if r.status_code == 200 and "access_token" in r.json():
            token = r.json()["access_token"]
            return {"Authorization": f"Bearer {token}"}
    except Exception:
        pass
    # Try JSON body as fallback
    try:
        r = requests.post(url, json=data, timeout=30)
        if r.status_code == 200 and "access_token" in r.json():
            token = r.json()["access_token"]
            return {"Authorization": f"Bearer {token}"}
    except Exception:
        pass
    return {}


def substitute_path_params(path: str) -> str:
    # Replace any {param} with '1'
    out = ""
    i = 0
    while i < len(path):
        if path[i] == "{" :
            while i < len(path) and path[i] != "}":
                i += 1
            out += "1"
        else:
            out += path[i]
        i += 1
    return out


def safe_post_allowlist() -> List[Tuple[str, Dict[str, Any], Dict[str, Any]]]:
    """
    Returns a list of tuples: (path, json_body, files) for safe POSTs.
    Only endpoints that shouldn't mutate critical data or are idempotent.
    """
    items: List[Tuple[str, Dict[str, Any], Dict[str, Any]]] = []

    # AI TTS (text -> mp3)
    items.append(("/api/v1/ai/tts", {"text": "Hello from smoke test", "language_code": "en"}, {}))

    # AI STT (audio -> text)
    files_stt: Dict[str, Any] = {}
    if TEST_AUDIO.exists():
        files_stt = {"file": (TEST_AUDIO.name, TEST_AUDIO.open("rb"), "audio/wav")}
    items.append(("/api/v1/ai/stt", {}, files_stt))

    # AI Pronunciation
    files_pr: Dict[str, Any] = {}
    if TEST_AUDIO.exists():
        files_pr = {"file": (TEST_AUDIO.name, TEST_AUDIO.open("rb"), "audio/wav")}
    items.append(("/api/v1/ai/pronunciation", {"reference_text": "Hello this is a test"}, files_pr))

    return items


def run_smoke(base_url: str):
    print(f"Base URL: {base_url}")
    # Quick health/version
    try:
        print("/health:", requests.get(base_url + "/health", timeout=10).status_code)
    except Exception as e:
        print("/health error:", e)
    try:
        print("/version:", requests.get(base_url + "/version", timeout=10).status_code)
    except Exception as e:
        print("/version error:", e)

    openapi = get_openapi(base_url)
    headers = try_login(base_url)
    if headers:
        print("Auth: OK (token acquired)")
    else:
        print("Auth: FAILED (continuing without token). Provide SMOKE_EMAIL/SMOKE_PASSWORD env vars to authenticate.")

    results = []
    # 1) Test GET/HEAD/OPTIONS for every path
    for path, ops in openapi.get("paths", {}).items():
        url_path = substitute_path_params(path)
        full = base_url.rstrip("/") + url_path
        if path.startswith("/docs") or path.startswith("/openapi"):
            continue
        for method in ["GET", "HEAD", "OPTIONS"]:
            if method.lower() in ops:
                try:
                    r = requests.request(method, full, headers=headers or None, timeout=60)
                    ok = 200 <= r.status_code < 300
                    # Treat 404 as acceptable for GET/HEAD (resource may not exist in empty DB)
                    if not ok and r.status_code == 404 and method in ("GET", "HEAD"):
                        note = "OK (404 acceptable for empty resource)"
                        results.append((method, url_path, r.status_code, note))
                    else:
                        results.append((method, url_path, r.status_code, "OK" if ok else r.text[:200]))
                except Exception as e:
                    results.append((method, url_path, 0, f"REQUEST ERROR: {e}"))

    # 2) Safe POST allowlist
    for path, body, files in safe_post_allowlist():
        url_path = path
        full = base_url.rstrip("/") + url_path
        try:
            if files:
                r = requests.post(full, headers=headers or None, data=body if body else None, files=files, timeout=90)
            else:
                r = requests.post(full, headers={**(headers or {}), "Content-Type": "application/json"}, json=body, timeout=90)
            results.append(("POST", url_path, r.status_code, "OK" if 200 <= r.status_code < 300 else r.text[:200]))
        except Exception as e:
            results.append(("POST", url_path, 0, f"REQUEST ERROR: {e}"))

    # Summary
    total = len(results)
    passed = sum(1 for _, _, s, _ in results if 200 <= s < 300)
    failed = total - passed
    print("\n=== LIVE API SMOKE RESULTS ===")
    print(f"Total checked: {total} | Passed: {passed} | Failed: {failed}")
    for method, url, status, note in results:
        print(f"{status:>3} {method:>7} {url} - {note}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Live API smoke tester for running server")
    parser.add_argument("--base", default=DEFAULT_BASE, help="Base URL, e.g. http://0.0.0.0:8002")
    args = parser.parse_args()
    run_smoke(args.base)
