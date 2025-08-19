import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Prioritize DATABASE_URL from environment for testing
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", str(settings.DATABASE_URL))

# Ensure the database URL is a string
if not isinstance(SQLALCHEMY_DATABASE_URL, str):
    raise ValueError(f"DATABASE_URL must be a string, got {type(SQLALCHEMY_DATABASE_URL)}")

connect_args = {}
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    pool_pre_ping=True, 
    connect_args=connect_args
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
