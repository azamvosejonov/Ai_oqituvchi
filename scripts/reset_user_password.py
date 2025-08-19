import sys
import os
import argparse

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.security import get_password_hash
from app.db.session import SessionLocal
from app.models.user import User

def reset_user_password(email: str, new_password: str):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"User with email {email} not found")
            return
        
        user.hashed_password = get_password_hash(new_password)
        db.commit()
        
        print(f"Password for {user.email} has been reset to: {new_password}")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reset a user's password.")
    parser.add_argument("email", type=str, help="User's email address")
    parser.add_argument("password", type=str, help="The new password")
    args = parser.parse_args()
    reset_user_password(args.email, args.password)
