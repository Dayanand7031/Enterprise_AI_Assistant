from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.auth_model import User
from app.schemas.mcp_audit import MCPAuditListResponse
from app.services.auth.dependencies import get_current_user
from app.services.rbac.dependencies import require_permission
from app.services.mcp.mcp_audit_query_service import (
    get_mcp_audit_logs,
)


router = APIRouter(
    prefix="/api/mcp/audit",
    tags=["MCP Audit"],
)


@router.get(
    "/",
    response_model=MCPAuditListResponse,
)
def get_audit_logs(
    page: int = Query(
        default=1,
        ge=1,
    ),
    page_size: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    user_id: int | None = Query(
        default=None
    ),
    tool_name: str | None = Query(
        default=None
    ),
    success: bool | None = Query(
        default=None
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("mcp:audit:read")
    ),
):
    return get_mcp_audit_logs(
        db=db,
        page=page,
        page_size=page_size,
        user_id=user_id,
        tool_name=tool_name,
        success=success,
    )