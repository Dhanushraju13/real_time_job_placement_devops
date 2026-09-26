import argparse
import sys
from app.database import SessionLocal, Base, engine
from app.models import User
from app.auth import hash_password

def create_admin_user(name: str, email: str, password: str):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == email.lower()).first()
        if existing:
            if existing.role != "ADMIN":
                print(f"Error: User with email '{email}' exists with role '{existing.role}'. Cannot overwrite.")
                sys.exit(1)
            else:
                existing.password_hash = hash_password(password)
                existing.name = name
                db.commit()
                print(f"Admin user '{email}' password updated successfully.")
                return

        admin = User(
            name=name,
            email=email.lower(),
            password_hash=hash_password(password),
            role="ADMIN"
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        print(f"Successfully created admin user: {email} (ID: {admin.id})")
    except Exception as e:
        print(f"Error creating admin: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create an Admin user for PlacementHub")
    parser.add_argument("--name", default="System Admin", help="Admin user full name")
    parser.add_argument("--email", required=True, help="Admin user email address")
    parser.add_argument("--password", required=True, help="Admin user password")

    args = parser.parse_args()
    create_admin_user(name=args.name, email=args.email, password=args.password)
