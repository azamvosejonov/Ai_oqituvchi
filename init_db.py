"""
Database initialization script.
This script creates all database tables based on SQLAlchemy models.
"""
import sys
import os
from pathlib import Path
import logging

# Add project root to the Python path
ROOT_DIR = Path(__file__).resolve().parent
sys.path.append(str(ROOT_DIR))

# Set environment variables
os.environ["ENVIRONMENT"] = "dev"
os.environ["DATABASE_URL"] = "sqlite:///./oquv_app.db"

# Import SQLAlchemy and models
from sqlalchemy import inspect, event, types, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.schema import CreateTable, MetaData, DropTable, ForeignKeyConstraint, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, configure_mappers, sessionmaker, relationship, backref

# Import the existing Base and engine
from app.core.config import settings
from app.db.session import engine
from app.db.base_class import Base as OriginalBase
from app.models.user import User, Role

logger = logging.getLogger(__name__)

# Create a custom JSON type that uses JSON for SQLite
class JSONType(types.TypeDecorator):
    impl = types.JSON
    
    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            from sqlalchemy.dialects.postgresql import JSONB
            return dialect.type_descriptor(JSONB())
        else:
            return dialect.type_descriptor(types.JSON())

# Import models in the correct order to avoid circular imports
# First, import base models without relationships
from app.models.course import Course
from app.models.word import Word
from app.models.forum import ForumTopic, ForumPost

# Then import models with relationships
from app.models.lesson import InteractiveLesson, LessonSession, LessonInteraction
from app.models.notification import Notification
from app.models.test import Test, TestSection, TestQuestion, TestAttempt, TestAnswer

# Import other models if they exist
try:
    from app.models.certificate import Certificate
except ImportError:
    print("Certificate model not found, skipping...")

try:
    from app.models.feedback import Feedback
except ImportError:
    print("Feedback model not found, skipping...")

try:
    from app.models.admin_log import AdminLog
except ImportError:
    print("AdminLog model not found, skipping...")

# Replace JSONB with our custom JSONType in all tables
for table in OriginalBase.metadata.tables.values():
    for column in table.columns:
        if hasattr(column.type, '__visit_name__') and column.type.__visit_name__ == 'JSONB':
            column.type = JSONType()

# Now configure all mappers
try:
    configure_mappers()
except Exception as e:
    print(f"Error configuring mappers: {e}")
    raise

def print_tables():
    """Print all tables in the database."""
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print("\nTables in the database:")
    for table in tables:
        print(f"- {table}")

def init_db():
    """Initialize the database by creating all tables."""
    print("Dropping all existing tables...")
    OriginalBase.metadata.drop_all(bind=engine)
    
    print("\nCreating database tables...")
    OriginalBase.metadata.create_all(bind=engine)
    print("\nDatabase tables created successfully!")
    
    # Print all tables in the database
    print_tables()
    
    # Verify tables by counting them
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"\nTotal tables created: {len(tables)}")

if __name__ == "__main__":
    print("Starting database initialization...")
    print(f"Database URL: {os.environ.get('DATABASE_URL')}")
    print(f"Current working directory: {os.getcwd()}")
    
    init_db()
