import asyncio

from app.db.database import SessionLocal
from app.db.auth_model import User
from app.models.role_permission_model import RolePermission,Role, Permission
from app.services.mcp.mcp_service import create_enterprise_ticket


async def main():
    db = SessionLocal()

    try:
        user = (
            db.query(User)
            .filter(User.email == "employee@test.com")
            .first()
        )

        if user is None:
            print("User not found.")
            return

        print("\n========== USER ==========")
        print("ID:", user.id)
        print("Email:", user.email)
        print("Role:", user.role.name if user.role else None)

        print("\n========== MCP SERVICE TEST ==========")

        result = await create_enterprise_ticket(
            title="Login page not working",
            description="Users receive a 500 error when attempting to log in.",
            priority="high",
            user_id=user.id,   # <-- IMPORTANT
        )

        print("\nService result:")
        print(result)

    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())