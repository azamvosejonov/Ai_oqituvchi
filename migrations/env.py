import os
import sys
from logging.config import fileConfig
from pathlib import Path

# Add project root to the Python path
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

# Import SQLAlchemy and Alembic
from sqlalchemy import engine_from_config, pool, MetaData
from alembic import context

# Import your models and Base
from app.db.base_class import Base

# Import all models to ensure they are registered with SQLAlchemy
from app.models import *

# Get the metadata from the Base
target_metadata = Base.metadata

# This is the Alembic Config object, which provides access to the values within the .ini file.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,  # For SQLite compatibility
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # Get database URL from config
    configuration = config.get_section(config.config_ini_section, {})
    
    # Override with environment variable if set
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        configuration["sqlalchemy.url"] = db_url
    else:
        # Default to SQLite if no URL is provided
        configuration["sqlalchemy.url"] = "sqlite:///./oquv_app.db"
    
    # For SQLite, ensure we have the right connection string
    if "sqlite" in configuration.get("sqlalchemy.url", ""):
        configuration["sqlalchemy.url"] = configuration["sqlalchemy.url"].replace(
            "sqlite:///", "sqlite:///"
        )
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,  # For SQLite compatibility
            compare_type=True,
            include_schemas=True,
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
