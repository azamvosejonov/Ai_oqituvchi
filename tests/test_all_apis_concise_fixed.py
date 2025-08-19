import requests
from pprint import pprint

class APITester:
    def __init__(self, base_url="http://0.0.0.0:8004/api/v1"):
        self.base_url = base_url
        self.session = requests.Session()
        self.token = None
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
    def login(self, username, password, is_admin=False):
        """Handle user login and store authentication token"""
        try:
            self.session = requests.Session()
            url = f"{self.base_url}/login"
            json_data = {"username": username, "password": password}
            headers = {"accept": "application/json", "Content-Type": "application/json"}
            
            print(f"\n🔐 Login attempt:")
            print(f"URL: {url}")
            print(f"Username: {username}")
            
            r = self.session.post(url, json=json_data, headers=headers, timeout=20)
            print(f"\n🔑 Login response:")
            print(f"Status: {r.status_code}")
            
            try:
                response_data = r.json()
                print("Response:", response_data)
            except:
                print("Response (raw):", r.text)
                response_data = {}
            
            r.raise_for_status()
            
            token = response_data.get("access_token")
            if token:
                self.token = f"Bearer {token}"
                self.headers["Authorization"] = self.token
                print(f"✅ Successfully logged in as {username}")
                self.user_info = response_data.get("user", {})
                self.is_authenticated = True
                self.is_admin = is_admin
                return True
            else:
                print("❌ Login failed - No access token in response")
                return False
                
        except Exception as e:
            print(f"❌ Login failed: {str(e)}")
            if hasattr(e, 'response') and e.response:
                print(f"Response status: {e.response.status_code}")
                try:
                    print(f"Response body: {e.response.json()}")
                except:
                    print(f"Response text: {e.response.text}")
            return False

    def test_endpoint(self, method, path, data=None, expected_status=200, headers=None, params=None, method_override=None):
        """Test an API endpoint with the given method and data"""
        url = f"{self.base_url}{path}"
        request_headers = self.headers.copy()
        
        if headers:
            if isinstance(headers, dict):
                request_headers.update(headers)
        
        if hasattr(self, 'token') and self.token and 'Authorization' not in request_headers:
            request_headers["Authorization"] = self.token
            
        http_method = method_override.upper() if method_override else method.upper()
            
        try:
            if http_method == "GET":
                r = self.session.get(url, headers=request_headers, params=params, timeout=30)
            elif http_method == "POST":
                r = self.session.post(url, json=data, headers=request_headers, params=params, timeout=30)
            elif http_method == "PUT":
                r = self.session.put(url, json=data, headers=request_headers, params=params, timeout=30)
            elif http_method == "DELETE":
                r = self.session.delete(url, headers=request_headers, params=params, timeout=30)
            elif http_method == "PATCH":
                r = self.session.patch(url, json=data, headers=request_headers, params=params, timeout=30)
            else:
                print(f"❌ Unsupported method: {http_method}")
                return False
                
            print(f"\n🔹 {http_method} {url}")
            if data:
                print(f"Request data: {data}")
            if params:
                print(f"Query params: {params}")
            print(f"Status: {r.status_code}")
            
            try:
                response_data = r.json()
                print(f"Response: {response_data}")
            except ValueError:
                print(f"Response: {r.text}")
                response_data = None
                
            if r.status_code == expected_status:
                print("✅ Success")
                return response_data if response_data is not None else True
            else:
                print(f"❌ Expected status {expected_status}")
                return False
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def test_authentication_endpoints(self):
        """Test authentication related endpoints"""
        self.print_header("🔐 Authentication Endpoints")
        
        # Test 1: Login with invalid credentials
        print("\n🔹 Testing login with invalid credentials")
        self.test_endpoint("POST", "/login",
                         data={"username": "invalid", "password": "wrongpassword"},
                         expected_status=401)
        
        # Test 2: Login with test user
        print("\n🔹 Testing login with test user")
        if not self.login(**TEST_USER_CREDENTIALS):
            print("❌ Test user login failed, cannot continue with other tests")
            return False
        
        # Test 3: Get current user info
        print("\n🔹 Testing current user endpoint")
        user_info = self.test_endpoint("GET", "/users/me", expected_status=200)
        if user_info and isinstance(user_info, dict):
            print(f"✅ Logged in as: {user_info.get('email')}")
            print(f"   User ID: {user_info.get('id')}")
            print(f"   Is Admin: {user_info.get('is_superuser', False)}")
        
        # Test 4: Logout
        print("\n🔹 Testing logout")
        self.test_endpoint("POST", "/logout", expected_status=200)
        
        # Login again for subsequent tests
        print("\n🔹 Logging in again for next tests")
        return self.login(**TEST_USER_CREDENTIALS)

    def test_user_endpoints(self):
        """Test user-related endpoints"""
        self.print_header("👤 User Endpoints")
        
        # User profile
        self.test_endpoint("GET", "/users/me")
        
        # Update profile
        self.test_endpoint("PUT", "/users/me/profile", 
                         data={"full_name": "Test User Updated"})
        
        # User preferences
        self.test_endpoint("GET", "/users/me/settings")
        self.test_endpoint("PUT", "/users/me/settings",
                         data={"language": "en", "theme": "dark"})
        
        # User notifications
        self.test_endpoint("GET", "/notifications/")
        
        # User statistics
        self.test_endpoint("GET", "/users/me/statistics")
        
        return True

    def test_lesson_endpoints(self):
        """Test lesson and interactive lesson endpoints"""
        self.print_header("📚 Lesson Endpoints")
        
        # Get all available lessons
        self.test_endpoint("GET", "/lessons/", 
                         params={"page": 1, "per_page": 10, "level": "A1"})
        
        # Search for lessons
        self.test_endpoint("GET", "/lessons/search", 
                         params={"query": "beginner", "tags": "grammar"})
        
        # Get lesson categories
        self.test_endpoint("GET", "/lessons/categories")
        
        # Start a new lesson session
        start_response = self.test_endpoint("POST", "/interactive-lessons/start",
                                          data={"lesson_type": "grammar", "level": "A1"})
        
        if start_response and isinstance(start_response, dict):
            lesson_id = start_response.get('id')
            
            # Test lesson interaction
            self.test_endpoint("POST", "/lesson-interactions/", {
                "lesson_id": lesson_id,
                "interaction_type": "message",
                "content": "Hello, this is a test message"
            })
            
            # Get lesson progress
            self.test_endpoint("GET", f"/lessons/{lesson_id}/progress")
            
            # Complete the lesson
            self.test_endpoint("POST", f"/lessons/{lesson_id}/complete", {
                "score": 85,
                "feedback": "Good job!",
                "time_spent_seconds": 300
            })
        
        # Get recommended lessons
        self.test_endpoint("GET", "/recommendations/for-you",
                         params={"limit": 5, "type": "adaptive"})
        
        return True

    def test_ai_endpoints(self):
        """Test AI-related endpoints"""
        self.print_header("🤖 AI Endpoints")
        
        # AI Chat with context
        self.test_endpoint("POST", "/ai/chat", {
            "message": "Can you explain the present perfect tense?",
            "context": {
                "user_level": "A2",
                "recent_topics": ["past simple", "present continuous"],
                "preferred_learning_style": "examples"
            },
            "conversation_id": "conv_123"
        })
        
        # Text generation
        self.test_endpoint("POST", "/ai/chat", {
            "message": "Write a short dialogue at a restaurant",
            "context": {
                "task": "generate_dialogue",
                "style": "casual"
            }
        })
        
        # Pronunciation assessment
        self.test_endpoint("POST", "/ai/speech/evaluate", {
            "audio_url": "https://example.com/audio.wav",
            "expected_text": "The quick brown fox jumps over the lazy dog",
            "language": "en-US"
        })
        
        # Grammar check
        self.test_endpoint("POST", "/ai/chat", {
            "message": "Check grammar: She don't likes apples. They is very tasty.",
            "context": {
                "task": "grammar_check",
                "explanation_level": "detailed"
            }
        })
        
        return True

    def test_admin_endpoints(self):
        """Test admin-only endpoints"""
        self.print_header("🔧 Admin Endpoints")
        
        # Test with regular user first (should fail with 403)
        print("\n🔹 Testing admin endpoints with regular user (should fail with 403)")
        
        # User management
        self.test_endpoint("GET", "/admin/users/", expected_status=403)
        
        # Course management
        self.test_endpoint("GET", "/admin/courses/", expected_status=403)
        self.test_endpoint("POST", "/admin/courses/", 
                         data={"title": "Test Course", "description": "Test Description", "is_active": True},
                         expected_status=403)
        
        # Now test with admin user if credentials are available
        if hasattr(self, 'admin_username') and hasattr(self, 'admin_password'):
            print("\n🔹 Testing admin endpoints with admin user")
            
            # Login as admin
            if not self.login(self.admin_username, self.admin_password, is_admin=True):
                print("❌ Admin login failed, skipping admin tests")
                return False
                
            # Test admin endpoints with admin user
            self.test_endpoint("GET", "/admin/users/")
            self.test_endpoint("GET", "/admin/courses/")
            
            # Test creating a course
            course_data = {
                "title": "Test Course",
                "description": "Test Description",
                "is_active": True,
                "level": "A2",
                "category": "General English"
            }
            self.test_endpoint("POST", "/admin/courses/", data=course_data)
            
            # Logout admin
            self.test_endpoint("POST", "/logout")
            
            # Log back in as regular user
            self.login(**TEST_USER_CREDENTIALS)
            
        return True
        
    def test_payment_endpoints(self):
        """Test payment-related endpoints"""
        self.print_header("💳 Payment Endpoints")
        
        # Get subscription plans
        self.test_endpoint("GET", "/subscription-plans/")
        
        # Create checkout session
        self.test_endpoint("POST", "/payments/create-checkout-session", {
            'subscription_plan_id': 'premium_monthly',
            'success_url': 'https://example.com/success',
            'cancel_url': 'https://example.com/cancel'
        })
        
        # Get payment history
        self.test_endpoint("GET", "/payments/history")
        
        return True
        
    def test_forum_endpoints(self):
        """Test forum and community endpoints"""
        self.print_header("💬 Forum Endpoints")
        
        # Forum categories
        self.test_endpoint("GET", "/forum/categories")
        
        # Forum posts
        self.test_endpoint("GET", "/forum/posts")
        self.test_endpoint("POST", "/forum/posts", {
            "title": "Test Post",
            "content": "This is a test post",
            "category_id": 1
        })
        
        return True
        
    def test_utility_endpoints(self):
        """Test utility endpoints"""
        self.print_header("🔧 Utility Endpoints")
        
        # System health and info
        self.test_endpoint("GET", "/health")
        self.test_endpoint("GET", "/version")
        
        # TTS/STT endpoints
        self.test_endpoint("GET", "/ai/tts/voices")
        self.test_endpoint("GET", "/ai/stt/languages")
        
        # API documentation
        self.test_endpoint("GET", "/docs")
        self.test_endpoint("GET", "/redoc")
        
        return True

    def run_all_tests(self):
        """Run all test suites"""
        print("🚀 Starting Comprehensive API Tests...")
        
        # Test authentication first
        if not self.test_authentication_endpoints():
            print("❌ Authentication tests failed")
            return
        
        # Test user endpoints
        if not self.test_user_endpoints():
            print("⚠️ Some user endpoint tests failed")
        
        # Test lesson endpoints
        if not self.test_lesson_endpoints():
            print("⚠️ Some lesson endpoint tests failed")
        
        # Test AI endpoints
        if not self.test_ai_endpoints():
            print("⚠️ Some AI endpoint tests failed")
        
        # Test admin endpoints (will be skipped if not admin)
        if not self.test_admin_endpoints():
            print("⚠️ Some admin endpoint tests were skipped or failed")
            
        # Test payment endpoints
        if not self.test_payment_endpoints():
            print("⚠️ Some payment endpoint tests failed")
            
        # Test forum endpoints
        if not self.test_forum_endpoints():
            print("⚠️ Some forum endpoint tests failed")
            
        # Test utility endpoints
        if not self.test_utility_endpoints():
            print("⚠️ Some utility endpoint tests failed")
        
        print("\n✅ All test suites completed!")

    def print_header(self, title):
        """Print a formatted header for test sections"""
        print(f"\n{'='*50}")
        print(f"{title}")
        print(f"{'='*50}")

if __name__ == "__main__":
    # Initialize tester
    tester = APITester()
    
    # Set test credentials
    TEST_USER_CREDENTIALS = {"username": "test@example.com", "password": "testpassword"}
    ADMIN_CREDENTIALS = {"username": "admin@example.com", "password": "admin123"}
    
    # Set admin credentials if available
    tester.admin_username = ADMIN_CREDENTIALS["username"]
    tester.admin_password = ADMIN_CREDENTIALS["password"]
    
    # Run all tests
    tester.run_all_tests()
