import requests
from pprint import pprint

# Configuration
BASE_URL = "http://0.0.0.0:8004/api/v1"
TEST_USER_EMAIL = "test@example.com"  # Free user
TEST_USER_PASSWORD = "testpassword"

# Global variables
tokens = {}

def print_section(title):
    print(f"\n{'='*50}\n{title}\n{'='*50}")

def print_result(name, success, response):
    status = "✓ PASSED" if success else "✗ FAILED"
    print(f"{status} - {name}")
    if not success:
        print(f"  Status: {response.status_code}")
        try: 
            print(f"  Error: {response.json()}")
        except: 
            print(f"  Response: {response.text}")

def login_user(email, password):
    """Login and return the access token"""
    try:
        response = requests.post(
            f"{BASE_URL}/login/access-token",
            data={"username": email, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=20
        )
        if response.status_code == 200:
            return response.json().get("access_token")
        return None
    except Exception as e:
        print(f"Login error: {e}")
        return None

def test_premium_endpoints():
    print_section("TESTING PREMIUM ACCESS WITH FREE USER")
    
    # Login with free user
    token = login_user(TEST_USER_EMAIL, TEST_USER_PASSWORD)
    if not token:
        print("✗ Failed to login with test user")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 1. Test premium data endpoint
    print("\nTesting /users/me/premium-data (should be blocked for free users):")
    response = requests.get(
        f"{BASE_URL}/users/me/premium-data",
        headers=headers,
        timeout=30
    )
    # Should be 403 Forbidden for free users
    print_result("Access premium data endpoint", response.status_code == 403, response)
    
    # 2. Test IELTS questions (premium feature)
    print("\nTesting /ielts/questions/listening (should be blocked for free users):")
    response = requests.get(
        f"{BASE_URL}/ielts/questions/listening",
        headers=headers,
        timeout=30
    )
    # Should be 403 Forbidden for free users
    print_result("Access IELTS questions", response.status_code == 403, response)
    
    # 3. Test getting a premium lesson
    print("\nTrying to access a premium lesson (if any exists):")
    # First get all lessons
    response = requests.get(
        f"{BASE_URL}/lessons/",
        headers=headers,
        timeout=30
    )
    
    if response.status_code == 200:
        lessons = response.json()
        premium_lessons = [l for l in lessons if l.get('is_premium', False)]
        
        if premium_lessons:
            # Try to access the first premium lesson
            lesson_id = premium_lessons[0]['id']
            response = requests.get(
                f"{BASE_URL}/lessons/{lesson_id}",
                headers=headers,
                timeout=30
            )
            # Should be 403 Forbidden for free users
            print_result(f"Access premium lesson ID {lesson_id}", response.status_code == 403, response)
        else:
            print("ℹ️ No premium lessons found to test")
    else:
        print(f"ℹ️ Could not fetch lessons: {response.status_code}")
    
    print("\nTest completed. If all tests passed, premium access is properly restricted.")

if __name__ == "__main__":
    test_premium_endpoints()
