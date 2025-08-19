import requests
import os
from pprint import pprint

# Configuration
BASE_URL = "http://localhost:8005/api/v1"
TEST_USER_EMAIL = "test@example.com"
TEST_USER_PASSWORD = "testpassword"

def print_section(title):
    print(f"\n{'='*50}\n{title}\n{'='*50}")

def print_result(name, success, response):
    status = "✓ PASSED" if success else "✗ FAILED"
    print(f"{status} - {name}")
    if not success:
        print(f"  Status: {response.status_code}")
        try: print(f"  Error: {response.json()}")
        except: print(f"  Response: {response.text}")

def login():
    try:
        response = requests.post(
            f"{BASE_URL}/login/access-token",
            data={"username": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=20
        )
        return response.json().get("access_token") if response.status_code == 200 else None
    except Exception as e:
        print(f"Login error: {e}")
        return None

def test_ai_endpoints():
    print_section("TESTING AI ENDPOINTS")
    
    # Login
    token = login()
    if not token:
        print("✗ Failed to login")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test /ai/ask
    print("\nTesting /ai/ask:")
    response = requests.post(
        f"{BASE_URL}/ai/ask",
        json={"prompt": "What is the capital of France?"},
        headers=headers,
        timeout=30
    )
    print_result("Ask a question", response.status_code == 200, response)
    if response.status_code == 200:
        print(f"  Response: {response.text[:200]}...")
    
    # Test /ai/suggest-lesson
    print("\nTesting /ai/suggest-lesson:")
    response = requests.get(f"{BASE_URL}/ai/suggest-lesson", headers=headers, timeout=30)
    print_result("Get suggested lesson", response.status_code in [200, 204], response)
    if response.status_code == 200:
        print(f"  Suggestion: {response.json()}")

    # Test /ai/tts (text-to-speech)
    print("\nTesting /ai/tts:")
    response = requests.get(
        f"{BASE_URL}/ai/tts",
        params={"text": "This is a test of text to speech.", "language": "en-US"},
        headers=headers,
        timeout=30
    )
    print_result("Convert text to speech", response.status_code == 200, response)
    if response.status_code == 200:
        print("  TTS request successful")

    print("\nNote: To test speech-to-text (/ai/stt), you'll need an audio file.")
    print("Note: To test pronunciation analysis (/ai/pronunciation), you'll need an audio file.")

if __name__ == "__main__":
    test_ai_endpoints()
