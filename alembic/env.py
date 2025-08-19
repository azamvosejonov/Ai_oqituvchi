import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from the project root
project_dir = Path(__file__).resolve().parents[1]
dotenv_path = project_dir / ".env"

if not dotenv_path.exists():
    raise FileNotFoundError(f"CRITICAL: .env file not found at {dotenv_path}")

load_dotenv(dotenv_path=dotenv_path)

from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name:
    fileConfig(config.config_file_name)

def get_url():
    """Return the database URL.
    
    Prioritizes the URL from the config object (set programmatically for tests)
    over the one from environment variables.
    """
    # Check if the URL is set directly in the config (e.g., from conftest.py)
    url_from_config = config.get_main_option("sqlalchemy.url")
    if url_from_config:
        return url_from_config

    # Fallback to environment variable for production/development
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL environment variable not set.")
        # Fallback for local development if needed, but better to use .env
        db_user = os.getenv("POSTGRES_USER", "user")
        db_password = os.getenv("POSTGRES_PASSWORD", "password")
        db_server = os.getenv("POSTGRES_SERVER", "db")
        db_port = os.getenv("POSTGRES_PORT", "5432")
        db_name = os.getenv("POSTGRES_DB", "app")
        db_url = f"postgresql://{db_user}:{db_password}@{db_server}:{db_port}/{db_name}"
    
    print(f"Database URL from env: {db_url}")
    return db_url

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from app.db.base_class import Base # noqa
# Import all models here for Alembic's autogenerate to work correctly
from app.models.user import User # noqa
from app.models.course import Course # noqa
from app.models.lesson import LessonSession, LessonInteraction, InteractiveLesson # noqa
from app.models.test import Test, TestSection, TestQuestion, TestAttempt, TestAnswer # noqa
from app.core.config import settings # noqa

target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    # Use the determined database_url
    url = get_url()
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True, dialect_opts={"paramstyle": "named"}, render_as_batch=True
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    configuration = config.get_section(config.config_ini_section, {})
    # Use the determined database_url
    url = get_url()
    configuration["sqlalchemy.url"] = url
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, render_as_batch=True)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
