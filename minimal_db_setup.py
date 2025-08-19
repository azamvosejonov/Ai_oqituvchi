"""
Minimal database setup script that creates the database schema directly.
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

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, ForeignKey, Boolean, Text, DateTime, JSON
from sqlalchemy.sql import func
import sqlite3

def create_tables():
    # Create a new SQLAlchemy engine and metadata
    engine = create_engine(os.environ["DATABASE_URL"])
    metadata = MetaData()
    
    # Drop all existing tables
    metadata.reflect(bind=engine)
    metadata.drop_all(bind=engine)
    
    # Create tables in the correct order
    with engine.begin() as conn:
        # Create roles table
        roles = Table(
            'roles', metadata,
            Column('id', Integer, primary_key=True, index=True),
            Column('name', String(50), unique=True, nullable=False),
            Column('description', String(255)),
            sqlite_autoincrement=True
        )
        
        # Create users table
        users = Table(
            'users', metadata,
            Column('id', Integer, primary_key=True, index=True),
            Column('email', String(255), unique=True, index=True, nullable=False),
            Column('hashed_password', String(255), nullable=False),
            Column('full_name', String(255)),
            Column('is_active', Boolean(), default=True),
            Column('is_superuser', Boolean(), default=False),
            sqlite_autoincrement=True
        )
        
        # Create user_role association table
        user_role = Table(
            'user_role', metadata,
            Column('user_id', Integer, ForeignKey('users.id')),
            Column('role_id', Integer, ForeignKey('roles.id'))
        )
        
        # Create courses table
        courses = Table(
            'courses', metadata,
            Column('id', Integer, primary_key=True, index=True),
            Column('title', String(255), nullable=False),
            Column('description', Text),
            Column('instructor_id', Integer, ForeignKey('users.id')),
            Column('is_published', Boolean, default=False),
            sqlite_autoincrement=True
        )
        
        # Create lessons table
        lessons = Table(
            'lessons', metadata,
            Column('id', Integer, primary_key=True, index=True),
            Column('title', String(255), nullable=False),
            Column('content', Text),
            Column('course_id', Integer, ForeignKey('courses.id')),
            Column('order', Integer, default=0),
            Column('is_published', Boolean, default=False),
            sqlite_autoincrement=True
        )
        
        # Create user_lesson_progress table
        user_lesson_progress = Table(
            'user_lesson_progress', metadata,
            Column('id', Integer, primary_key=True, index=True),
            Column('user_id', Integer, ForeignKey('users.id')),
            Column('lesson_id', Integer, ForeignKey('lessons.id')),
            Column('is_completed', Boolean, default=False),
            Column('progress', Integer, default=0),
            sqlite_autoincrement=True
        )
        
        # Create all tables
        metadata.create_all(engine)
        
        print("Database tables created successfully!")
        
        # Create initial data
        with engine.connect() as conn:
            # Insert roles
            conn.execute(roles.insert(), [
                {"name": "admin", "description": "Administrator role"},
                {"name": "user", "description": "Regular user role"}
            ])
            
            # Insert admin user (password: admin)
            admin_id = conn.execute(users.insert().returning(users.c.id), {
                "email": "admin@example.com",
                "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
                "full_name": "Admin User",
                "is_active": True,
                "is_superuser": True
            }).scalar()
            
            # Insert test user (password: test)
            test_user_id = conn.execute(users.insert().returning(users.c.id), {
                "email": "test@example.com",
                "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
                "full_name": "Test User",
                "is_active": True,
                "is_superuser": False
            }).scalar()
            
            # Assign admin role to admin user
            conn.execute(user_role.insert(), {"user_id": admin_id, "role_id": 1})
            
            # Assign user role to test user
            conn.execute(user_role.insert(), {"user_id": test_user_id, "role_id": 2})
            
            # Create a test course
            course_id = conn.execute(courses.insert().returning(courses.c.id), {
                "title": "Test Course",
                "description": "This is a test course",
                "instructor_id": admin_id,
                "is_published": True
            }).scalar()
            
            # Create a test lesson
            lesson_id = conn.execute(lessons.insert().returning(lessons.c.id), {
                "title": "Test Lesson",
                "content": "This is a test lesson",
                "course_id": course_id,
                "order": 1,
                "is_published": True
            }).scalar()
            
            # Create user lesson progress
            conn.execute(user_lesson_progress.insert(), {
                "user_id": test_user_id,
                "lesson_id": lesson_id,
                "is_completed": False,
                "progress": 0
            })
            
            print("Test data created successfully!")
            print("Admin user: admin@example.com / admin")
            print("Test user: test@example.com / test")

if __name__ == "__main__":
    print("Starting minimal database setup...")
    print(f"Database URL: {os.environ.get('DATABASE_URL')}")
    create_tables()
    print("Database setup completed!")
