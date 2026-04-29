import uuid
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

BuildStatus = Literal["idea", "building", "shipped", "maintained", "paused"]


class BuildProjectCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    description: str | None = None
    status: BuildStatus = "building"
    shipped_at: date | None = None
    url: str | None = None
    repository_url: str | None = None
    notes: str | None = None


class BuildProjectPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = None
    description: str | None = None
    status: BuildStatus | None = None
    shipped_at: date | None = None
    url: str | None = None
    repository_url: str | None = None
    notes: str | None = None


class BuildProjectRead(BuildProjectCreate):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
