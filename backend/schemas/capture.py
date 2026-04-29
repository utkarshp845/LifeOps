import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

CaptureStatus = Literal["open", "archived", "converted"]
CaptureTarget = Literal["workout", "golf", "metric", "book", "philosophy", "decision"]


class CaptureCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    raw_text: str = Field(min_length=1)
    source: str = "quick"


class CaptureArchive(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["archived", "open"]


class CaptureConvert(BaseModel):
    model_config = ConfigDict(extra="forbid")

    target_type: CaptureTarget
    payload: dict[str, Any]


class CaptureRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    raw_text: str
    source: str
    status: CaptureStatus
    target_type: str | None
    target_id: uuid.UUID | None
    created_at: datetime
    converted_at: datetime | None
