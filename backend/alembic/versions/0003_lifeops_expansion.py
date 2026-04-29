"""add markets build and wealth modules

Revision ID: 0003_lifeops_expansion
Revises: 0002_capture_items
Create Date: 2026-04-29 00:00:02
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0003_lifeops_expansion"
down_revision: Union[str, None] = "0002_capture_items"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "market_stocks",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("ticker", sa.String(length=16), nullable=False),
        sa.Column("company_name", sa.String(length=255), nullable=True),
        sa.Column("shares", sa.Float(), nullable=True),
        sa.Column("average_cost", sa.Float(), nullable=True),
        sa.Column("watchlist", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("thesis", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_market_stocks_ticker"), "market_stocks", ["ticker"], unique=False)

    op.create_table(
        "market_quotes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("ticker", sa.String(length=16), nullable=False),
        sa.Column("price", sa.Float(), nullable=False),
        sa.Column("change_amount", sa.Float(), nullable=True),
        sa.Column("change_percent", sa.Float(), nullable=True),
        sa.Column("currency", sa.String(length=12), nullable=False),
        sa.Column("provider", sa.String(length=80), nullable=False),
        sa.Column("fetched_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_market_quotes_ticker"), "market_quotes", ["ticker"], unique=False)

    op.create_table(
        "build_projects",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=80), server_default="building", nullable=False),
        sa.Column("shipped_at", sa.Date(), nullable=True),
        sa.Column("url", sa.String(length=500), nullable=True),
        sa.Column("repository_url", sa.String(length=500), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "wealth_snapshots",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("cash", sa.Float(), nullable=True),
        sa.Column("investments", sa.Float(), nullable=True),
        sa.Column("retirement", sa.Float(), nullable=True),
        sa.Column("crypto", sa.Float(), nullable=True),
        sa.Column("other_assets", sa.Float(), nullable=True),
        sa.Column("debt", sa.Float(), nullable=True),
        sa.Column("annual_expenses", sa.Float(), nullable=True),
        sa.Column("financial_freedom_number", sa.Float(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("date", name="uq_wealth_snapshots_date"),
    )
    op.create_index(op.f("ix_wealth_snapshots_date"), "wealth_snapshots", ["date"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_wealth_snapshots_date"), table_name="wealth_snapshots")
    op.drop_table("wealth_snapshots")
    op.drop_table("build_projects")
    op.drop_index(op.f("ix_market_quotes_ticker"), table_name="market_quotes")
    op.drop_table("market_quotes")
    op.drop_index(op.f("ix_market_stocks_ticker"), table_name="market_stocks")
    op.drop_table("market_stocks")
