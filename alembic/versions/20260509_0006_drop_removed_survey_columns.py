"""drop removed survey columns

Revision ID: 20260509_0006
Revises: 20260508_0005
Create Date: 2026-05-09 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "20260509_0006"
down_revision: str | None = "20260508_0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_column("surveys", "extra_learning_intent")
    op.drop_column("surveys", "school_condition")
    op.drop_column("users", "education_place")
    op.drop_column("users", "address")


def downgrade() -> None:
    op.add_column("users", sa.Column("address", sa.String(length=512), nullable=True))
    op.add_column("users", sa.Column("education_place", sa.String(length=255), nullable=True))
    op.add_column("surveys", sa.Column("school_condition", sa.String(length=64), nullable=True))
    op.add_column("surveys", sa.Column("extra_learning_intent", sa.String(length=64), nullable=True))
