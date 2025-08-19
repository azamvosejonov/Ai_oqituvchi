import asyncio
from sqlalchemy.orm import Session

from app.db.session import SessionLocal, engine
from app import crud, schemas
from app.core.config import settings

def run_test():
    print("--- Starting Direct DB User Creation Test ---")
    db: Session = SessionLocal()

    try:
        # 1. Check initial user count
        initial_count = crud.user.get_count(db)
        print(f"Initial user count: {initial_count}")

        # 2. Create a new user
        test_email = "direct_db_test@example.com"
        print(f"Creating a new user with email: {test_email}...")
        user_in = schemas.UserCreate(
            email=test_email,
            username="direct_db_tester",
            password="testpassword123",
            full_name="Direct DB Tester"
        )
        
        # First, delete if user already exists to make the script idempotent
        existing_user = crud.user.get_by_email(db, email=test_email)
        if existing_user:
            print(f"User {test_email} already exists. Deleting first.")
            db.delete(existing_user)
            db.commit()
            initial_count = crud.user.get_count(db)
            print(f"User count after deletion: {initial_count}")

        new_user = crud.user.create(db, obj_in=user_in)
        print(f"User created with ID: {new_user.id} and Email: {new_user.email}")

        # 3. Check user count after creation
        count_after_creation = crud.user.get_count(db)
        print(f"User count after creation: {count_after_creation}")

        # 4. Retrieve the created user directly
        print(f"Retrieving user with email {test_email}...")
        retrieved_user = crud.user.get_by_email(db, email=test_email)
        if retrieved_user:
            print(f"Successfully retrieved user: {retrieved_user.email} (ID: {retrieved_user.id})")
        else:
            print(f"!!! FAILED to retrieve the user right after creation.")

    except Exception as e:
        print(f"An error occurred: {e}")
        db.rollback()
    finally:
        print("--- Test Finished ---")
        db.close()

if __name__ == "__main__":
    run_test()
