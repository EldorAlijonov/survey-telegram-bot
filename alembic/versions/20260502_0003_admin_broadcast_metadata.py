"""add admin and broadcast metadata

Revision ID: 20260502_0003
Revises: 20260501_0002
Create Date: 2026-05-02 00:00:00
"""

from typing import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260502_0003"
down_revision: str | None = "20260501_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("admins", sa.Column("username", sa.String(length=255), nullable=True))
    op.add_column("admins", sa.Column("added_by_username", sa.String(length=255), nullable=True))
    op.add_column("broadcasts", sa.Column("admin_username", sa.String(length=255), nullable=True))
    op.add_column("broadcasts", sa.Column("content_type", sa.String(length=64), nullable=True))
    op.add_column("broadcasts", sa.Column("preview", sa.Text(), nullable=True))
    op.add_column(
        "broadcasts",
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_column("broadcasts", "updated_at")
    op.drop_column("broadcasts", "preview")
    op.drop_column("broadcasts", "content_type")
    op.drop_column("broadcasts", "admin_username")
    op.drop_column("admins", "added_by_username")
    op.drop_column("admins", "username")
