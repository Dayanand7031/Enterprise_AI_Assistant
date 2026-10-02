from app.db.database import SessionLocal
from app.db.auth_model import User

from app.services.rbac.permission_service import has_permission
from app.models.role_permission_model import (
    Role,
    Permission,
    RolePermission,
)


db = SessionLocal()

try:

    # --------------------------------------------------
    # GET USER
    # --------------------------------------------------

    user = (
        db.query(User)
        .filter(
            User.email == "dayanand.chauhan@tsfe365.com"
        )
        .first()
    )

    if user is None:
        print("User not found.")
        raise SystemExit(1)

    print("\n========== USER ==========")
    print("ID:", user.id)
    print("Name:", user.name)
    print("Email:", user.email)

    if user.role:
        print("Role:", user.role.name)
    else:
        print("Role: None")


    # --------------------------------------------------
    # TEST PERMISSIONS
    # --------------------------------------------------

    permissions_to_test = [
        "jira:create",
        "jira:read",
        "jira:update",
        "jira:delete",
        "rag:query",
        "mcp:execute",
        "something:not_allowed",
    ]


    print("\n========== PERMISSION TEST ==========")

    for permission in permissions_to_test:

        result = has_permission(
            db=db,
            user=user,
            permission_name=permission,
        )

        print(
            f"{permission:<25} -> {result}"
        )


finally:
    db.close()