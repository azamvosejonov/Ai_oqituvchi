"""
Direct database initialization script that creates tables with foreign key checks disabled.
"""
import os
import sys
from pathlib import Path

# Add project root to the Python path
ROOT_DIR = Path(__file__).resolve().parent
sys.path.append(str(ROOT_DIR))

# Set environment variables
os.environ["ENVIRONMENT"] = "dev"
os.environ["DATABASE_URL"] = "sqlite:///./test_oquv_app.db"

from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker
import sqlite3

# This function will be called for each database connection
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=OFF")
        cursor.close()

# Import models after setting up the event listener
from app.core.config import settings
from app.db.session import engine, SessionLocal
from app.db.base_class import Base
from app.models import *  # Import all models to ensure they are registered
from app.models.user import User, Role, user_role
from app.models.course import Course
from app.models.lesson import InteractiveLesson
from app.models.ai_avatar import AIAvatar

def create_tables():
    print("Dropping all existing tables...")
    Base.metadata.drop_all(bind=engine)
    
    print("Creating tables with foreign key checks disabled...")
    
    # Create all tables at once
    Base.metadata.create_all(bind=engine)
    
    # Re-enable foreign key checks
    with engine.connect() as conn:
        conn.execute(text("PRAGMA foreign_keys=ON"))
    
    print("Tables created successfully!")

def create_test_data():
    print("Creating test data...")
    db = SessionLocal()
    
    try:
        # Create roles
        admin_role = Role(name="admin", description="Administrator role")
        user_role_obj = Role(name="user", description="Regular user role")
        db.add_all([admin_role, user_role_obj])
        db.commit()
        
        # Create an AI Avatar for the lesson
        ai_avatar = AIAvatar(
            name="Test Avatar",
            avatar_url="http://example.com/avatar.png",
            voice_id="test_voice_id",
            language="en",
            is_active=True
        )
        db.add(ai_avatar)
        db.commit()
        
        # Create users
        admin_user = User(
            email="admin@example.com",
            username="admin",
            hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # password: admin
            full_name="Admin User",
            is_active=True,
            is_superuser=True
        )
        admin_user.roles.append(admin_role)
        
        test_user = User(
            email="test@example.com",
            username="testuser",
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
        lesson = InteractiveLesson(
            title="Test Lesson",
            content={"text": "This is a test lesson"},
            course_id=course.id,
            order=1,
            avatar_id=ai_avatar.id
        )
        db.add(lesson)
        db.commit()
        
        # Create user lesson progress
        progress = UserLessonProgress(
            user_id=test_user.id,
            lesson_id=lesson.id,
            score=0.0
        )
        db.add(progress)
        db.commit()
        
        print("Test data created successfully!")
        print(f"Admin user: admin@example.com / admin")
        print(f"Test user: test@example.com / test")
        
    except Exception as e:
        db.rollback()
        print(f"Error creating test data: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("Starting direct database initialization...")
    print(f"Database URL: {os.environ.get('DATABASE_URL')}")
    
    # Create tables
    create_tables()
    
    # Create test data
    create_test_data()
    
    print("Database initialization completed!")
