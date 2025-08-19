"""
Script to create a test user in the database using raw SQL.
This bypasses SQLAlchemy models to avoid circular import issues.
"""
import sys
import os
from pathlib import Path
import sqlite3
from datetime import datetime, timezone

# Database file path
DB_PATH = "../oquv_app.db"

def create_test_user():
    """Create a test user directly in the SQLite database."""
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if user already exists
        cursor.execute("SELECT id, email FROM users WHERE email = ?", ("test@example.com",))
        existing_user = cursor.fetchone()
        
        if existing_user:
            print(f"Test user already exists with ID: {existing_user[0]}")
            print(f"Email: {existing_user[1]}")
            return
        
        # Create test user
        test_user = {
            'username': 'testuser',
            'email': 'test@example.com',
            'full_name': 'Test User',
            'hashed_password': 'hashed_password_placeholder',  # We'll update this after hashing
            'is_active': 1,  # True
            'is_superuser': 0,  # False
            'role': 'free',  # Must be one of: free, premium, admin, superadmin
            'current_level': 'A1',
            'created_at': datetime.now(timezone.utc).isoformat(),
            'last_login': None
        }
        
        # Insert the user
        cursor.execute("""
            INSERT INTO users (
                username, email, full_name, hashed_password, 
                is_active, is_superuser, role, current_level, 
                created_at, last_login
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            test_user['username'],
            test_user['email'],
            test_user['full_name'],
            test_user['hashed_password'],
            test_user['is_active'],
            test_user['is_superuser'],
            test_user['role'],
            test_user['current_level'],
            test_user['created_at'],
            test_user['last_login']
        ))
        
        # Get the user ID
        user_id = cursor.lastrowid
        
        # Now update with a properly hashed password
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        hashed_password = pwd_context.hash("testpassword")
        
        cursor.execute(
            "UPDATE users SET hashed_password = ? WHERE id = ?",
            (hashed_password, user_id)
        )
        
        # Commit the transaction
        conn.commit()
        
        print(f"Test user created successfully with ID: {user_id}")
        print(f"Email: {test_user['email']}")
        print("Password: testpassword")
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("Creating test user using direct SQL...")
    create_test_user()
