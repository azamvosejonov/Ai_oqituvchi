import sys
import os
from pathlib import Path

# Add project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

from app.db.session import SessionLocal
from app import crud, schemas
from app.core.config import settings

def create_admin_user():
    db = SessionLocal()
    try:
        # Check if admin user already exists
        admin = crud.user.get_by_email(db, email="admin@example.com")
        if admin:
            print("Admin user already exists")
            return admin
        
        # Create admin user
        user_in = schemas.UserCreate(
            email="admin@example.com",
            username="admin",
            password="admin123",
            is_superuser=True,
            is_active=True
        )
        admin = crud.user.create(db, obj_in=user_in)
        print(f"Admin user created: {admin.email}")
        return admin
    except Exception as e:
        print(f"Error creating admin user: {e}")
        return None
    finally:
        db.close()

if __name__ == "__main__":
    print("Creating test admin user...")
    admin = create_admin_user()
    if admin:
        print(f"Admin user created successfully!")
        print(f"Email: {admin.email}")
        print(f"Password: admin123")
    else:
        print("Failed to create admin user")
