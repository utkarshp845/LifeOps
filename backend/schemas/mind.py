import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class BookCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    author: str
    date_finished: date | None = None
    my_reaction: str | None = None


class BookPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    date_finished: date | None = None
    my_reaction: str | None = None


class BookRead(BookCreate):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime


class PhilosophyNoteCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    thinker: str
    source: str | None = None
    disturbance: str
    date: date


class PhilosophyNoteRead(PhilosophyNoteCreate):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime


class DecisionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    date: date
    title: str
    context: str
    reasoning: str
    expected_outcome: str
    actual_outcome: str | None = None
    reviewed_at: date | None = None


class DecisionPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    actual_outcome: str | None = None
    reviewed_at: date | None = None


class DecisionRead(DecisionCreate):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
