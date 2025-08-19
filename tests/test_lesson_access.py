import os
import pytest
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Depends
from datetime import datetime, timedelta

from app import crud, models
from app.core.security import get_password_hash
from app.models.user import Role, User
from app.models.course import Course
from app.models.lesson import InteractiveLesson as Lesson
from app.models.subscription import Subscription, SubscriptionPlan
from app.schemas.user import UserCreate, UserUpdate, UserInDB
from app.schemas.course import CourseCreate, CourseInDB
from app.schemas.lesson import LessonCreate, LessonInDB
from app.schemas.subscription import SubscriptionCreate
from main import app
from tests.utils.user import create_random_user, user_authentication_headers
from fastapi.testclient import TestClient

# Helper function to generate random strings for testing
def random_lower_string() -> str:
    import random
    import string
    return ''.join(random.choices(string.ascii_lowercase, k=32))

# Helper function to create a test user
def create_test_user(db: Session, email: str, password: str, role_name: str = "free") -> User:
    """Helper function to create a test user with a specific role."""
    # Fetch the role from the database
    role = db.query(Role).filter(Role.name == role_name).first()
    if not role:
        # If role doesn't exist, create it for testing purposes
        role = Role(name=role_name, description=f"{role_name.capitalize()} role")
        db.add(role)
        db.commit()
        db.refresh(role)

    user_in = UserCreate(email=email, password=password, username=random_lower_string())
    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        username=user_in.username,
        is_active=True,
    )
    db.add(user)
    # Assign role via many-to-many relationship
    user.roles.append(role)
    db.commit()
    db.refresh(user)
    return user

# Helper function to create a test course
def create_test_course(db: Session, creator_id: int, title: str = "Test Course") -> Course:
    course_in = CourseCreate(
        title=title,
        description="Test Description",
        difficulty_level="A1",
        instructor_id=creator_id
    )
    return crud.course.create(db, obj_in=course_in)

# Helper function to create a test lesson
def create_test_lesson(db: Session, course_id: int, avatar_id: int, title: str = "Test Lesson", is_premium: bool = False) -> Lesson:
    lesson_in = LessonCreate(
        title=title,
        content="Test Content",
        course_id=course_id,
        order=1,
        is_premium=is_premium,
        avatar_id=avatar_id
    )
    return crud.lesson.create(db, obj_in=lesson_in)

