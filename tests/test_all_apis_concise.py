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
            # Clear any existing session
            self.session = requests.Session()
            
            # Using the correct login endpoint with JSON data for API v1
            url = f"{self.base_url}/login"
            json_data = {
                "username": username,
                "password": password
            }
            headers = {
                "accept": "application/json",
                "Content-Type": "application/json"
            }
            
            print(f"\n🔐 Login attempt:")
            print(f"URL: {url}")
            print(f"Username: {username}")
            
            # Using json parameter for JSON data
            r = self.session.post(url, json=json_data, headers=headers)
            
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
                
                # Store user info if available
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
        
        # Use provided headers or default headers
        request_headers = self.headers.copy()
        if headers:
            if isinstance(headers, dict):
                request_headers.update(headers)
            
        # Add authorization header if token exists
        if hasattr(self, 'token') and self.token and 'Authorization' not in request_headers:
            request_headers["Authorization"] = self.token
            
        # Use method_override if provided (for PATCH, etc.)
        http_method = method_override.upper() if method_override else method.upper()
            
        try:
            # Make the request with appropriate method and parameters
            if http_method == "GET":
                r = self.session.get(url, headers=request_headers, params=params)
            elif http_method == "POST":
                r = self.session.post(url, json=data, headers=request_headers, params=params)
            elif http_method == "PUT":
                r = self.session.put(url, json=data, headers=request_headers, params=params)
            elif http_method == "DELETE":
                r = self.session.delete(url, headers=request_headers, params=params)
            elif http_method == "PATCH":
                r = self.session.patch(url, json=data, headers=request_headers, params=params)
            else:
                print(f"❌ Unsupported method: {http_method}")
                return False
                
            # Print request and response details
            print(f"\n🔹 {http_method} {url}")
            if data:
                print(f"Request data: {data}")
            if params:
                print(f"Query params: {params}")
            print(f"Status: {r.status_code}")
            
            # Try to parse JSON response
            try:
                response_data = r.json()
                print(f"Response: {response_data}")
            except ValueError:
                print(f"Response: {r.text}")
                response_data = None
                
            # Check if status code matches expected
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
        
        # Test 3: Get current user info (should work when authenticated)
        print("\n🔹 Testing current user endpoint")
        user_info = self.test_endpoint("GET", "/users/me", expected_status=200)
        if user_info and isinstance(user_info, dict):
            print(f"✅ Logged in as: {user_info.get('email')}")
            print(f"   User ID: {user_info.get('id')}")
            print(f"   Is Admin: {user_info.get('is_superuser', False)}")
        
        # Test 4: Refresh token (if available)
        print("\n🔹 Testing token refresh")
        self.test_endpoint("POST", "/auth/refresh-token", expected_status=200)
        
        # Test 5: Logout (if implemented)
        print("\n🔹 Testing logout")
        self.test_endpoint("POST", "/logout", expected_status=200)
        
        # Test 6: Verify token is invalid after logout
        print("\n🔹 Testing token after logout")
        self.test_endpoint("GET", "/users/me", expected_status=401)
        
        # Login again for subsequent tests
        print("\n🔹 Logging in again for next tests")
        return self.login(**TEST_USER_CREDENTIALS)

    def test_user_endpoints(self):
        """Test user-related endpoints"""
        self.print_header("👤 User Endpoints")
        
        # User profile
        self.test_endpoint("GET", "/users/me")
        
        # Update profile - using the correct endpoint based on the API
        self.test_endpoint("PUT", "/users/me/profile", 
                         data={"full_name": "Test User Updated"})
        
        # Change password - using the correct endpoint
        self.test_endpoint("POST", "/auth/change-password", 
                         data={"current_password": "testpassword", 
                               "new_password": "testpassword"})
        
        # User preferences - using the correct endpoint
        self.test_endpoint("GET", "/users/me/settings")
        self.test_endpoint("PUT", "/users/me/settings",
                         data={"language": "en", "theme": "dark"})
        
        # User notifications
        self.test_endpoint("GET", "/notifications/")
        self.test_endpoint("PATCH", "/notifications/read-all")
        
        # User statistics
        self.test_endpoint("GET", "/users/me/statistics")
        
        return True

    def test_lesson_endpoints(self):
        """Test lesson and interactive lesson endpoints"""
        self.print_header("📚 Lesson Endpoints")
        
        # Get all available lessons with pagination
        self.test_endpoint("GET", "/lessons/", 
                         params={"page": 1, "per_page": 10, "level": "A1"})
        
        # Search for lessons
        self.test_endpoint("GET", "/lessons/search", 
                         params={"query": "beginner", "tags": "grammar"})
        
        # Get lesson categories
        self.test_endpoint("GET", "/lessons/categories")
        
        # Start a new lesson session
        start_response = self.test_endpoint("POST", "/interactive-lessons/start-lesson",
                                          data={"lesson_type": "grammar", "level": "A1"})
        
        if start_response and isinstance(start_response, dict):
            lesson_id = start_response.get('id')
            
            # Test lesson interaction
            self.test_endpoint("POST", "/lesson-interactions/", {
                "lesson_id": lesson_id,
                "interaction_type": "message",
                "content": "Hello, this is a test message",
                "timestamp": "2025-08-13T10:00:00Z"
            })
            
            # Get lesson progress
            self.test_endpoint("GET", f"/lessons/{lesson_id}/progress")
            
            # Submit exercise response
            self.test_endpoint("POST", f"/lessons/{lesson_id}/submit", {
                "exercise_id": 1,
                "user_response": "Sample answer",
                "time_spent_seconds": 45
            })
            
            # Complete the lesson
            self.test_endpoint("POST", f"/lessons/{lesson_id}/complete", {
                "score": 85,
                "feedback": "Good job!",
                "time_spent_seconds": 300
            })
            
            # Get lesson analytics
            self.test_endpoint("GET", f"/lessons/{lesson_id}/analytics")
        
        # Get recommended lessons based on user progress
        self.test_endpoint("GET", "/recommendations/for-you",
                         params={"limit": 5, "type": "adaptive"})
        
        # Get popular lessons
        self.test_endpoint("GET", "/lessons/popular",
                         params={"timeframe": "week"})
        
        # Get user's learning statistics
        self.test_endpoint("GET", "/users/me/statistics")
        
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
        
        # Text generation with parameters
        self.test_endpoint("POST", "/ai/generate-text", {
            "prompt": "Write a short dialogue at a restaurant",
            "max_tokens": 150,
            "temperature": 0.7,
            "language": "en",
            "style": "casual"
        })
        
        # Pronunciation assessment with mock file upload
        try:
            with open("tests/test_audio.wav", "rb") as f:
                files = {
                    'audio_file': ('test_audio.wav', f, 'audio/wav')
                }
                # This endpoint needs a multipart/form-data request, which is not
                # handled by the current test_endpoint method.
                # self.test_endpoint("POST", "/ai/pronunciation-assessment", data=files, headers=None)
        except FileNotFoundError:
            print("⚠️  test_audio.wav not found, skipping pronunciation test")
        
        # Grammar correction
        self.test_endpoint("POST", "/ai/grammar-check", {
            "text": "She don't likes apples. They is very tasty.",
            "language": "en",
            "explanation_level": "detailed"
        })
        
        # Vocabulary suggestions
        self.test_endpoint("POST", "/ai/vocabulary-suggestions", {
            "text": "The food was good and the service was nice.",
            "level": "B1",
            "suggestions_count": 5
        })
        
        # Writing feedback
        self.test_endpoint("POST", "/ai/writing-feedback", {
            "text": "I am learning English since two years. I think I am improve.",
            "task_type": "informal_email",
            "criteria": ["grammar", "vocabulary", "coherence"]
        })
        
        # Conversation practice
        self.test_endpoint("POST", "/ai/conversation-practice/start", {
            "scenario": "job_interview",
            "difficulty": "B1",
            "user_role": "candidate",
            "industry": "technology"
        })
        
        return True

    def test_admin_endpoints(self):
        """Test admin-only endpoints"""
        self.print_header("🔧 Admin Endpoints")
        
        # Switch to admin user
        if not self.login(**ADMIN_CREDENTIALS):
            print("Skipping admin tests - admin login failed")
            return False
        
        # User management
        self.test_endpoint("GET", "/admin/users/")
        
        # Course management
        self.test_endpoint("GET", "/admin/courses/")
        self.test_endpoint("POST", "/admin/courses/", {
            "title": "Test Course",
            "description": "Test Description",
            "is_active": True
        })
        
        # Lesson management
        self.test_endpoint("GET", "/admin/lessons/")
        
        # Subscription management
        return True
        
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
        
        # Comments
        self.test_endpoint("GET", "/forum/posts/1/comments")
        
        return True
        
    def test_analytics_endpoints(self):
        """Test analytics and reporting endpoints"""
        self.print_header("📊 Analytics Endpoints")
        
        # User progress
        self.test_endpoint("GET", "/analytics/user-progress")
        
        # Learning statistics
        self.test_endpoint("GET", "/analytics/learning-stats")
        
        # Activity feed
        self.test_endpoint("GET", "/analytics/activity-feed")
        
        # Time spent
        self.test_endpoint("GET", "/analytics/time-spent")
        
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
        
        # Test utility endpoints
        if not self.test_utility_endpoints():
            print("⚠️ Some utility endpoint tests failed")
            
        # Test payment endpoints
        if not self.test_payment_endpoints():
            print("⚠️ Some payment endpoint tests failed")
            
        # Test forum endpoints
        if not self.test_forum_endpoints():
            print("⚠️ Some forum endpoint tests failed")
            
        # Test analytics endpoints
        if not self.test_analytics_endpoints():
            print("⚠️ Some analytics endpoint tests failed")
        
        print("\n✅ All test suites completed!")

    def print_header(self, title):
        """Print a formatted header for test sections"""
        print(f"\n{'='*50}")
        print(f"{title}")
        print(f"{'='*50}")

if __name__ == "__main__":
    # Using credentials from the memory
    ADMIN_CREDENTIALS = {"username": "test@example.com", "password": "testpassword"}
    TEST_USER_CREDENTIALS = {"username": "test@example.com", "password": "testpassword"}
    
    tester = APITester()
    tester.run_all_tests()
