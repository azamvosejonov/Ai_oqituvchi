"""
Simple database initialization script that creates only the essential tables.
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

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.db.session import SessionLocal, engine
from app.db.base_class import Base
from app.models import user, course, lesson, exercise, test, homework, subscription

def create_tables():
    print("Dropping all existing tables...")
    Base.metadata.drop_all(bind=engine)
    
    print("Creating essential tables...")
    
    # Create only the most basic tables first
    metadata = MetaData()
    metadata.reflect(bind=engine)
    
    # Create tables one by one in the correct order
    with engine.begin() as conn:
        # Create core tables first
        print("Creating core tables...")
        user.User.__table__.create(conn, checkfirst=True)
        user.Role.__table__.create(conn, checkfirst=True)
        user.user_role.create(conn, checkfirst=True)
        
        # Create course-related tables
        print("Creating course tables...")
        course.Course.__table__.create(conn, checkfirst=True)
        lesson.Lesson.__table__.create(conn, checkfirst=True)
        
        # Create other essential tables
        print("Creating other essential tables...")
        lesson.UserLessonProgress.__table__.create(conn, checkfirst=True)
        
    print("Tables created successfully!")

def create_test_data():
    print("Creating test data...")
    db = SessionLocal()
    
    try:
        # Create roles
        admin_role = user.Role(name="admin", description="Administrator role")
        user_role_obj = user.Role(name="user", description="Regular user role")
        db.add_all([admin_role, user_role_obj])
        db.commit()
        
        # Create users
        admin_user = user.User(
            email="admin@example.com",
            hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # password: admin
            full_name="Admin User",
            is_active=True,
            is_superuser=True
        )
        admin_user.roles.append(admin_role)
        
        test_user = user.User(
            email="test@example.com",
            hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # password: test
            full_name="Test User",
            is_active=True
        )
        test_user.roles.append(user_role_obj)
        
        db.add_all([admin_user, test_user])
        db.commit()
        
        # Create a test course
        course_obj = course.Course(
            title="Test Course",
            description="This is a test course",
            instructor_id=admin_user.id,
            is_published=True
        )
        db.add(course_obj)
        db.commit()
        
        # Create a test lesson
        lesson_obj = lesson.Lesson(
            title="Test Lesson",
            content="This is a test lesson",
            course_id=course_obj.id,
            order=1,
            is_published=True
        )
        db.add(lesson_obj)
        db.commit()
        
        # Create user lesson progress
        progress = lesson.UserLessonProgress(
            user_id=test_user.id,
            lesson_id=lesson_obj.id,
            is_completed=False,
            progress=0
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
    print("Starting simple database initialization...")
    print(f"Database URL: {os.environ.get('DATABASE_URL')}")
    
    # Create tables
    create_tables()
    
    # Create test data
    create_test_data()
    
    print("Database initialization completed!")
