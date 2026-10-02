from app.db.database import SessionLocal

# Register SQLAlchemy models
from app.models.auth_model import (
    User,
    UserApplicationAccess,
    RefreshToken,
    Conversation,
    Message,
)

from app.models.Jira_connection_model import JiraConnection
from app.models.jira_ticket_model import JiraTicket

from app.models.role_permission_model import (
    Role,
    Permission,
    RolePermission,
)

from app.models.mcp_audit_model import MCPToolExecution

from app.services.mcp.mcp_authorization import (
    authorize_mcp_tool,
    MCPAuthorizationError,
)


def test_tool(user_id: int, tool_name: str, db):

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        print(f"User {user_id} not found")
        return

    try:
        authorize_mcp_tool(
            db=db,
            user=user,
            tool_name=tool_name,
        )

        print(f"{tool_name:<30} → ALLOWED")

    except MCPAuthorizationError as exc:
        print(f"{tool_name:<30} → DENIED")
        print(f"    Reason: {exc}")


def main():

    db = SessionLocal()

    try:
        user_id = 5

        print(f"\nTesting MCP authorization for user {user_id}\n")

        test_tool(
            user_id,
            "create_ticket",
            db,
        )

        test_tool(
            user_id,
            "get_ticket",
            db,
        )

        test_tool(
            user_id,
            "jira_cloud_get_ticket",
            db,
        )

    finally:
        db.close()


if __name__ == "__main__":
    main()