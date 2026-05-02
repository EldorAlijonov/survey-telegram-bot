"""initial schema

Revision ID: 20260501_0001
Revises:
Create Date: 2026-05-01 00:00:00
"""

from typing import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260501_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    broadcast_status = sa.Enum("draft", "running", "finished", "cancelled", name="broadcast_status")

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("username", sa.String(length=255), nullable=True),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=32), nullable=True),
        sa.Column("address", sa.String(length=512), nullable=True),
        sa.Column("education_place", sa.String(length=255), nullable=True),
        sa.Column("is_registered", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("has_completed_survey", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_subscribed", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_users_telegram_id", "users", ["telegram_id"], unique=True)

    op.create_table(
        "admins",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("full_name", sa.String(), nullable=True),
        sa.Column("added_by", sa.BigInteger(), nullable=True),
        sa.Column("is_main", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_admins_telegram_id", "admins", ["telegram_id"], unique=True)

    op.create_table(
        "surveys",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("interest_level", sa.String(length=64), nullable=True),
        sa.Column("school_condition", sa.String(length=64), nullable=True),
        sa.Column("extra_learning_intent", sa.String(length=64), nullable=True),
        sa.Column("convenient_time", sa.String(length=64), nullable=True),
        sa.Column("interested_field", sa.String(length=64), nullable=True),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_surveys_user_id", "surveys", ["user_id"])

    op.create_table(
        "broadcasts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("admin_id", sa.Integer(), sa.ForeignKey("admins.id", ondelete="SET NULL"), nullable=True),
        sa.Column("source_chat_id", sa.BigInteger(), nullable=False),
        sa.Column("source_message_id", sa.Integer(), nullable=False),
        sa.Column("status", broadcast_status, nullable=False, server_default="draft"),
        sa.Column("total_users", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("sent_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("failed_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("broadcasts")
    op.drop_index("ix_surveys_user_id", table_name="surveys")
    op.drop_table("surveys")
    op.drop_index("ix_admins_telegram_id", table_name="admins")
    op.drop_table("admins")
    op.drop_index("ix_users_telegram_id", table_name="users")
    op.drop_table("users")
    sa.Enum(name="broadcast_status").drop(op.get_bind(), checkfirst=True)
