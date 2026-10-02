from datetime import datetime

from sqlalchemy import String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

class JiraTicket(Base):
    __tablename__ = "jira_tickets"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    priority: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="medium"
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="open"
    )

    created_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now()
    )

    creator = relationship(
        "User",
        foreign_keys=[created_by]
    )


from app.models.role_permission_model import (
    Role,
    Permission,
    RolePermission,
)