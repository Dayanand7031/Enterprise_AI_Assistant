from datetime import datetime

from sqlalchemy import String, Text, DateTime, ForeignKey, func,Boolean,UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    role_id: Mapped[int | None] = mapped_column(
        ForeignKey("roles.id"),
        nullable=True,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )

    role = relationship(
        "Role",
        back_populates="users",
    )

    conversations = relationship(
        "Conversation",
        back_populates="user",
    )

    refresh_tokens = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    jira_connections = relationship(
        "JiraConnection",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    application_access = relationship(
        "UserApplicationAccess",
        back_populates="user",
        cascade="all, delete-orphan"
    )


class UserApplicationAccess(Base):
    __tablename__ = "user_application_access"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "application",
            name="uq_user_application_access",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    application: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user = relationship(
        "User",
        back_populates="application_access",
    )

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    token_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False
    )

    revoked: Mapped[bool] = mapped_column(
        default=False,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    user = relationship(
        "User",
        back_populates="refresh_tokens"
    )

class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id")
    )

    title: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
    )

    user = relationship(
        "User",
        back_populates="conversations"
    )

    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan"
    )


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("conversations.id")
    )

    role: Mapped[str] = mapped_column(
        String(50)
    )

    content: Mapped[str] = mapped_column(
        Text
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now()
    )

    conversation = relationship(
        "Conversation",
        back_populates="messages"
    )







from app.models.role_permission_model import (
    Role,
    Permission,
    RolePermission,
)