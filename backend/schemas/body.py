import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class ExerciseBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    sets: int | None = None
    reps: int | None = None
    weight_lbs: float | None = None


class ExerciseCreate(ExerciseBase):
    pass


class ExerciseRead(ExerciseBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    workout_id: uuid.UUID


class WorkoutCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    date: date
    notes: str | None = None
    exercises: list[ExerciseCreate] = []


class WorkoutRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    date: date
    notes: str | None
    created_at: datetime
    exercises: list[ExerciseRead] = []


class GolfRoundCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    date: date
    course: str | None = None
    score: int | None = None
    notes: str | None = None


class GolfRoundRead(GolfRoundCreate):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID


class DailyMetricCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    date: date
    weight_lbs: float | None = None
    sleep_hours: float | None = None
    notes: str | None = None


class DailyMetricRead(DailyMetricCreate):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
