import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MarketStockCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ticker: str
    company_name: str | None = None
    shares: float | None = None
    average_cost: float | None = None
    watchlist: bool = False
    thesis: str | None = None
    notes: str | None = None


class MarketStockPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ticker: str | None = None
    company_name: str | None = None
    shares: float | None = None
    average_cost: float | None = None
    watchlist: bool | None = None
    thesis: str | None = None
    notes: str | None = None


class MarketQuoteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    ticker: str
    price: float
    change_amount: float | None
    change_percent: float | None
    currency: str
    provider: str
    fetched_at: datetime


class MarketStockRead(MarketStockCreate):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    latest_quote: MarketQuoteRead | None = None
