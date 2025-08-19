from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from .base_class import Base
from ..core.config import settings

# Create database engine
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize the database by creating all tables.
    
    This function imports all models through the model registry to ensure
    proper table creation order and avoid circular imports.
    """
    # Import the model registry to ensure all models are registered
    from app.models.model_registry import ensure_models_imported
    
    # This will ensure all models are imported and registered with SQLAlchemy
    ensure_models_imported()
    
    # Create all tables
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get a database session.
    
    Yields:
        Session: A database session.
        
    Example:
        with get_db() as db:
            result = db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

# Re-export Base for use in models
__all__ = ['Base', 'SessionLocal', 'get_db', 'init_db']
