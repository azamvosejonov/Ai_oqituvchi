#!/usr/bin/env python3
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from app.core.config import settings

def setup_database():
    """Create database if it doesn't exist"""
    # Extract database name from DATABASE_URL
    db_url = settings.DATABASE_URL
    if not db_url:
        print("Error: DATABASE_URL is not set in .env file")
        sys.exit(1)
    
    # Create database if it doesn't exist
    engine = create_engine(db_url.rsplit('/', 1)[0] + '/postgres')
    conn = engine.connect()
    conn.execute("COMMIT")
    
    db_name = db_url.split('/')[-1].split('?')[0]
    if not database_exists(db_url):
        print(f"Creating database: {db_name}")
        create_database(db_url)
        print("Database created successfully")
    else:
        print(f"Database {db_name} already exists")
    
    conn.close()
    engine.dispose()

if __name__ == "__main__":
    setup_database()
