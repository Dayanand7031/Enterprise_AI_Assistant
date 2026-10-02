import asyncio

from app.db.database import SessionLocal
from app.db.auth_model import User
from app.services.mcp.mcp_service import (
    get_enterprise_ticket,
)


async def main():

    db = SessionLocal()

    try:

        user = (
            db.query(User)
            .filter(
                User.email ==
                "dayanand.chauhan@tsfe365.com"
            )
            .first()
        )

        if user is None:
            print("User not found.")
            return

        print("\n========== USER ==========")
        print("ID:", user.id)
        print("Email:", user.email)
        print("Role:", user.role.name if user.role else None)

        print("\n========== GET TICKET ==========")

        result = await get_enterprise_ticket(
            ticket_id=5,
            user_id=user.id,
        )

        print("\nResult:")
        print(result)

    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())