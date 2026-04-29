"""add goals and reviews

Revision ID: 0004_goals_reviews
Revises: 0003_lifeops_expansion
Create Date: 2026-04-29 00:00:03
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0004_goals_reviews"
down_revision: Union[str, None] = "0003_lifeops_expansion"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "life_areas",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("position", sa.Integer(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "goals",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("area_id", sa.Uuid(), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("why", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=40), server_default="active", nullable=False),
        sa.Column("target_date", sa.Date(), nullable=True),
        sa.Column("metric_name", sa.String(length=120), nullable=True),
        sa.Column("target_value", sa.Float(), nullable=True),
        sa.Column("current_value", sa.Float(), nullable=True),
        sa.Column("unit", sa.String(length=40), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["area_id"], ["life_areas.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_goals_area_id"), "goals", ["area_id"], unique=False)
    op.create_table(
        "reviews",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("kind", sa.String(length=40), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("goal_id", sa.Uuid(), nullable=True),
        sa.Column("wins", sa.Text(), nullable=True),
        sa.Column("friction", sa.Text(), nullable=True),
        sa.Column("lessons", sa.Text(), nullable=True),
        sa.Column("next_actions", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["goal_id"], ["goals.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_reviews_date"), "reviews", ["date"], unique=False)
    op.create_index(op.f("ix_reviews_goal_id"), "reviews", ["goal_id"], unique=False)
    op.create_index(op.f("ix_reviews_kind"), "reviews", ["kind"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_reviews_kind"), table_name="reviews")
    op.drop_index(op.f("ix_reviews_goal_id"), table_name="reviews")
    op.drop_index(op.f("ix_reviews_date"), table_name="reviews")
    op.drop_table("reviews")
    op.drop_index(op.f("ix_goals_area_id"), table_name="goals")
    op.drop_table("goals")
    op.drop_table("life_areas")
