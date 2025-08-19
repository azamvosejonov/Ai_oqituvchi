"""
Script to create a test user in the database.
"""
import sys
import os
from pathlib import Path

# Add project root to the Python path
ROOT_DIR = Path(__file__).resolve().parent
sys.path.append(str(ROOT_DIR))

# Set environment variables
os.environ["ENVIRONMENT"] = "dev"
os.environ["DATABASE_URL"] = "sqlite:///./oquv_app.db"

# Import SQLAlchemy and models
from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine
from app.models.user import User
from app.core.security import get_password_hash

def create_test_user():
    """Create a test user in the database."""
    db = SessionLocal()
    try:
        # Check if test user already exists
        test_user = db.query(User).filter(User.email == "test@example.com").first()
        if test_user:
            print("Test user already exists:")
            print(f"Email: {test_user.email}")
            return
        
        # Create test user
        hashed_password = get_password_hash("testpassword")
        test_user = User(
            email="test@example.com",
            username="testuser",  # Adding required username field
            hashed_password=hashed_password,
            full_name="Test User",
            is_active=True,
            is_superuser=False
        )
        
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        print("Test user created successfully:")
        print(f"Email: {test_user.email}")
        print(f"Password: testpassword")
        
    except Exception as e:
        print(f"Error creating test user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Creating test user...")
    create_test_user()
