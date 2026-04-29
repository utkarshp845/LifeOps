import uuid
from datetime import date as date_type, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

GoalStatus = Literal["active", "paused", "achieved", "dropped"]
ReviewKind = Literal["daily", "weekly", "monthly"]


class LifeAreaCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    description: str | None = None
    position: int = 0


class LifeAreaPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = None
    description: str | None = None
    position: int | None = None


class LifeAreaRead(LifeAreaCreate):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime


class GoalCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    area_id: uuid.UUID | None = None
    title: str
    why: str | None = None
    status: GoalStatus = "active"
    target_date: date_type | None = None
    metric_name: str | None = None
    target_value: float | None = None
    current_value: float | None = None
    unit: str | None = None
    notes: str | None = None


class GoalPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    area_id: uuid.UUID | None = None
    title: str | None = None
    why: str | None = None
    status: GoalStatus | None = None
    target_date: date_type | None = None
    metric_name: str | None = None
    target_value: float | None = None
    current_value: float | None = None
    unit: str | None = None
    notes: str | None = None


class GoalRead(GoalCreate):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    area: LifeAreaRead | None = None
    progress_pct: float | None = None


class GoalsSummary(BaseModel):
    active_count: int
    achieved_count: int
    paused_count: int
    due_soon_count: int
    active_goals: list[GoalRead]


class ReviewCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: ReviewKind
    date: date_type
    goal_id: uuid.UUID | None = None
    wins: str | None = None
    friction: str | None = None
    lessons: str | None = None
    next_actions: str | None = None
    notes: str | None = None


class ReviewPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: ReviewKind | None = None
    date: date_type | None = None
    goal_id: uuid.UUID | None = None
    wins: str | None = None
    friction: str | None = None
    lessons: str | None = None
    next_actions: str | None = None
    notes: str | None = None


class ReviewRead(ReviewCreate):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    goal: GoalRead | None = None


class ReviewDue(BaseModel):
    daily_done: bool
    weekly_done: bool
    monthly_done: bool
    latest_daily: ReviewRead | None
    latest_weekly: ReviewRead | None
    latest_monthly: ReviewRead | None
