import os
import sys
import json
import requests
from typing import Dict, Any, Optional
from pprint import pprint

# Configuration
BASE_URL = "http://0.0.0.0:8004/api/v1"
TEST_USER = {
    "username": "test@example.com",
    "password": "testpassword"
}

class APITester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        
    def print_header(self, text: str):
        print("\n" + "="*80)
        print(f"TESTING: {text}")
        print("="*80)
    
    def login(self) -> bool:
        self.print_header("1. LOGIN")
        try:
            response = self.session.post(
                f"{BASE_URL}/login",
                json={"username": TEST_USER["username"], "password": TEST_USER["password"]},
                timeout=20
            )
            response.raise_for_status()
            data = response.json()
            self.token = data.get("access_token")
            if self.token:
                self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                print("✅ Login successful")
                print(f"Token: {self.token[:20]}...")
                return True
            else:
                print("❌ Login failed - No token received")
                return False
        except Exception as e:
            print(f"❌ Login failed: {str(e)}")
            return False
    
    def test_endpoint(self, method: str, endpoint: str, data: Optional[Dict] = None, expected_status: int = 200) -> bool:
        try:
            url = f"{BASE_URL}{endpoint}"
            print(f"\n🔹 {method.upper()} {endpoint}")
            
            if method.lower() == 'get':
                response = self.session.get(url, timeout=30)
            elif method.lower() == 'post':
                response = self.session.post(url, json=data or {}, timeout=30)
            elif method.lower() == 'put':
                response = self.session.put(url, json=data or {}, timeout=30)
            elif method.lower() == 'delete':
                response = self.session.delete(url, timeout=30)
            else:
                print(f"❌ Unsupported method: {method}")
                return False
            
            print(f"Status: {response.status_code}")
            
            try:
                print("Response:")
                pprint(response.json())
            except:
                print("No JSON response")
            
            if response.status_code == expected_status:
                print("✅ Success")
                return True
            else:
                print(f"❌ Failed - Expected status {expected_status}, got {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False
    
    def test_all(self):
        # Test login first
        if not self.login():
            print("❌ Cannot proceed without login")
            return False
        
        # Test user endpoints
        self.print_header("2. USER ENDPOINTS")
        self.test_endpoint("GET", "/users/me")
        
        # Test interactive lessons
        self.print_header("3. INTERACTIVE LESSONS")
        self.test_endpoint("POST", "/interactive-lessons/start-lesson", 
                         {"lesson_type": "conversation", "topic": "greetings", 
                          "difficulty": "beginner", "avatar_type": "default"})
        
        # Test lesson interactions
        self.print_header("4. LESSON INTERACTIONS")
        self.test_endpoint("POST", "/lesson-interactions/send-message",
                         {"session_id": 1, "message": "Test message", "message_type": "text"})
        
        # Test AI feedback
        self.print_header("5. AI FEEDBACK")
        self.test_endpoint("POST", "/ai/feedback",
                         {"text": "This is a test feedback", "rating": 5})
        
        # Test pronunciation
        self.print_header("6. PRONUNCIATION")
        self.test_endpoint("POST", "/interactive-lessons/assess-pronunciation",
                         {"expected_text": "Hello world", "audio_base64": "base64_encoded_audio_here"})
        
        # Test homework
        self.print_header("7. HOMEWORK")
        self.test_endpoint("GET", "/homework/")
        
        # Test adaptive lessons
        self.print_header("8. ADAPTIVE LESSONS")
        self.test_endpoint("GET", "/ai/recommend-lesson")
        
        # Test notifications
        self.print_header("9. NOTIFICATIONS")
        self.test_endpoint("GET", "/notifications/")
        
        # Test admin endpoints (if user has admin privileges)
        self.print_header("10. ADMIN ENDPOINTS")
        self.test_endpoint("GET", "/admin/users/", expected_status=403)  # Should be 403 if not admin

if __name__ == "__main__":
    tester = APITester()
    tester.test_all()
