from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MCPAuditResponse(BaseModel):
    id: int
    user_id: int
    tool_name: str
    arguments: dict | None
    success: bool
    result: str | None
    error: str | None
    execution_time_ms: float | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MCPAuditListResponse(BaseModel):
    items: list[MCPAuditResponse]
    total: int
    page: int
    page_size: int
    total_pages: int