# Helper function to create a subscription plan
def create_subscription_plan(db: Session, name: str = "Premium Plan") -> SubscriptionPlan:
    plan = models.SubscriptionPlan(
        name=name,
        price=9.99,
        description="Test Plan",
        stripe_price_id=f"price_{name.lower().replace(' ', '_')}",
        gpt4o_requests_quota=100,
        stt_requests_quota=200,
        tts_chars_quota=10000,
        pronunciation_analysis_quota=50,
        gemini_requests_quota=100
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan

# Helper function to create a subscription
def create_subscription(db: Session, user_id: int, plan_id: int) -> Subscription:
    subscription = models.Subscription(
        user_id=user_id,
        plan_id=plan_id,
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow() + timedelta(days=30),
        is_active=True
    )
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    return subscription


def test_get_accessible_lessons_for_free_user(client: TestClient, db: Session) -> None:
    # Create a free user
    email = "free_user@example.com"
    password = "testpass123"
    user = create_test_user(db, email=email, password=password, role_name="free")
    
    # Create a course creator
    creator = create_test_user(
        db, 
        email="creator@example.com", 
        password="creatorpass123", 
        role_name="free"
    )
    
    # Create a course with both free and premium lessons
    course = create_test_course(db, creator_id=creator.id, title="Test Course")
    
    # Create lessons (2 free, 1 premium)
    free_lesson1 = create_test_lesson(
        db, 
        course_id=course.id, 
        avatar_id=1,
        title="Free Lesson 1", 
        is_premium=False
    )
    free_lesson2 = create_test_lesson(
        db, 
        course_id=course.id, 
        avatar_id=1,
        title="Free Lesson 2", 
        is_premium=False
    )
    premium_lesson = create_test_lesson(
        db, 
        course_id=course.id, 
        avatar_id=1,
        title="Premium Lesson", 
        is_premium=True
    )
    
    # Test getting accessible lessons for free user
    accessible_lessons = crud.lesson.get_accessible_lessons(db, user=user, course_id=course.id)
    
    # Verify only free lessons are accessible
    assert len(accessible_lessons) == 2
    assert {lesson.id for lesson in accessible_lessons} == {free_lesson1.id, free_lesson2.id}
    assert premium_lesson.id not in {lesson.id for lesson in accessible_lessons}
    
    # Verify can_access_lesson method
    assert crud.lesson.can_access_lesson(db, user=user, lesson_id=free_lesson1.id) is True
    assert crud.lesson.can_access_lesson(db, user=user, lesson_id=premium_lesson.id) is False


def test_get_accessible_lessons_for_premium_user(client: TestClient, db: Session) -> None:
    # Create a premium user
    email = "premium_user@example.com"
    password = "testpass123"
    user = create_test_user(db, email=email, password=password, role_name="premium")
    
    # Create a course creator
    creator = create_test_user(
        db, 
        email="creator2@example.com", 
        password="creatorpass123", 
        role_name="free"
    )
    
    # Create a course with both free and premium lessons
    course = create_test_course(db, creator_id=creator.id, title="Premium Test Course")
    
    # Create lessons (2 free, 1 premium)
    free_lesson1 = create_test_lesson(
        db, 
        course_id=course.id, 
        avatar_id=1,
        title="Free Lesson 1", 
        is_premium=False
    )
    premium_lesson1 = create_test_lesson(
        db, 
        course_id=course.id, 
        avatar_id=1,
        title="Premium Lesson 1", 
        is_premium=True
    )
    premium_lesson2 = create_test_lesson(
        db, 
        course_id=course.id, 
        avatar_id=1,
        title="Premium Lesson 2", 
        is_premium=True
    )
    
    # Test getting accessible lessons for premium user (limit to this course)
    accessible_lessons = crud.lesson.get_accessible_lessons(db, user=user, course_id=course.id)
    
    # Verify all lessons are accessible to premium user
    assert len(accessible_lessons) == 3
    assert {lesson.id for lesson in accessible_lessons} == {
        free_lesson1.id, 
        premium_lesson1.id, 
        premium_lesson2.id
    }
    
    # Verify can_access_lesson method
    assert crud.lesson.can_access_lesson(db, user=user, lesson_id=free_lesson1.id) is True
    assert crud.lesson.can_access_lesson(db, user=user, lesson_id=premium_lesson1.id) is True
    assert crud.lesson.can_access_lesson(db, user=user, lesson_id=premium_lesson2.id) is True


def test_creator_access_to_own_lessons(client: TestClient, db: Session) -> None:
    # Create a course creator
    creator = create_test_user(
        db, 
        email="creator3@example.com", 
        password="creatorpass123", 
        role_name="free"
    )
    
    # Create a course with premium lessons
    course = create_test_course(db, creator_id=creator.id, title="Creator's Course")
    
    # Create a premium lesson
    premium_lesson = create_test_lesson(
        db, 
        course_id=course.id, 
        avatar_id=1,
        title="Creator's Premium Lesson", 
        is_premium=True
    )
    
    # Verify creator can access their own premium lesson
    assert crud.lesson.can_access_lesson(db, user_id=creator.id, lesson_id=premium_lesson.id) is True
    
    # Create another free user
    free_user = create_test_user(
        db, 
        email="free_user2@example.com", 
        password="testpass123", 
        role_name="free"
    )
    
    # Verify free user cannot access premium lesson
    assert crud.lesson.can_access_lesson(db, user_id=free_user.id, lesson_id=premium_lesson.id) is False


def test_admin_access_to_all_lessons(client: TestClient, db: Session) -> None:
    # Create an admin user
    admin = create_test_user(
        db, 
        email="admin_test1@example.com", 
        password="adminpass123", 
        role_name="admin"
    )
    
    # Create a course creator
    creator = create_test_user(
        db, 
        email="creator4@example.com", 
        password="creatorpass123", 
        role_name="free"
    )
    
    # Create a course with premium lessons
    course = create_test_course(db, creator_id=creator.id, title="Admin Test Course")
    
    # Create a premium lesson
    premium_lesson = create_test_lesson(
        db, 
        course_id=course.id, 
        avatar_id=1,
        title="Admin Test Premium Lesson", 
        is_premium=True
    )
    
    # Verify admin can access the premium lesson
    assert crud.lesson.can_access_lesson(db, user=admin, lesson_id=premium_lesson.id) is True
    
    # Test getting all lessons as admin (should return all lessons)
    all_lessons = crud.lesson.get_accessible_lessons(db, user=admin, course_id=course.id)
    assert any(lesson.id == premium_lesson.id for lesson in all_lessons)


def test_check_lesson_access_dependency(client: TestClient, db: Session) -> None:
    from fastapi import Depends, HTTPException
    from fastapi.testclient import TestClient
    from app.api.deps import get_db, get_current_active_user
    
    # Create test users
    free_user = create_test_user(
        db, 
        email="free_user3@example.com", 
        password="testpass123", 
        role_name="free"
    )
    
    premium_user = create_test_user(
        db, 
        email="premium_user2@example.com", 
        password="testpass123", 
        role_name="premium"
    )
    
    admin_user = create_test_user(
        db, 
        email="admin2@example.com", 
        password="adminpass123", 
        role_name="admin"
    )
    
    # Create a course with a premium lesson
    creator = create_test_user(
        db, 
        email="creator5@example.com", 
        password="creatorpass123", 
        role_name="free"
    )
    
    course = create_test_course(db, creator_id=creator.id, title="Dependency Test Course")
    premium_lesson = create_test_lesson(
        db, 
        course_id=course.id, 
        avatar_id=1,
        title="Dependency Test Premium Lesson", 
        is_premium=True
    )
    
    # Create a test endpoint that uses the check_lesson_access dependency
    @app.get("/test-lesson-access/{lesson_id}")
    async def test_lesson_access(
        lesson_id: int,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ):
        from app.api.deps import check_lesson_access
        await check_lesson_access(lesson_id, current_user, db)
        return {"message": "Access granted"}
    
    # Test with TestClient
    client = TestClient(app)
    
    # Get tokens for test users
    def get_token(email: str, password: str) -> str:
        response = client.post(
            "/api/v1/login/access-token",
            data={"username": email, "password": password}
        )
        return response.json()["access_token"]
    
    # Test free user access (should be denied)
    free_token = get_token("free_user3@example.com", "testpass123")
    response = client.get(
        f"/test-lesson-access/{premium_lesson.id}",
        headers={"Authorization": f"Bearer {free_token}"}
    )
    assert response.status_code == 403
    
    # Test premium user access (should be granted)
    premium_token = get_token("premium_user2@example.com", "testpass123")
    response = client.get(
        f"/test-lesson-access/{premium_lesson.id}",
        headers={"Authorization": f"Bearer {premium_token}"}
    )
    assert response.status_code == 200
    
    # Test admin access (should be granted)
    admin_token = get_token("admin2@example.com", "adminpass123")
    response = client.get(
        f"/test-lesson-access/{premium_lesson.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    
    # Test creator access (should be granted)
    creator_token = get_token("creator5@example.com", "creatorpass123")
    response = client.get(
        f"/test-lesson-access/{premium_lesson.id}",
        headers={"Authorization": f"Bearer {creator_token}"}
    )
    assert response.status_code == 200
    
    # Clean up the test endpoint
    app.router.routes = [r for r in app.router.routes if r.path != "/test-lesson-access/{lesson_id}"]
    
    # Create a course
    course = crud.course.create(
        db,
        obj_in={
            "title": "Test Course",
            "description": "Test Description",
            "difficulty_level": "A1",
            "instructor_id": creator.id,  # Using creator.id instead of user.id
        },
    )
    
    # Create lessons - some premium, some free
    lesson1 = crud.lesson.create(
        db,
        obj_in={
            "title": "Free Lesson 1",
            "content": "Content 1",
            "course_id": course.id,
            "order": 1,
            "is_premium": False,
            "avatar_id": 1
        },
    )
    
    lesson2 = crud.lesson.create(
        db,
        obj_in={
            "title": "Premium Lesson",
            "content": "Premium Content",
            "course_id": course.id,
            "order": 2,
            "is_premium": True,
            "avatar_id": 1
        },
    )
    
    lesson3 = crud.lesson.create(
        db,
        obj_in={
            "title": "Free Lesson 2",
            "content": "Content 2",
            "course_id": course.id,
            "order": 3,
            "is_premium": False,
            "avatar_id": 1
        },
    )
    
    # Test getting accessible lessons for free user
    accessible_lessons = crud.lesson.get_accessible_lessons(db, user=free_user)
    assert len(accessible_lessons) == 2  # Should only get the 2 free lessons
    assert {l.title for l in accessible_lessons} == {"Free Lesson 1", "Free Lesson 2"}
    
    # Test can_access_lesson for free user
    assert crud.lesson.can_access_lesson(db, user=free_user, lesson_id=lesson1.id) is True
    assert crud.lesson.can_access_lesson(db, user=free_user, lesson_id=lesson2.id) is False  # Premium lesson
    assert crud.lesson.can_access_lesson(db, user=free_user, lesson_id=lesson3.id) is True


def test_creator_access_to_own_lessons(client: TestClient, db: Session) -> None:
    # Create a course creator user
    creator_data = UserCreate(
        email="creator@example.com",
        password="creatorpass",
        full_name="Course Creator",
        username="creator",
        role="free",  # Free user but course creator
    )
    creator = crud.user.create(db, obj_in=creator_data)
    
    # Create a course
    course = create_test_course(db, creator_id=creator.id)
    # Create a premium lesson in the course
    premium_lesson = create_test_lesson(
        db, 
        course_id=course.id, 
        avatar_id=1,
        title="Creator's Premium Lesson", 
        is_premium=True
    )
    
    # Test creator can access their own premium lesson even as a free user
    assert crud.lesson.can_access_lesson(db, user=creator, lesson_id=premium_lesson.id) is True
    
    # Create another free user who is not the creator
    other_user_data = UserCreate(
        email="other@example.com",
        password="otherpass",
        full_name="Other User",
        username="otheruser",
        role="free",
    )
    other_user = crud.user.create(db, obj_in=other_user_data)
    
    # Test other free user cannot access the premium lesson
    assert crud.lesson.can_access_lesson(db, user=other_user, lesson_id=premium_lesson.id) is False


def test_check_lesson_access_dependency(client: TestClient, db: Session) -> None:
    from app.api.deps import check_lesson_access
    
    # Create a course creator user
    creator_data = UserCreate(
        email="creator@example.com",
        password="creatorpass",
        full_name="Course Creator",
        username="creator",
        role="free",
    )
    creator = crud.user.create(db, obj_in=creator_data)
    
    # Create a free user who is not the course creator
    free_user_data = UserCreate(
        email="free@example.com",
        password="freepass",
        full_name="Free User",
        username="freeuser",
        role="free",
    )
    free_user = crud.user.create(db, obj_in=free_user_data)
    
    # Create a course with the creator as the owner
    course = create_test_course(db, creator_id=creator.id)
    
    # Create a premium lesson in the course
    premium_lesson = create_test_lesson(
        db, 
        course_id=course.id, 
        avatar_id=1,
        title="Dependency Test Premium Lesson", 
        is_premium=True
    )
    
    # Test access with the dependency - should raise 403 for free user who is not the creator
    print(f"\nDebug - Testing access for free user to premium lesson")
    print(f"Free user roles: {free_user.roles}")
    print(f"Premium lesson is_premium: {premium_lesson.is_premium}")
    print(f"Is free user premium? {crud.user.is_premium(free_user)}")
    print(f"Is free user the course creator? {free_user.id == course.instructor_id}")
    
    # Debug the lesson access directly
    try:
        result = check_lesson_access(lesson_id=premium_lesson.id, db=db, current_user=free_user)
        print(f"Unexpected success! Got result: {result}")
    except HTTPException as e:
        print(f"Got HTTPException as expected: {e.status_code} - {e.detail}")
        if e.status_code == 403:
            return  # Test passes if we get a 403
        raise
    
    # If we get here, the test should fail
    pytest.fail("Expected HTTPException with status_code 403 not raised")
    
    # Create a premium user
    premium_user = crud.user.create(
        db,
        obj_in={
            "email": "premium@example.com",
            "password": "premiumpass",
            "full_name": "Premium User",
            "role": "premium",
        },
    )
    
    # Premium user should be able to access
    print("\nTesting premium user access to premium lesson...")
    print(f"Premium user role: {premium_user.roles}")
    print(f"Premium user is_premium: {crud.user.is_premium(premium_user)}")
    
    # Test premium user access
    try:
        lesson = check_lesson_access(lesson_id=premium_lesson.id, db=db, current_user=premium_user)
        print(f"Premium user successfully accessed premium lesson: {lesson.title}")
        assert lesson.id == premium_lesson.id
    except HTTPException as e:
        print(f"ERROR: Premium user could not access premium lesson: {e.status_code} - {e.detail}")
        raise
    
    # Also test with a different premium user who is not the course creator
    another_premium_user_data = UserCreate(
        email="another_premium@example.com",
        password="premiumpass2",
        full_name="Another Premium User",
        username="anotherpremium",
        role="premium",
    )
    another_premium_user = crud.user.create(db, obj_in=another_premium_user_data)
    
    print("\nTesting another premium user (not course creator) access to premium lesson...")
    try:
        lesson = check_lesson_access(lesson_id=premium_lesson.id, db=db, current_user=another_premium_user)
        print(f"Another premium user successfully accessed premium lesson: {lesson.title}")
        assert lesson.id == premium_lesson.id
    except HTTPException as e:
        print(f"ERROR: Another premium user could not access premium lesson: {e.status_code} - {e.detail}")
        raise

def setup_users(db: Session):
    # Clear existing users and roles to ensure a clean state
    db.query(User).delete()
    db.query(Role).delete()
    db.commit()

    # Create roles
    free_role = Role(id=1, name="free", description="Free User")
    premium_role = Role(id=2, name="premium", description="Premium User")
    creator_role = Role(id=4, name="creator", description="Course Creator")
    admin_role = Role(id=3, name="admin", description="Administrator")
    db.add_all([free_role, premium_role, creator_role, admin_role])
    db.commit()

    # Create users with roles
    creator = User(email="creator@example.com", hashed_password=get_password_hash("password"), full_name="Course Creator", role_id=creator_role.id)
    admin = User(email="admin@example.com", hashed_password=get_password_hash("password"), full_name="Admin User", is_superuser=True, role_id=admin_role.id)
    free_user = User(email="free@example.com", hashed_password=get_password_hash("password"), full_name="Free User", role_id=free_role.id)
    premium_user = User(email="premium@example.com", hashed_password=get_password_hash("password"), full_name="Premium User", role_id=premium_role.id)
    db.add_all([creator, admin, free_user, premium_user])
    db.commit()

    db.refresh(creator)
    db.refresh(admin)
    db.refresh(free_user)
    db.refresh(premium_user)

    return creator, admin, free_user, premium_user


@pytest.fixture(scope="function")
def setup_data(db: Session):
    creator, admin, free_user, premium_user = setup_users(db)
    yield creator, admin, free_user, premium_user
