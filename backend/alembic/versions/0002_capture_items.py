"""add capture items

Revision ID: 0002_capture_items
Revises: 0001_initial
Create Date: 2026-04-29 00:00:01
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0002_capture_items"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "capture_items",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("raw_text", sa.Text(), nullable=False),
        sa.Column("source", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("target_type", sa.String(length=80), nullable=True),
        sa.Column("target_id", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("converted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_capture_items_status"), "capture_items", ["status"], unique=False)
    op.create_index(op.f("ix_capture_items_created_at"), "capture_items", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_capture_items_created_at"), table_name="capture_items")
    op.drop_index(op.f("ix_capture_items_status"), table_name="capture_items")
    op.drop_table("capture_items")
