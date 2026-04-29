import uuid

from sqlalchemy import Boolean, DateTime, Float, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Uuid

from database import Base


class MarketStock(Base):
    __tablename__ = "market_stocks"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    ticker: Mapped[str] = mapped_column(String(16), index=True, nullable=False)
    company_name: Mapped[str | None] = mapped_column(String(255))
    shares: Mapped[float | None] = mapped_column(Float)
    average_cost: Mapped[float | None] = mapped_column(Float)
    watchlist: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    thesis: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class MarketQuote(Base):
    __tablename__ = "market_quotes"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    ticker: Mapped[str] = mapped_column(String(16), index=True, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    change_amount: Mapped[float | None] = mapped_column(Float)
    change_percent: Mapped[float | None] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(12), nullable=False, default="USD")
    provider: Mapped[str] = mapped_column(String(80), nullable=False)
    fetched_at: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
