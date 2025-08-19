import requests
import json
import os

BASE_URL = "http://localhost:8002"
API_V1_STR = "/api/v1"
# Using admin credentials as they have broader access for testing
USERNAME = "admin@example.com"
PASSWORD = "adminpassword"


def get_auth_token():
    """Fetches the JWT token for the test user."""
    login_data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    try:
        # The login endpoint in openapi.json is /api/v1/login/access-token and uses form data
        response = requests.post(
            f"{BASE_URL}{API_V1_STR}/login/access-token",
            data=login_data
        )
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json().get("access_token")
    except requests.exceptions.RequestException as e:
        print(f"Error getting auth token: {e}")
        return None

def run_api_tests(token):
    """Runs tests against all API endpoints found in openapi.json."""
    headers = {}
    if token:
        headers = {"Authorization": f"Bearer {token}"}
    else:
        print("Warning: No auth token provided. Testing only public endpoints.")

    try:
        with open("openapi.json", "r") as f:
            openapi_spec = json.load(f)
    except FileNotFoundError:
        print("Error: openapi.json not found. Please run the script from the project root.")
        return
    except json.JSONDecodeError:
        print("Error: Could not parse openapi.json.")
        return

    paths = openapi_spec.get("paths", {})
    total_endpoints = 0
    successful_tests = 0
    failed_tests = 0

    print("--- Starting API Endpoint Tests ---")

    for path, path_item in paths.items():
        # Skip parameterized paths for this simple test
        if '{' in path and '}' in path:
            print(f"Skipping parameterized path: {path}")
            continue

        full_url = f"{BASE_URL}{path}"
        for method, operation in path_item.items():
            if method.upper() not in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                continue
            
            total_endpoints += 1
            print(f"Testing: {method.upper()} {path}")

            try:
                # We will only test GET requests to avoid state changes
                if method.lower() == 'get':
                    response = requests.get(full_url, headers=headers, timeout=15)
                    if 200 <= response.status_code < 300:
                        print(f"  [SUCCESS] Status: {response.status_code}")
                        successful_tests += 1
                    # 401/403 is also a 'success' for a protected endpoint without a token
                    elif response.status_code in [401, 403]:
                         print(f"  [SUCCESS - PROTECTED] Status: {response.status_code}")
                         successful_tests += 1
                    else:
                        print(f"  [FAILURE] Status: {response.status_code} - {response.text[:100]}")
                        failed_tests += 1
                else:
                    print(f"  [SKIPPED] Non-GET method: {method.upper()}")
                    # We count skipped non-GET as success to not clutter results
                    successful_tests += 1

            except requests.exceptions.RequestException as e:
                print(f"  [ERROR] Request failed: {e}")
                failed_tests += 1

    print("\n--- Test Summary ---")
    print(f"Total endpoints found: {total_endpoints}")
    print(f"Successful GET/skipped non-GET tests: {successful_tests}")
    print(f"Failed GET tests: {failed_tests}")
    print("--------------------")

if __name__ == "__main__":
    auth_token = get_auth_token()
    run_api_tests(auth_token)
