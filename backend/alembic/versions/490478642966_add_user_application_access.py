"""add user application access

Revision ID: 490478642966
Revises: c3fc4297991c
Create Date: 2026-09-30 10:35:34.082680

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "490478642966"
down_revision: Union[str, Sequence[str], None] = "c3fc4297991c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user_application_access",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("application", sa.String(length=50), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            "application",
            name="uq_user_application_access",
        ),
    )

    op.create_index(
        "ix_user_application_access_id",
        "user_application_access",
        ["id"],
        unique=False,
    )

    op.create_index(
        "ix_user_application_access_user_id",
        "user_application_access",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_user_application_access_user_id",
        table_name="user_application_access",
    )

    op.drop_index(
        "ix_user_application_access_id",
        table_name="user_application_access",
    )

    op.drop_table("user_application_access")