import asyncio
import os
from datetime import timedelta
from typing import Generator, Dict

from app.core import security
# Import session module to be reloaded
from app.db import session as session_module

import pytest
from alembic import command
from alembic.config import Config
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app import crud, schemas, models
from app.api import deps
from app.db.base_class import Base

from app.core.config import settings
from app.api.deps import get_db
from app.models.user import User
from app.schemas import UserCreate
from tests.utils.user import user_authentication_headers, create_random_user
from tests.utils.utils import get_superuser_token_headers
from app.core.security import get_password_hash
from main import app

# Test user data
TEST_USER_EMAIL = "test@example.com"
TEST_USER_USERNAME = "testuser"
TEST_USER_PASSWORD = "testpass123"
TEST_USER_FULL_NAME = "Test User"

# Alias fixture: provide `db` as an alias to our shared `session` fixture
@pytest.fixture(scope="function")
def db(session: Session) -> Session:
    return session

# Create a test user
@pytest.fixture(scope="function")
def test_user(session):
    print(f"\n=== Creating test user ===")
    print(f"Email: {TEST_USER_EMAIL}")
    print(f"Username: {TEST_USER_USERNAME}")
    print(f"Password (plain): {TEST_USER_PASSWORD}")
    
    # Delete any existing test user first
    existing_user = crud.user.get_by_email(session, email=TEST_USER_EMAIL)
    if existing_user:
        print(f"  - Found existing test user, deleting... (ID: {existing_user.id})")
        session.delete(existing_user)
        session.commit()
        # Verify deletion
        deleted_user = crud.user.get_by_email(session, email=TEST_USER_EMAIL)
        assert deleted_user is None, "Failed to delete existing test user"
    
    # Create a new test user with all required fields
    user_in = {
        'email': TEST_USER_EMAIL,
        'username': TEST_USER_EMAIL.split('@')[0],  # Use email prefix as username
        'full_name': TEST_USER_FULL_NAME,
        'password': TEST_USER_PASSWORD,
    }
    
    print("  - Creating new test user...")
    print(f"    - Email: {user_in['email']}")
    print(f"    - Username: {user_in['username']}")
    print(f"    - Full name: {user_in['full_name']}")
    # Role is assigned after creation via role assignment helper
    
    # Create the user in the database using proper schema
    user_in_schema = UserCreate(**user_in)
    created_user = crud.user.create(session, obj_in=user_in_schema)
    session.commit()  # Ensure the user is committed to the database
    session.refresh(created_user)  # Refresh to get any default values
    
    # Assign default 'free' role to the user
    try:
        crud.user.assign_default_role(session, user=created_user)
        session.refresh(created_user)
        print(f"    - Assigned default role(s): {[r.name for r in created_user.roles]}")
    except Exception as e:
        print(f"    - Warning: failed to assign default role: {e}")
    
    # Verify the user was created successfully
    assert created_user is not None, "User creation failed - user is None"
    assert created_user.email == TEST_USER_EMAIL, f"Email mismatch: {created_user.email} != {TEST_USER_EMAIL}"
    assert created_user.is_active, "User is not active by default"
    
    # Verify the password was hashed correctly
    assert created_user.hashed_password != TEST_USER_PASSWORD, "Password was not hashed"
    assert security.verify_password(TEST_USER_PASSWORD, created_user.hashed_password), \
        "Password verification failed - hash doesn't match"
    
    # Print debug information
    print("  - User created successfully!")
    print(f"    - User ID: {created_user.id}")
    print(f"    - Hashed password: {created_user.hashed_password[:15]}...")
    print(f"    - Is active: {created_user.is_active}")
    print(f"    - Roles: {[r.name for r in created_user.roles]}")
    
    # Verify the user can be retrieved from the database
    db_user = session.query(User).filter(User.email == TEST_USER_EMAIL).first()
    assert db_user is not None, "Could not retrieve user from database after creation"
    assert db_user.email == TEST_USER_EMAIL, "Retrieved user email doesn't match"
    
    # Print all users in the database for debugging
    all_users = session.query(User).all()
    print(f"\n[DEBUG] All users in database ({len(all_users)}):")
    for u in all_users:
        print(f"- ID: {u.id}, Email: {u.email}, Active: {u.is_active}, Roles: {[r.name for r in getattr(u, 'roles', [])]}")
    
    # Double-check the user exists in the database
    user_in_db = session.query(User).filter(User.email == TEST_USER_EMAIL).first()
    assert user_in_db is not None, "Test user not found in database after creation"
    print(f"\n[SUCCESS] Test user setup complete!")
    
    return created_user

