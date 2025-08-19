import requests
import os
import json
from typing import Dict, List, Tuple, Optional, Any

# Base URL for API (without trailing slash)
BASE_URL = "http://0.0.0.0:8004"  # Base URL without /api/v1 as it's added in the router
API_PREFIX = "/api/v1"  # API version prefix

# Test credentials
TEST_CREDENTIALS = {
    "username": "test@example.com",
    "password": "testpassword"
}

class EndpointTester:
    def __init__(self, base_url: str, credentials: Dict[str, str]):
        self.base_url = base_url
        self.credentials = credentials
        self.session = requests.Session()
        self.token = None
        self.logs = []
    
    def log(self, message: str, error: bool = False):
        """Log a message with timestamp"""
        log_entry = f"[{'ERROR' if error else 'INFO'}] {message}"
        self.logs.append(log_entry)
        print(log_entry)
    
    def login(self) -> bool:
        """Login and get authentication token"""
        try:
            self.log(f"Attempting to login as {self.credentials['username']}")
            response = self.session.post(
                f"{self.base_url}/api/v1/login",
                json={
                    "username": self.credentials["username"],
                    "password": self.credentials["password"]
                },
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code != 200:
                self.log(f"Login failed with status {response.status_code}: {response.text}", error=True)
                return False
            
            token_data = response.json()
            self.token = token_data.get("access_token")
            
            if not self.token:
                self.log("No access token in login response", error=True)
                return False
                
            self.log("Login successful")
            return True
            
        except Exception as e:
            self.log(f"Login error: {str(e)}", error=True)
            return False
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get headers with authentication token"""
        if not self.token:
            if not self.login():
                return {}
        return {"Authorization": f"Bearer {self.token}"}
    
    def check_endpoint(
        self, 
        method: str, 
        path: str, 
        expected_status: int = 200,
        json_data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        retry_auth: bool = True
    ) -> bool:
        """Check if an endpoint returns the expected status code"""
        url = f"{self.base_url}{path}"
        headers = self.get_auth_headers()
        
        if not headers and path != "/health":
            self.log(f"Skipping {method} {path} - Not authenticated", error=True)
            return False
        
        try:
            self.log(f"Testing {method} {path}")
            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                json=json_data,
                params=params,
                timeout=10,
                allow_redirects=False
            )
            
            # Handle redirects
            if 300 <= response.status_code < 400 and 'Location' in response.headers:
                self.log(f"Following redirect from {url} to {response.headers['Location']}")
                return self.check_endpoint(
                    method=method,
                    path=response.headers['Location'],
                    expected_status=expected_status,
                    json_data=json_data,
                    params=params,
                    retry_auth=False
                )
            
            if response.status_code != expected_status:
                self.log(
                    f"Expected status {expected_status}, got {response.status_code} for {method} {path}", 
                    error=True
                )
                
                # Log detailed error for 4xx/5xx responses
                if response.status_code >= 400:
                    try:
                        error_details = response.json()
                        self.log(f"Error details: {json.dumps(error_details, indent=2)}", error=True)
                        
                        # If it's a 404, log the full URL that was tried
                        if response.status_code == 404:
                            self.log(f"Endpoint not found: {method} {url}", error=True)
                    except:
                        self.log(f"Response: {response.text}", error=True)
                
                # Try to re-authenticate and retry if this is the first failure
                if retry_auth and response.status_code in (401, 403):
                    self.log("Authentication failed, attempting to re-authenticate...")
                    if self.login():
                        return self.check_endpoint(
                            method=method,
                            path=path,
                            expected_status=expected_status,
                            json_data=json_data,
                            params=params,
                            retry_auth=False
                        )
                
                return False
                
            self.log(f"✓ {method} {path} - Status {response.status_code}")
            return True
            
        except Exception as e:
            self.log(f"Error checking {method} {path}: {str(e)}", error=True)
            return False

def main():
    print("🔍 Starting API Endpoint Tester 🔍\n")
    
    # Initialize the tester
    tester = EndpointTester(BASE_URL, TEST_CREDENTIALS)
    
    # List of endpoints to check with their expected status codes
    endpoints = [
        # Root endpoints (no API prefix)
        ("GET", "/health", 200),  # Health check should always work
        ("GET", "/version", 200),  # Version endpoint
        ("GET", "/docs", 200),     # Swagger docs
        ("GET", "/redoc", 200),    # ReDoc docs
        
        # API v1 endpoints (with API prefix)
        ("GET", f"{API_PREFIX}/users/me", 200),
        ("GET", f"{API_PREFIX}/notifications/", 200),
        ("GET", f"{API_PREFIX}/subscription-plans/", 200),
        ("GET", f"{API_PREFIX}/lessons/", 200),
        ("GET", f"{API_PREFIX}/lessons/categories", 200),
        ("GET", f"{API_PREFIX}/ai/tts/voices", 200),
        ("GET", f"{API_PREFIX}/ai/stt/languages", 200),
        
        # Add more endpoints as needed, making sure to include the API_PREFIX for API endpoints
    ]
    
    # Run the tests
    results = {}
    for method, path, expected_status in endpoints:
        success = tester.check_endpoint(method, path, expected_status=expected_status)
        results[f"{method} {path}"] = success
    
    # Print summary
    print("\n📊 Test Results:")
    print("=" * 40)
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    failed = total - passed
    
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {(passed/total)*100:.1f}%\n")
    
    # Print detailed results
    print("🔍 Detailed Results:")
    print("-" * 40)
    for endpoint, success in results.items():
        status = "✅" if success else "❌"
        print(f"{status} {endpoint}")
    
    # Print any errors from the logs
    errors = [log for log in tester.logs if "ERROR" in log]
    if errors:
        print("\n❌ Errors encountered:")
        print("-" * 40)
        for error in errors:
            print(error)
    
    # Save logs to file
    with open("api_test_logs.txt", "w") as f:
        f.write("\n".join(tester.logs))
    
    print(f"\n📝 Full logs saved to: api_test_logs.txt")

if __name__ == "__main__":
    main()
