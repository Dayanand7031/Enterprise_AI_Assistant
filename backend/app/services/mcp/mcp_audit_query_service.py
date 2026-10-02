from math import ceil

from sqlalchemy.orm import Session

from app.models.mcp_audit_model import MCPToolExecution


def get_mcp_audit_logs(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    user_id: int | None = None,
    tool_name: str | None = None,
    success: bool | None = None,
):
    query = db.query(MCPToolExecution)

    # -----------------------------------------
    # Filters
    # -----------------------------------------

    if user_id is not None:
        query = query.filter(
            MCPToolExecution.user_id == user_id
        )

    if tool_name is not None:
        query = query.filter(
            MCPToolExecution.tool_name == tool_name
        )

    if success is not None:
        query = query.filter(
            MCPToolExecution.success == success
        )

    # -----------------------------------------
    # Total count
    # -----------------------------------------

    total = query.count()

    # -----------------------------------------
    # Pagination
    # -----------------------------------------

    offset = (page - 1) * page_size

    logs = (
        query
        .order_by(
            MCPToolExecution.created_at.desc()
        )
        .offset(offset)
        .limit(page_size)
        .all()
    )

    total_pages = (
        ceil(total / page_size)
        if total > 0
        else 0
    )

    return {
        "items": logs,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }