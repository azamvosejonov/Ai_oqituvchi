import sys
from pathlib import Path

# Add project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

from app.db.session import SessionLocal
from app import crud, models
from app.schemas.user import UserRole

def assign_superadmin_role():
    db = SessionLocal()
    try:
        admin_email = "admin@example.com"
        user = crud.user.get_by_email(db, email=admin_email)

        if not user:
            print(f"Admin user with email {admin_email} not found.")
            return

        # Get or create the superadmin role
        superadmin_role = crud.role.get_or_create(db, name=UserRole.superadmin)

        # Check if the user already has the role
        if superadmin_role in user.roles:
            print(f"User {admin_email} already has the '{UserRole.superadmin.value}' role.")
            return

        # Assign the role
        user.roles.append(superadmin_role)
        db.add(user)
        db.commit()
        print(f"Successfully assigned '{UserRole.superadmin.value}' role to {admin_email}.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    assign_superadmin_role()
