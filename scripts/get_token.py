import requests
import json
import argparse

def get_user_token(username, password):
    login_data = {
        "username": username,
        "password": password
    }
    response = requests.post(
        "http://0.0.0.0:8004/api/v1/login",
        headers={"Content-Type": "application/json"},
        data=json.dumps(login_data)
    )
    if response.status_code == 200:
        token_data = response.json()
        print(token_data.get("access_token"))
    else:
        print(f"Failed to get token. Status: {response.status_code}, Response: {response.text}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get access token for a user.")
    parser.add_argument("username", type=str, help="User's email address")
    parser.add_argument("password", type=str, help="User's password")
    args = parser.parse_args()
    get_user_token(args.username, args.password)
