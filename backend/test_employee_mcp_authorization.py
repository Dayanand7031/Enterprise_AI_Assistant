from app.db.database import SessionLocal
from app.db.auth_model import User
from app.services.mcp.mcp_authorization import (
    authorize_mcp_tool,
    MCPAuthorizationError,
)


def main():

    db = SessionLocal()

    try:

        # ---------------------------------------------
        # Find employee user
        # ---------------------------------------------

        user = (
            db.query(User)
            .filter(User.email == "employee@test.com")
            .first()
        )

        if user is None:
            print("Employee user not found.")
            return

        print("\n========== USER ==========")
        print("ID:", user.id)
        print("Email:", user.email)
        print("Role:", user.role.name if user.role else None)

        # ---------------------------------------------
        # Test CREATE permission
        # ---------------------------------------------

        print("\n========== CREATE TICKET ==========")

        try:

            authorize_mcp_tool(
                db=db,
                user=user,
                tool_name="create_ticket",
            )

            print("Authorization: ALLOWED")

        except MCPAuthorizationError as exc:

            print("Authorization: DENIED")
            print("Error:", str(exc))

        # ---------------------------------------------
        # Test UPDATE permission
        # ---------------------------------------------

        print("\n========== UPDATE TICKET ==========")

        try:

            authorize_mcp_tool(
                db=db,
                user=user,
                tool_name="update_ticket",
            )

            print("Authorization: ALLOWED")

        except MCPAuthorizationError as exc:

            print("Authorization: DENIED")
            print("Error:", str(exc))

        print("\n========== DELETE TICKET ==========")

        try:

            authorize_mcp_tool(
                db=db,
                user=user,
                tool_name="delete_ticket",
            )

            print("Authorization: ALLOWED")

        except MCPAuthorizationError as exc:

            print("Authorization: DENIED")
            print("Error:", str(exc))

    finally:
        db.close()


if __name__ == "__main__":
    main()