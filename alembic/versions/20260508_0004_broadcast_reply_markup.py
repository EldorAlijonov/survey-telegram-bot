"""add broadcast reply markup

Revision ID: 20260508_0004
Revises: 20260502_0003
Create Date: 2026-05-08 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "20260508_0004"
down_revision: str | None = "20260502_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("broadcasts", sa.Column("reply_markup", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("broadcasts", "reply_markup")
