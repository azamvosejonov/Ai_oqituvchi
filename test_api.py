import requests
import json
from typing import Dict, Any, List, Optional
import os

# Base URL for the API
BASE_URL = "http://localhost:8005/api/v1"

# Test user credentials
TEST_USER = {
    "username": "test@example.com",
    "password": "testpassword"
}

# Admin credentials (update these with actual admin credentials if available)
ADMIN_USER = {
    "username": "admin@example.com",
    "password": "adminpassword"
}

# Global variables to store test data
test_data = {
    "user_token": None,
    "admin_token": None,
    "course_id": None,
    "lesson_id": None,
    "word_id": None,
    "topic_id": None,
    "subscription_plan_id": None,
    "certificate_id": None,
    "feedback_id": None
}

def print_section(title: str):
    print(f"\n{'=' * 50}")
    print(f"{title.upper():^50}")
    print(f"{'=' * 50}")

def print_test_result(name: str, success: bool, response=None, expected_codes: List[int] = None):
    status = "✓ PASSED" if success else "✗ FAILED"
    print(f"{status} - {name}")
    if not success and response is not None:
        print(f"  Status Code: {response.status_code}")
        if expected_codes:
            print(f"  Expected one of: {expected_codes}")
        try:
            print(f"  Response: {response.json()}")
        except:
            print(f"  Response: {response.text}")

def get_headers(token: str = None, content_type: str = "application/json") -> Dict[str, str]:
    headers = {"Content-Type": content_type}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers

def login_user(email: str, password: str) -> str:
    """Login and return the access token"""
    url = f"{BASE_URL}/login/access-token"
    data = {
        "username": email,
        "password": password
    }
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            return response.json().get("access_token")
        else:
            print(f"Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error during login: {str(e)}")
        return None

def test_authentication():
    print_section("Authentication Tests")
    
    # Test login with test user
    token = login_user(TEST_USER["username"], TEST_USER["password"])
    if token:
        test_data["user_token"] = token
        print_test_result("User Login", True)
    else:
        print_test_result("User Login", False)
    
    # Test login with admin user
    admin_token = login_user(ADMIN_USER["username"], ADMIN_USER["password"])
    if admin_token:
        test_data["admin_token"] = admin_token
        print_test_result("Admin Login", True)
    else:
        print_test_result("Admin Login", False)

def test_user_endpoints():
    if not test_data["user_token"]:
        print("Skipping user endpoints test - no user token available")
        return
        
    print_section("User Endpoint Tests")
    headers = get_headers(test_data["user_token"])
    
    # Test get current user
    response = requests.get(f"{BASE_URL}/users/me", headers=headers)
    success = response.status_code == 200
    print_test_result("Get Current User", success, response, [200])
    
    # Test update user
    update_data = {"full_name": "Test User Updated"}
    response = requests.put(f"{BASE_URL}/users/me", json=update_data, headers=headers)
    success = response.status_code == 200
    print_test_result("Update Current User", success, response, [200])

def test_course_endpoints():
    if not test_data["user_token"]:
        print("Skipping course endpoints test - no user token available")
        return
        
    print_section("Course Endpoint Tests")
    headers = get_headers(test_data["user_token"])
    
    # Test get all courses
    response = requests.get(f"{BASE_URL}/courses/", headers=headers)
    success = response.status_code == 200
    print_test_result("Get All Courses", success, response, [200])
    
    if success and response.json():
        test_data["course_id"] = response.json()[0].get("id")
        
        # Test get single course
        response = requests.get(f"{BASE_URL}/courses/{test_data['course_id']}", headers=headers)
        success = response.status_code == 200
        print_test_result("Get Single Course", success, response, [200])
        
        # Test get course lessons
        response = requests.get(f"{BASE_URL}/courses/{test_data['course_id']}/lessons", headers=headers)
        success = response.status_code == 200
        print_test_result("Get Course Lessons", success, response, [200])
        
        if success and response.json():
            test_data["lesson_id"] = response.json()[0].get("id")

def test_lesson_endpoints():
    if not test_data.get("lesson_id"):
        print("Skipping lesson endpoints test - no lesson ID available")
        return
        
    print_section("Lesson Endpoint Tests")
    headers = get_headers(test_data["user_token"])
    
    # Test get lesson by ID
    response = requests.get(f"{BASE_URL}/lessons/{test_data['lesson_id']}", headers=headers)
    success = response.status_code == 200
    print_test_result("Get Lesson by ID", success, response, [200])
    
    # Test get lesson content
    response = requests.get(f"{BASE_URL}/lessons/{test_data['lesson_id']}/content", headers=headers)
    success = response.status_code == 200
    print_test_result("Get Lesson Content", success, response, [200])

def main():
    print("Starting API Tests...")
    
    # Run authentication tests first
    test_authentication()
    
    # If user login was successful, run other tests
    if test_data["user_token"]:
        test_user_endpoints()
        test_course_endpoints()
        test_lesson_endpoints()
    
    print("\nTest Summary:")
    print("=" * 50)
    print("Note: Some tests may be skipped if previous dependencies failed.")
    print("Please check the full output for any errors or warnings.")

if __name__ == "__main__":
    main()
