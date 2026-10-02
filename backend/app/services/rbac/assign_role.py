from app.db.database import SessionLocal
from app.db.auth_model import User
from app.models.role_permission_model import Role


db = SessionLocal()

try:
    user = (
        db.query(User)
        .filter(User.email == "dayanand.chauhan@tsfe365.com")
        .first()
    )

    if user is None:
        print("User not found.")

    else:
        role = (
            db.query(Role)
            .filter(Role.name == "admin")
            .first()
        )

        if role is None:
            print("Admin role not found.")

        else:
            user.role_id = role.id
            db.commit()
            db.refresh(user)

            print("Role assigned successfully.")
            print("User:", user.email)
            print("Role:", role.name)

finally:
    db.close()