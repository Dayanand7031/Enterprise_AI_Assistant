from app.db.database import SessionLocal
from app.db.auth_model import User
from app.services.auth.security import hash_password

db = SessionLocal()

try:
    user = (
        db.query(User)
        .filter(User.email == "employee@test.com")
        .first()
    )

    if not user:
        print("Employee user not found.")
    else:
        user.password_hash = hash_password("Employee@123")
        db.commit()

        print("Password reset successfully.")
        print("Email: employee@test.com")
        print("Password: Employee@123")
        print("Role:", user.role.name if user.role else None)

finally:
    db.close()