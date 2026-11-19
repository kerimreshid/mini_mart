
from getpass import getpass

from app.database import SessionLocal, Base, engine
from app import models
from app.security import hash_password


# Create any missing database tables.
Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    username = input("Admin username: ").strip()

    if not username:
        print("Username cannot be empty.")
        raise SystemExit

    password = getpass("Admin password: ")

    if len(password) < 8:
        print("Password must contain at least 8 characters.")
        raise SystemExit

    confirm_password = getpass("Confirm admin password: ")

    if password != confirm_password:
        print("Passwords do not match.")
        raise SystemExit

    existing_user = db.query(models.User).filter(
        models.User.username == username
    ).first()

    if existing_user:
        print("This username already exists.")
    else:
        admin = models.User(
            username=username,
            hashed_password=hash_password(password),
            role="admin",
            is_active=True
        )

        db.add(admin)
        db.commit()

        print("Admin account created successfully!")

except Exception:
    db.rollback()
    raise

finally:
    db.close()