from app.core.security import get_password_hash
from app.db.session import SessionLocal
from app.models.user import User

def reset_admin_password():
    db = SessionLocal()
    try:
        # Get the admin user
        admin = db.query(User).filter(User.email == "admin@example.com").first()
        if not admin:
            print("Admin user not found")
            return
        
        # Set new password (you can change this to a secure password)
        new_password = "new_admin_password_123"
        admin.hashed_password = get_password_hash(new_password)
        db.commit()
        
        print(f"Password for {admin.email} has been reset to: {new_password}")
        print("Please change this password immediately after logging in.")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    reset_admin_password()
