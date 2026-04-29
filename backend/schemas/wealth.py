import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class WealthSnapshotCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    date: date
    cash: float | None = None
    investments: float | None = None
    retirement: float | None = None
    crypto: float | None = None
    other_assets: float | None = None
    debt: float | None = None
    annual_expenses: float | None = None
    financial_freedom_number: float | None = None
    notes: str | None = None


class WealthSnapshotRead(WealthSnapshotCreate):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    net_worth: float
    progress_pct: float | None
    runway_years: float | None


class WealthSummary(BaseModel):
    latest: WealthSnapshotRead | None
    net_worth: float
    financial_freedom_number: float | None
    progress_pct: float | None
    runway_years: float | None
