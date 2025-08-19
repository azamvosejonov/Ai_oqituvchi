from sqlalchemy import create_engine, event, inspect
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Generator, Any
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.db.base_class import Base
from app.core.config import settings

def create_test_engine():
    """Create a test database engine"""
    TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL", "sqlite:///:memory:")
    
    if 'sqlite' in TEST_DATABASE_URL:
        engine = create_engine(
            TEST_DATABASE_URL,
            connect_args={"check_same_thread": False, "timeout": 30},
            poolclass=StaticPool,
        )
    else:
        engine = create_engine(
            TEST_DATABASE_URL,
            pool_pre_ping=True,
            pool_recycle=300,
        )
    
    return engine

def setup_test_db(engine):
    """Set up test database with all tables in correct order"""
    # Enable SQLite foreign keys and WAL mode for better performance
    if 'sqlite' in str(engine.url):
        @event.listens_for(engine, 'connect')
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous = NORMAL")
            cursor.close()
    
    # Drop all tables first to ensure clean state
    Base.metadata.drop_all(bind=engine)
    
    # Create all tables in the correct order
    # SQLAlchemy will handle the dependencies if we create all at once
    Base.metadata.create_all(bind=engine)
    
    # Verify all tables were created
    from sqlalchemy import inspect
    inspector = inspect(engine)
    all_tables = inspector.get_table_names()
    print(f"\n=== Created {len(all_tables)} tables in test database ===")
    for table in sorted(all_tables):
        print(f"- {table}")
    print()
    
    # Create UUID extension if using PostgreSQL
    if 'postgresql' in str(engine.url):
        with engine.connect() as conn:
            conn.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";")
            conn.commit()

def get_test_session(engine) -> sessionmaker:
    """Create a test database session factory"""
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    """Dependency for getting DB session"""
    from app.db.session import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
