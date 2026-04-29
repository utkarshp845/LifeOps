import uuid

from sqlalchemy import Date, DateTime, Float, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Uuid

from database import Base


class WealthSnapshot(Base):
    __tablename__ = "wealth_snapshots"
    __table_args__ = (UniqueConstraint("date", name="uq_wealth_snapshots_date"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    date: Mapped[object] = mapped_column(Date, index=True, nullable=False)
    cash: Mapped[float | None] = mapped_column(Float)
    investments: Mapped[float | None] = mapped_column(Float)
    retirement: Mapped[float | None] = mapped_column(Float)
    crypto: Mapped[float | None] = mapped_column(Float)
    other_assets: Mapped[float | None] = mapped_column(Float)
    debt: Mapped[float | None] = mapped_column(Float)
    annual_expenses: Mapped[float | None] = mapped_column(Float)
    financial_freedom_number: Mapped[float | None] = mapped_column(Float)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
