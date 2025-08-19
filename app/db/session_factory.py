from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
from typing import Generator

from app.core.config import settings

# Create engine with connection pooling
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.MAX_OVERFLOW,
    pool_timeout=30,  # seconds
    pool_recycle=1800,  # Recycle connections after 30 minutes
    pool_pre_ping=True,  # Enable the connection pool “pre-ping” feature
    echo=False,  # Set to True for SQL query logging
)

# Create session factory
SessionFactory = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

# Scoped session for thread safety
Session = scoped_session(SessionFactory)

@contextmanager
def get_db() -> Generator[scoped_session, None, None]:
    """
    Dependency for getting database session.
    Handles session lifecycle including rollback on exceptions.
    """
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def get_db_session() -> scoped_session:
    """
    Get a database session without context manager.
    Caller is responsible for closing the session.
    """
    return Session()

def close_db() -> None:
    """Close the database connection"""
    Session.remove()

# For backward compatibility
SessionLocal = Session
