"""
Fixed database initialization script that creates tables in the correct order.
"""
import sys
import os
from pathlib import Path

from app.models.course import Enrollment

# Add project root to the Python path
ROOT_DIR = Path(__file__).resolve().parent
sys.path.append(str(ROOT_DIR))

# Set environment variables
os.environ["ENVIRONMENT"] = "dev"
os.environ["DATABASE_URL"] = "sqlite:///./test_oquv_app.db"  # Use a test database

import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

from app.core.config import settings
from app.db.session import engine, SessionLocal
from app.db.base_class import Base
from app.models import (
    User, Role, user_role, Course, Lesson,
    UserLessonCompletion, UserLessonProgress, Word, WordDefinition,
    WordExample, WordSynonym, WordAntonym, Homework, UserHomework,
    LessonSession, LessonInteraction, InteractiveLessonSession,
    InteractiveLessonInteraction, Test, TestSection, TestQuestion,
    TestAttempt, TestAnswer, ForumTopic, ForumPost, Notification,
    Certificate, Subscription, SubscriptionPlan, PaymentVerification,
    AIAvatar, InteractiveLesson, PronunciationPhrase, PronunciationSession,
    PronunciationAttempt, PronunciationAnalysisResult, UserPronunciationProfile
)

def create_tables():
    print("Creating database tables in the correct order...")
    
    # Drop all tables first
    print("Dropping existing tables...")
    Base.metadata.drop_all(bind=engine)
    
    # Create tables in the correct order
    print("Creating tables...")
    
    # Create tables without foreign key dependencies first
    Base.metadata.create_all(bind=engine, tables=[
        Role.__table__,
        User.__table__,
        user_role,
        Course.__table__,
        Word.__table__,
        WordDefinition.__table__,
        WordExample.__table__,
        WordSynonym.__table__,
        WordAntonym.__table__,
        SubscriptionPlan.__table__,
        Subscription.__table__,
        AIAvatar.__table__,
        InteractiveLesson.__table__,
        PronunciationPhrase.__table__,
        PronunciationSession.__table__,
        PronunciationAttempt.__table__,
        PronunciationAnalysisResult.__table__,
        UserPronunciationProfile.__table__,
        ForumTopic.__table__,
        ForumPost.__table__,
        Test.__table__,
        TestSection.__table__,
        TestQuestion.__table__,
        TestAttempt.__table__,
        TestAnswer.__table__,
        Certificate.__table__,
        PaymentVerification.__table__,
        Notification.__table__
    ])
    
    # Then create tables with foreign key dependencies
    Base.metadata.create_all(bind=engine, tables=[
        Enrollment.__table__,
        Lesson.__table__,
        UserLessonCompletion.__table__,
        UserLessonProgress.__table__,
        Homework.__table__,
        UserHomework.__table__,
        LessonSession.__table__,
        LessonInteraction.__table__,
        InteractiveLessonSession.__table__,
        InteractiveLessonInteraction.__table__
    ])
    
    print("All tables created successfully!")

def create_test_data():
    print("Creating test data...")
    db = SessionLocal()
    
    try:
        # Create test roles
        admin_role = Role(name="admin", description="Administrator role")
        user_role_obj = Role(name="user", description="Regular user role")
        
        db.add_all([admin_role, user_role_obj])
        db.commit()
        
        # Create test admin user
        admin_user = User(
            email="admin@example.com",
            hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # password: admin
            full_name="Admin User",
            is_active=True,
            is_superuser=True
        )
        admin_user.roles.append(admin_role)
        
        # Create test regular user
        test_user = User(
            email="test@example.com",
            hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # password: test
            full_name="Test User",
            is_active=True
        )
        test_user.roles.append(user_role_obj)
        
        db.add_all([admin_user, test_user])
        db.commit()
        
        # Create a test course
        course = Course(
            title="Test Course",
            description="This is a test course",
            instructor_id=admin_user.id,
            is_published=True
        )
        db.add(course)
        db.commit()
        
        # Create a test lesson
        lesson = Lesson(
            title="Test Lesson",
            content="This is a test lesson",
            course_id=course.id,
            order=1,
            is_published=True
        )
        db.add(lesson)
        db.commit()
        
        print("Test data created successfully!")
        print(f"Admin user: admin@example.com / admin")
        print(f"Test user: test@example.com / test")
        
    except Exception as e:
        db.rollback()
        print(f"Error creating test data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("Starting database initialization...")
    print(f"Database URL: {os.environ.get('DATABASE_URL')}")
    
    # Create tables
    create_tables()
    
    # Create test data
    create_test_data()
    
    print("Database initialization completed!")
