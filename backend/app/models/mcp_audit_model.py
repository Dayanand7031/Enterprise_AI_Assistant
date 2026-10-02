from datetime import datetime

from sqlalchemy import String, Text, DateTime, ForeignKey, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base

class MCPToolExecution(Base):
    __tablename__ = "mcp_tool_executions"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    tool_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )

    arguments: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True
    )

    success: Mapped[bool] = mapped_column(
        nullable=False,
        default=False
    )

    result: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    error: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    execution_time_ms: Mapped[float | None] = mapped_column(
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

    user = relationship("User")