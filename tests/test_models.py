import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.db.base_class import Base
from app.models.user import User, Role
from app.crud import user as crud_user
from app.schemas import UserCreate

# Use a separate in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_models.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def db_session() -> Session:
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def test_create_user(db_session: Session):
    """Test creating a user and saving it to the database."""
    # Create a role first
    free_role = Role(name="free", description="Free Role")
    db_session.add(free_role)
    db_session.commit()
    db_session.refresh(free_role)

    # Create a new user instance
    new_user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="somehashedpassword"
    )
    new_user.roles.append(free_role)

    # Add to session and commit
    db_session.add(new_user)
    db_session.commit()
    db_session.refresh(new_user)

    # Query the user from the database
    user_in_db = db_session.query(User).filter(User.id == new_user.id).first()

    # Assertions
    assert user_in_db is not None
    assert user_in_db.username == "testuser"
    assert len(user_in_db.roles) == 1
    assert user_in_db.roles[0].name == "free"


def test_create_user_directly(db_session: Session):
    """Test creating a user directly in the database."""
    username = "testmodeluser"
    email = "testmodel@example.com"
    password = "testpassword"
    user_in = UserCreate(username=username, email=email, password=password)

    user = crud_user.create(db_session, obj_in=user_in)

    assert user is not None
    assert user.email == email
    assert user.username == username
    assert hasattr(user, "hashed_password")
    assert user.hashed_password != password


def test_get_user_by_email(db_session: Session):
    """Test retrieving a user by email."""
    username = "testgetuser"
    email = "getuser@example.com"
    password = "getpassword"
    user_in = UserCreate(username=username, email=email, password=password)
    crud_user.create(db_session, obj_in=user_in)

    user_from_db = crud_user.get_by_email(db_session, email=email)

    assert user_from_db is not None
    assert user_from_db.email == email
    assert user_from_db.username == username
