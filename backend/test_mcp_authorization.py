from app.db.database import SessionLocal
from app.db.auth_model import User
from app.models.role_permission_model import Role,Permission,RolePermission

from app.services.mcp.mcp_authorization import (
    authorize_mcp_tool,
)


db = SessionLocal()

try:

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
    print("Email:", user.email)
    print(
        "Role:",
        user.role.name if user.role else None,
    )


    # --------------------------------------------------
    # CREATE TICKET
    # --------------------------------------------------

    print("\n========== CREATE TICKET ==========")

    try:

        authorize_mcp_tool(
            db=db,
            user=user,
            tool_name="create_ticket",
        )

        print("Authorization: ALLOWED")

    except Exception as exc:

        print("Authorization: DENIED")
        print("Error:", exc)


    # --------------------------------------------------
    # READ TICKET
    # --------------------------------------------------

    print("\n========== GET TICKET ==========")

    try:

        authorize_mcp_tool(
            db=db,
            user=user,
            tool_name="get_ticket",
        )

        print("Authorization: ALLOWED")

    except Exception as exc:

        print("Authorization: DENIED")
        print("Error:", exc)


    # --------------------------------------------------
    # UNKNOWN TOOL
    # --------------------------------------------------

    print("\n========== UNKNOWN TOOL ==========")

    try:

        authorize_mcp_tool(
            db=db,
            user=user,
            tool_name="delete_database",
        )

        print("Authorization: ALLOWED")

    except Exception as exc:

        print("Authorization: DENIED")
        print("Error:", exc)


finally:
    db.close()