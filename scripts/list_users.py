import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.session import SessionLocal
from app.models.user import User

def list_all_users():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        if not users:
            print("No users found in the database.")
            return

        print("Listing all users:")
        for user in users:
            print(f"  - User ID: {user.id}, Email: {user.email}, Is Superuser: {user.is_superuser}")

    finally:
        db.close()

if __name__ == "__main__":
    list_all_users()
