"""add subscriptions

Revision ID: 20260501_0002
Revises: 20260501_0001
Create Date: 2026-05-01 00:10:00
"""

from typing import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260501_0002"
down_revision: str | None = "20260501_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "subscriptions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("channel_username", sa.String(length=64), nullable=False),
        sa.Column("channel_url", sa.String(length=255), nullable=False),
        sa.Column("chat_id", sa.BigInteger(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_subscriptions_channel_username", "subscriptions", ["channel_username"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_subscriptions_channel_username", table_name="subscriptions")
    op.drop_table("subscriptions")
