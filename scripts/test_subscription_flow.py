import requests
import time
import random
import string

# --- Test Configuration ---
BASE_URL = "http://127.0.0.1:8002"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "changethis"

# --- Helper Functions ---

def random_string(length=8):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

def print_status(message, success=True):
    status = " SUCCESS" if success else " FAILED"
    print(f"{status}: {message}")

class APIClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()

    def login(self, email, password):
        url = f"{self.base_url}/api/v1/login/access-token"
        data = {"username": email, "password": password}
        try:
            response = self.session.post(url, data=data)
            response.raise_for_status()
            token = response.json()["access_token"]
            self.session.headers.update({"Authorization": f"Bearer {token}"})
            print_status(f"Logged in as {email}")
            return True
        except requests.exceptions.RequestException as e:
            print_status(f"Login failed for {email}: {e}", success=False)
            return False

    def post(self, endpoint, json=None, params=None):
        return self.session.post(f"{self.base_url}{endpoint}", json=json, params=params)

    def get(self, endpoint):
        return self.session.get(f"{self.base_url}{endpoint}")

    def delete(self, endpoint):
        return self.session.delete(f"{self.base_url}{endpoint}")

# --- Test Flow ---

def run_test():
    admin_client = APIClient(BASE_URL)
    user_client = APIClient(BASE_URL)

    plan_id = None
    user_id = None
    user_subscription_id = None

    # 1. Admin logs in
    if not admin_client.login(ADMIN_EMAIL, ADMIN_PASSWORD):
        return

    try:
        # 2. Admin creates a new subscription plan
        plan_name = f"TestPlan_{random_string(4)}"
        plan_data = {"name": plan_name, "price": 10.0, "duration_days": 30}
        response = admin_client.post("/api/v1/subscription-plans/", json=plan_data)
        if response.status_code == 201:
            plan_id = response.json()["id"]
            print_status(f"Created subscription plan '{plan_name}' with ID {plan_id}")
        else:
            print_status(f"Failed to create subscription plan: {response.text}", success=False)
            return

        # 3. Admin creates a new user
        user_email = f"testuser_{random_string()}@example.com"
        user_password = "testpassword"
        user_data = {
            "username": user_email,
            "email": user_email,
            "password": user_password,
            "full_name": "Test User"
        }
        response = admin_client.post("/api/v1/users/", json=user_data)
        if response.status_code == 201:
            user_id = response.json()["id"]
            print_status(f"Created user '{user_email}' with ID {user_id}")
        else:
            print_status(f"Failed to create user: {response.text}", success=False)
            admin_client.delete(f"/api/v1/subscription-plans/{plan_id}") # Cleanup plan
            return

        # 4. New user logs in
        if not user_client.login(user_email, user_password):
            # Cleanup
            admin_client.delete(f"/api/v1/admin/users/{user_id}")
            admin_client.delete(f"/api/v1/subscription-plans/{plan_id}")
            return

        # 5. User tries to access premium data (should fail)
        response = user_client.get("/api/v1/users/me/premium-data")
        if response.status_code == 403:
            print_status("User correctly blocked from premium data (no subscription)")
        else:
            print_status(f"User incorrectly allowed access to premium data: {response.status_code}", success=False)

        # 6. Admin assigns subscription to the user
        response = admin_client.post(f"/api/v1/subscriptions/users/{user_id}/subscriptions", params={"plan_id": plan_id})
        if response.status_code == 201:
            user_subscription_id = response.json()["id"]
            print_status(f"Assigned plan {plan_id} to user {user_id}")
        else:
            print_status(f"Failed to assign subscription: {response.text}", success=False)

        # 7. User tries to access premium data again (should succeed)
        response = user_client.get("/api/v1/users/me/premium-data")
        if response.status_code == 200:
            print_status("User correctly allowed access to premium data")
            print(f"    -> Premium message: {response.json()['msg']}")
        else:
            print_status(f"User incorrectly blocked from premium data: {response.status_code}", success=False)

    finally:
        print("\n--- Starting Cleanup ---")
        # Clean up in reverse order of creation
        if user_subscription_id:
            # This endpoint needs to exist for cleanup
            response = admin_client.delete(f"/api/v1/subscriptions/{user_subscription_id}")
            if response.status_code == 200:
                print(f" SUCCESS: Cleaned up user subscription {user_subscription_id}")
            else:
                print(f" FAILED: Failed to clean up user subscription {user_subscription_id}: {response.status_code} {response.text}")

        if user_id:
            # Assuming an admin endpoint to delete users exists
            # response = admin_client.delete(f"/api/v1/admin/users/{user_id}")
            # if response.status_code == 200:
            #     print(f" SUCCESS: Cleaned up user {user_id}")
            # else:
            #     print(f" FAILED: Failed to clean up user {user_id}")
            pass # Temporarily skipping user deletion

        if plan_id:
            response = admin_client.delete(f"/api/v1/subscription-plans/{plan_id}")
            if response.status_code == 200:
                print_status(f"Cleaned up plan {plan_id}")
            else:
                print_status(f"Failed to clean up plan {plan_id}", success=False)

if __name__ == "__main__":
    print("--- Starting API Subscription Flow Test ---")
    print("NOTE: Ensure the FastAPI server is running before executing this script.")
    time.sleep(2)
    run_test()
