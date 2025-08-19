from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.user import User, Role


def assign_teacher_role(user_id: int):
    engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            print(f"User with ID {user_id} not found.")
            return

        teacher_role = db.query(Role).filter(Role.name == "teacher").first()
        if not teacher_role:
            print("Role 'teacher' not found. Creating it.")
            teacher_role = Role(name="teacher", description="A teacher user")
            db.add(teacher_role)
            db.commit()
            db.refresh(teacher_role)

        if teacher_role not in user.roles:
            user.roles.append(teacher_role)
            db.commit()
            print(f"Successfully assigned 'teacher' role to user {user.email}.")
        else:
            print(f"User {user.email} already has the 'teacher' role.")

    finally:
        db.close()

if __name__ == "__main__":
    assign_teacher_role(1)
