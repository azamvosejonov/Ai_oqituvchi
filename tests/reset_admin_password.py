import sys
import os
from pathlib import Path

# Add project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

from app.db.session import SessionLocal
from app import crud
from app.core.security import get_password_hash

def reset_admin_password():
    db = SessionLocal()
    try:
        admin_email = "admin@example.com"
        new_password = "admin123"

        user = crud.user.get_by_email(db, email=admin_email)

        if not user:
            print(f"Admin user with email {admin_email} not found.")
            return

        hashed_password = get_password_hash(new_password)
        user.hashed_password = hashed_password
        db.add(user)
        db.commit()
        print(f"Password for admin user {admin_email} has been reset successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    reset_admin_password()