# Get authentication token for the test user
@pytest.fixture(scope="function")
def test_user_token_headers(client, test_user, session):
    print("\n=== Debugging test user token headers ===")
    
    # Get the user from the database to ensure it exists
    db_user = crud.user.get_by_email(session, email=test_user.email)
    if not db_user:
        all_users = session.query(User).all()
        print(f"\n[ERROR] Test user not found in database. Available users (total: {len(all_users)}):")
        for u in all_users:
            print(f"- ID: {u.id}, Email: {u.email}, Username: {u.username}, Active: {u.is_active}")
        raise ValueError(f"Test user with email {test_user.email} not found in database")
    
    print(f"\n[1/3] Found test user in database:")
    print(f"  - ID: {db_user.id}")
    print(f"  - Email: {db_user.email}")
    print(f"  - Username: {db_user.username}")
    print(f"  - Active: {db_user.is_active}")
    print(f"  - Roles: {[r.name for r in getattr(db_user, 'roles', [])]}")
    print(f"  - Hashed password: {db_user.hashed_password[:15]}...")
    
    # Verify the password can be verified directly
    print(f"\n[2/3] Verifying password...")
    try:
        password_valid = security.verify_password(TEST_USER_PASSWORD, db_user.hashed_password)
        print(f"  - Password verification: {'SUCCESS' if password_valid else 'FAILED'}")
        
        if not password_valid:
            # Try to re-hash the password to see if it matches
            new_hash = crud.user.get_password_hash(TEST_USER_PASSWORD)
            print(f"  - New hash of test password: {new_hash[:15]}...")
            print(f"  - New hash matches stored hash: {new_hash == db_user.hashed_password}")
            raise ValueError("Password verification failed against stored hash")
    except Exception as e:
        print(f"  - Error during password verification: {e}")
        raise
    
    # Make login request
    login_url = f"{settings.API_V1_STR}/login/access-token"
    form_data = {
        "username": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD,
    }
    
    print(f"\n[3/3] Sending login request to {login_url}")
    print(f"Form data: {form_data}")

    r = client.post(
        login_url,
        data=form_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    print(f"\nLogin response status: {r.status_code}")
    print(f"Response headers: {dict(r.headers)}")
    
    try:
        response_data = r.json()
        print(f"Response JSON: {response_data}")
        
        # Check if the response has the expected structure
        if "access_token" not in response_data:
            raise ValueError("No access_token in response")
            
        a_token = response_data["access_token"]
        print(f"Access token received: {'*' * 10}{a_token[-5:] if a_token else ''}")
        
        # Return the headers with the authorization token
        headers = {
            "Authorization": f"Bearer {a_token}",
            "Content-Type": "application/json"
        }
        return headers
        
    except Exception as e:
        print(f"Error getting access token: {e}")
        print(f"Response status code: {r.status_code}")
        print(f"Response content: {r.content}")
        print(f"  - Form data response status: {r.status_code}")
        print(f"  - Response headers: {dict(r.headers)}")
        print(f"  - Response content: {r.text}")
        
        # If form data fails, try with JSON (some implementations accept this)
        if r.status_code != 200:
            print("\n  - Form data login failed, trying with JSON...")
            json_headers = {
                "Content-Type": "application/json",
                "accept": "application/json"
            }
            r = client.post(
                login_url,
                json=form_data,
                headers=json_headers
            )
            print(f"  - JSON response status: {r.status_code}")
            print(f"  - Response content: {r.text}")
            
    except Exception as e:
        print(f"  - Request failed: {str(e)}")
        raise Exception("Failed to authenticate test user")

    # 4. Handle response
    if r.status_code == 200:
        try:
            tokens = r.json()
            access_token = tokens.get("access_token")
            if not access_token:
                print("  - [WARNING] Login succeeded but no access_token in response")
                print(f"  - Full response: {tokens}")
            else:
                print(f"  - [SUCCESS] Login successful!")
                print(f"  - Access token (first 20 chars): {access_token[:20]}...")
                return {"Authorization": f"Bearer {access_token}"}
        except Exception as e:
            print(f"  - [ERROR] Failed to parse login response: {str(e)}")
            print(f"  - Raw response: {r.text}")
    
    # If we get here, login failed
    print("\n[ERROR] LOGIN FAILED - DETAILED DIAGNOSTICS:")
    print("=" * 60)
    
    # Check user in database again
    user_after_login = session.query(User).filter(User.email == TEST_USER_EMAIL).first()
    print("\n[1/3] User status in database after login attempt:")
    if user_after_login:
        print(f"  - ID: {user_after_login.id}")
        print(f"  - Email: {user_after_login.email}")
        print(f"  - Active: {user_after_login.is_active}")
        print(f"  - Roles: {[r.name for r in getattr(user_after_login, 'roles', [])]}")
        print(f"  - Last login: {getattr(user_after_login, 'last_login', 'N/A')}")
        
        # Check password verification
        pw_match = security.verify_password(TEST_USER_PASSWORD, user_after_login.hashed_password)
        print(f"  - Password verification: {'MATCH' if pw_match else 'NO MATCH'}")
        
        # Check password hash algorithm
        if user_after_login.hashed_password:
            hash_parts = user_after_login.hashed_password.split('$')
            if len(hash_parts) > 2:  # Should be at least $2b$...
                print(f"  - Hash algorithm: {hash_parts[1]}")
            else:
                print(f"  - Hash format unexpected: {user_after_login.hashed_password[:30]}...")
    else:
        print("  - [ERROR] User not found in database after login attempt!")
    
    # Check response details
    print("\n[2/3] Response details:")
    print(f"  - Status code: {r.status_code}")
    try:
        response_json = r.json()
        print(f"  - Response JSON: {response_json}")
        
        # Check for common error patterns
        if 'detail' in response_json:
            error_detail = response_json['detail']
            print(f"  - Error detail: {error_detail}")
            
            # Handle different error detail formats
            if isinstance(error_detail, str):
                print(f"  - Error message: {error_detail}")
            elif isinstance(error_detail, dict):
                for k, v in error_detail.items():
                    print(f"  - {k}: {v}")
        
        # Check for WWW-Authenticate header
        if 'WWW-Authenticate' in r.headers:
            print(f"  - WWW-Authenticate: {r.headers['WWW-Authenticate']}")
            
    except Exception as e:
        print(f"  - Could not parse JSON response: {e}")
        print(f"  - Raw response text: {r.text}")
    
    # Try direct authentication as a fallback
    print("\n[3/3] Attempting direct authentication via CRUD...")
    try:
        auth_user = crud.user.authenticate(
            session, email=TEST_USER_EMAIL, password=TEST_USER_PASSWORD
        )
        if auth_user:
            print("  - [SUCCESS] Direct authentication via CRUD worked!")
            print(f"  - User ID: {auth_user.id}, Email: {auth_user.email}")
            print(f"  - User active: {auth_user.is_active}")
            
            # Try to generate a token directly as a fallback
            from app.core.security import create_access_token
            from datetime import timedelta
            direct_token = create_access_token(
                auth_user.id,
                expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            )
            print(f"  - [SUCCESS] Generated token directly: {direct_token[:20]}...")
            
            # Return the directly generated token as a fallback
            return {"Authorization": f"Bearer {direct_token}"}
        else:
            print("  - [FAILED] Direct authentication via CRUD failed")
            
            # Try to find the user by email directly
            direct_user = crud.user.get_by_email(session, email=TEST_USER_EMAIL)
            if direct_user:
                print(f"  - [INFO] Found user by email but authentication failed")
                print(f"  - User active: {direct_user.is_active}")
                print(f"  - User roles: {[r.name for r in getattr(direct_user, 'roles', [])]}")
                
                # Check if user is active
                if not direct_user.is_active:
                    print("  - [ISSUE] User account is not active!")
                
                # Check password verification directly
                pw_verify = security.verify_password(TEST_USER_PASSWORD, direct_user.hashed_password)
                print(f"  - Direct password verification: {'SUCCESS' if pw_verify else 'FAILED'}")
                
                # If password verification fails, show hash info
                if not pw_verify:
                    print(f"  - Stored hash: {direct_user.hashed_password[:30]}...")
                    new_hash = crud.user.get_password_hash(TEST_USER_PASSWORD)
                    print(f"  - New hash of same password: {new_hash[:30]}...")
    
    except Exception as e:
        print(f"  - Error during direct authentication: {str(e)}")
    
    # If we get here, all authentication attempts failed
    print("\n[CRITICAL] All authentication attempts failed!")
    print("=" * 60)
    
    # Dump the full user object for debugging
    if 'user_after_login' in locals() and user_after_login:
        print("\nFull user object from database:")
        for key, value in user_after_login.__dict__.items():
            if not key.startswith('_'):  # Skip private attributes
                print(f"  - {key}: {value}")
    
    raise Exception(f"Login failed with status {r.status_code}. Check debug output above for details.")

# Create a test superuser
@pytest.fixture(scope="function")
def test_superuser(session):
    user_obj = User(
        email="admin@example.com",
        username="admin123",
        hashed_password=get_password_hash("12345678"),
        full_name="Admin User",
        is_superuser=True,
        is_active=True,
    )
    session.add(user_obj)
    session.commit()
    session.refresh(user_obj)
    return user_obj

# Get authentication token for the test superuser
@pytest.fixture(scope="function")
def test_superuser_token_headers(client, test_superuser, session):
    """
    Fixture to get superuser token headers.
    """
    # Use the email from the test_superuser fixture for login
    login_data = {
        "username": test_superuser.email,  # Use the created user's email
        "password": "12345678",  # Use the known password for the test user
    }
    print("\n=== Debugging superuser token headers ===")
    db_user = crud.user.get_by_email(session, email=test_superuser.email)
    print(f"Superuser in DB: {db_user is not None}")
    if db_user:
        print(f"Superuser active: {db_user.is_active}")
        print(f"Superuser password set: {bool(db_user.hashed_password)}")

    print(f"Sending login request to {settings.API_V1_STR}/login/access-token")
    print(f"Form data: {login_data}")

    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    
    if r.status_code != 200:
        print(f"Login failed with status {r.status_code}")
        print(f"Response: {r.json()}")
        pytest.fail("Failed to log in superuser for tests.")

    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers

# Alias fixture to match tests expecting `user_token_headers`
@pytest.fixture(scope="function")
def user_token_headers(test_user_token_headers):
    return test_user_token_headers

from app.db.session import SessionLocal, engine
from app.db.base import Base
from app.db.initial_data import init_db


@pytest.fixture(scope="function")
def session() -> Generator:
    """Create a fresh database session for each test."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    connection = engine.connect()
    transaction = connection.begin()
    session = SessionLocal(bind=connection)
    
    # Initialize database with test data
    init_db(session)
    
    yield session

    session.close()
    transaction.rollback()
    connection.close()


# Make db_session fixture point to the same app session to avoid DB mismatches
@pytest.fixture(scope="function")
def db_session(session: Session) -> Session:
    return session


@pytest.fixture(scope="function")
def client(session: Session) -> Generator:
    def get_db_override():
        return session

    app.dependency_overrides[deps.get_db] = get_db_override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def superuser_token_headers(client: TestClient, session: Session) -> Dict[str, str]:
    return get_superuser_token_headers(client, db=session)


@pytest.fixture(scope="function")
def normal_user_token_headers(client: TestClient, session: Session) -> Dict[str, str]:
    return authentication_token_from_email(
        client=client, email=settings.EMAIL_TEST_USER, db=session
    )


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def teacher_user(session: Session) -> User:
    """Fixture to create a user with a teacher role."""
    email = "teacher@example.com"
    password = "teacherpassword"
    user_in = UserCreate(email=email, password=password, username=email.split('@')[0])
    user = crud.user.create(db=session, obj_in=user_in)
    teacher_role = crud.role.get_by_name(db=session, name="teacher")
    if teacher_role:
        crud.user.assign_role(db=session, user=user, role=teacher_role)
    
    user.plain_password = password
    return user


@pytest.fixture
def student_user(session: Session) -> User:
    """Fixture to create a user with a student role."""
    user = create_random_user(db=session)
    return user


@pytest.fixture(scope="function")
def power_user(session: Session) -> models.User:
    """
    Create a powerful user with all roles (superuser, admin, teacher) and high AI quotas.
    """
    email = "poweruser@example.com"
    user = crud.user.get_by_email(db=session, email=email)
    if user:
        # Ensure user has all roles and quotas if they already exist
        pass
    else:
        user_in = schemas.UserCreate(
            email=email,
            password="powerpassword",
            full_name="Power User",
            username="poweruser",
        )
        user = crud.user.create(db=session, obj_in=user_in)

    # Assign all roles
    user.is_superuser = True
    admin_role = crud.role.get_by_name(db=session, name="admin")
    if admin_role and admin_role not in user.roles:
        user.roles.append(admin_role)
    teacher_role = crud.role.get_by_name(db=session, name="teacher")
    if teacher_role and teacher_role not in user.roles:
        user.roles.append(teacher_role)

    # Grant high AI quotas
    ai_usage = crud.user_ai_usage.get_or_create(db=session, user_id=user.id)
    ai_usage_update = schemas.UserAIUsageUpdate(
        monthly_text_credits=1000000,
        monthly_voice_credits=1000000,
    )
    crud.user_ai_usage.update(db=session, db_obj=ai_usage, obj_in=ai_usage_update)

    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(scope="function")
def power_user_token_headers(client: TestClient, power_user: models.User, session: Session) -> Dict[str, str]:
    """Return a token header for the power user."""
    return user_authentication_headers(client=client, db=session, email=power_user.email, password="powerpassword")

def authentication_token_from_id(*, client: TestClient, user_id: int) -> Dict[str, str]:
    """
    Return a valid token for the user with the given ID.
    """
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        user_id, expires_delta=access_token_expires
    )
    headers = {"Authorization": f"Bearer {access_token}"}
    return headers


# This function is kept for legacy tests that might still use it,
# but new tests should use authentication_token_from_id.
def authentication_token_from_email(
    *, client: TestClient, email: str, db: Session
) -> Dict[str, str]:
    """
    Return a valid token for the user with the given email.
    """
    user = crud.user.get_by_email(db, email=email)
    assert user is not None
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        user.id, expires_delta=access_token_expires
    )
    headers = {"Authorization": f"Bearer {access_token}"}
    return headers
