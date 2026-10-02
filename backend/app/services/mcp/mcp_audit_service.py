import json
import time

from sqlalchemy.orm import Session

from app.models.mcp_audit_model import MCPToolExecution


def create_mcp_audit_log(
    db: Session,
    user_id: int,
    tool_name: str,
    arguments: dict | None,
    success: bool,
    result: str | None = None,
    error: str | None = None,
    execution_time_ms: float | None = None,
):
    audit = MCPToolExecution(
        user_id=user_id,
        tool_name=tool_name,
        arguments=arguments,
        success=success,
        result=result,
        error=error,
        execution_time_ms=execution_time_ms,
    )

    db.add(audit)
    db.commit()
    db.refresh(audit)

    return audit


def audit_mcp_execution(
    user_id: int,
    tool_name: str,
    arguments: dict | None,
    success: bool,
    result=None,
    error: str | None = None,
    execution_time_ms: float | None = None,
):
    """
    Create an MCP audit record using a fresh database session.

    This helper is intended to be called from MCP service functions
    after authorization or tool execution.
    """

    from app.db.database import SessionLocal

    db = SessionLocal()

    try:
        if result is not None and not isinstance(result, str):
            result = json.dumps(result, default=str)

        return create_mcp_audit_log(
            db=db,
            user_id=user_id,
            tool_name=tool_name,
            arguments=arguments,
            success=success,
            result=result,
            error=error,
            execution_time_ms=execution_time_ms,
        )

    finally:
        db.close()


def get_execution_time_ms(start_time: float) -> float:
    """
    Calculate elapsed execution time in milliseconds.
    """

    return (time.perf_counter() - start_time) * 1000


def audit_mcp_denial(
    user_id: int,
    tool_name: str,
    arguments: dict | None,
    error: str,
):
    return audit_mcp_execution(
        user_id=user_id,
        tool_name=tool_name,
        arguments=arguments,
        success=False,
        error=error,
    )