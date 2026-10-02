from sqlalchemy.orm import Session

from app.models.auth_model import User

from app.services.rbac.permission_service import (
    has_permission,
)

from app.services.mcp.tool_permissions import (
    MCP_TOOL_PERMISSIONS,
    MCP_TOOL_APPLICATIONS
)


from app.services.access.application_access_service import (
    has_application_access,
)

class MCPAuthorizationError(Exception):
    """Raised when a user is not authorized to execute an MCP tool."""


def authorize_mcp_tool(
    db: Session,
    user: User,
    tool_name: str,
) -> None:

    # ---------------------------------------------------------
    # 1. Identify required permission
    # ---------------------------------------------------------
    permission = MCP_TOOL_PERMISSIONS.get(tool_name)

    if permission is None:
        raise MCPAuthorizationError(
            f"MCP tool is not authorized: {tool_name}"
        )


    # ---------------------------------------------------------
    # 2. Check application mapping
    # ---------------------------------------------------------

    application = MCP_TOOL_APPLICATIONS.get(tool_name)

    if application is None:
        raise MCPAuthorizationError(
            f"MCP application is not configured: {tool_name}"
        )


    print("========== AUTHORIZATION DEBUG ==========")
    print("user.id:", user.id)
    print("tool_name:", tool_name)
    print("permission:", permission)
    print("application:", application)

    application_access = has_application_access(
        db=db,
        user_id=user.id,
        application=application,
    )

    print("application_access:", application_access)
    print("=========================================")

    if not application_access:
        raise MCPAuthorizationError(
            f"Access denied for application: {application}"
        )



    # ---------------------------------------------------------
    # 3. Check application access
    # ---------------------------------------------------------

    if not has_application_access(
        db=db,
        user_id=user.id,
        application=application,
    ):
        raise MCPAuthorizationError(
            f"Access denied for application: {application}"
        )

    # ---------------------------------------------------------
    # 4. Check existing RBAC permission
    # ---------------------------------------------------------
    allowed = has_permission(
        db=db,
        user=user,
        permission_name=permission,
    )

    if not allowed:
        raise MCPAuthorizationError(
            f"Permission required: {permission}"
        )