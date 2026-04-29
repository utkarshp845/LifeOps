"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-04-29 00:00:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("username", sa.String(length=120), nullable=False),
        sa.Column("password_hash", sa.String(length=512), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)

    op.create_table(
        "workouts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_workouts_date"), "workouts", ["date"], unique=False)

    op.create_table(
        "golf_rounds",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("course", sa.String(length=255), nullable=True),
        sa.Column("score", sa.Integer(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_golf_rounds_date"), "golf_rounds", ["date"], unique=False)

    op.create_table(
        "daily_metrics",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("weight_lbs", sa.Float(), nullable=True),
        sa.Column("sleep_hours", sa.Float(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("date", name="uq_daily_metrics_date"),
    )
    op.create_index(op.f("ix_daily_metrics_date"), "daily_metrics", ["date"], unique=False)

    op.create_table(
        "books",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("author", sa.String(length=255), nullable=False),
        sa.Column("date_finished", sa.Date(), nullable=True),
        sa.Column("my_reaction", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "philosophy_notes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("thinker", sa.String(length=255), nullable=False),
        sa.Column("source", sa.String(length=255), nullable=True),
        sa.Column("disturbance", sa.Text(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_philosophy_notes_date"), "philosophy_notes", ["date"], unique=False)

    op.create_table(
        "decisions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("context", sa.Text(), nullable=False),
        sa.Column("reasoning", sa.Text(), nullable=False),
        sa.Column("expected_outcome", sa.Text(), nullable=False),
        sa.Column("actual_outcome", sa.Text(), nullable=True),
        sa.Column("reviewed_at", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_decisions_date"), "decisions", ["date"], unique=False)

    op.create_table(
        "exercises",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workout_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("sets", sa.Integer(), nullable=True),
        sa.Column("reps", sa.Integer(), nullable=True),
        sa.Column("weight_lbs", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(["workout_id"], ["workouts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_exercises_workout_id"), "exercises", ["workout_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_exercises_workout_id"), table_name="exercises")
    op.drop_table("exercises")
    op.drop_index(op.f("ix_decisions_date"), table_name="decisions")
    op.drop_table("decisions")
    op.drop_index(op.f("ix_philosophy_notes_date"), table_name="philosophy_notes")
    op.drop_table("philosophy_notes")
    op.drop_table("books")
    op.drop_index(op.f("ix_daily_metrics_date"), table_name="daily_metrics")
    op.drop_table("daily_metrics")
    op.drop_index(op.f("ix_golf_rounds_date"), table_name="golf_rounds")
    op.drop_table("golf_rounds")
    op.drop_index(op.f("ix_workouts_date"), table_name="workouts")
    op.drop_table("workouts")
    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_table("users")
