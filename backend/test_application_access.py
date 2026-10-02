from app.db.database import SessionLocal

# Register SQLAlchemy models
from app.models.auth_model import UserApplicationAccess
from app.models.Jira_connection_model import JiraConnection
from app.models.jira_ticket_model import JiraTicket
from app.models.role_permission_model import (
    Role,
    Permission,
    RolePermission,
)
from app.models.mcp_audit_model import MCPToolExecution

from app.services.access.application_access_service import (
    has_application_access,
)


def main():

    db = SessionLocal()

    try:
        user_id = 5

        print(
            "LOCAL_MCP:",
            has_application_access(
                db,
                user_id,
                "LOCAL_MCP",
            ),
        )

        print(
            "RAG:",
            has_application_access(
                db,
                user_id,
                "RAG",
            ),
        )

        print(
            "JIRA_CLOUD:",
            has_application_access(
                db,
                user_id,
                "JIRA_CLOUD",
            ),
        )

    finally:
        db.close()


if __name__ == "__main__":
    main()