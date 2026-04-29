import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from auth import get_current_user
from database import get_db
from models.body import DailyMetric, Exercise, GolfRound, Workout
from models.capture import CaptureItem
from models.mind import Book, Decision, PhilosophyNote
from models.user import User
from schemas.body import DailyMetricCreate, GolfRoundCreate, WorkoutCreate
from schemas.capture import CaptureArchive, CaptureConvert, CaptureRead, CaptureStatus, CaptureTarget, CaptureCreate
from schemas.mind import BookCreate, DecisionCreate, PhilosophyNoteCreate

router = APIRouter(prefix="/captures", tags=["captures"], dependencies=[Depends(get_current_user)])


@router.get("", response_model=list[CaptureRead])
def list_captures(
    status_filter: CaptureStatus | None = Query("open", alias="status"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    statement = select(CaptureItem).order_by(CaptureItem.created_at.desc())
    if status_filter is not None:
        statement = statement.where(CaptureItem.status == status_filter)
    return db.scalars(statement).all()


@router.post("", response_model=CaptureRead, status_code=status.HTTP_201_CREATED)
def create_capture(payload: CaptureCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    item = CaptureItem(raw_text=payload.raw_text.strip(), source=payload.source)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.patch("/{capture_id}", response_model=CaptureRead)
def update_capture_status(
    capture_id: uuid.UUID,
    payload: CaptureArchive,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    item = db.get(CaptureItem, capture_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Capture not found")
    if item.status == "converted" and payload.status != "converted":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Converted captures cannot be reopened")
    item.status = payload.status
    db.commit()
    db.refresh(item)
    return item


def _validate(model, payload: dict):
    try:
        return model.model_validate(payload)
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.errors()) from None


def _create_target(target_type: CaptureTarget, payload: dict, db: Session):
    if target_type == "workout":
        validated = _validate(WorkoutCreate, payload)
        workout = Workout(date=validated.date, notes=validated.notes)
        workout.exercises = [Exercise(**exercise.model_dump()) for exercise in validated.exercises]
        return workout
    if target_type == "golf":
        return GolfRound(**_validate(GolfRoundCreate, payload).model_dump())
    if target_type == "metric":
        validated = _validate(DailyMetricCreate, payload)
        existing = db.scalar(select(DailyMetric).where(DailyMetric.date == validated.date))
        if existing is not None:
            for key, value in validated.model_dump().items():
                setattr(existing, key, value)
            return existing
        return DailyMetric(**validated.model_dump())
    if target_type == "book":
        return Book(**_validate(BookCreate, payload).model_dump())
    if target_type == "philosophy":
        return PhilosophyNote(**_validate(PhilosophyNoteCreate, payload).model_dump())
    if target_type == "decision":
        return Decision(**_validate(DecisionCreate, payload).model_dump())
    raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Unsupported target type")


@router.post("/{capture_id}/convert", response_model=CaptureRead)
def convert_capture(
    capture_id: uuid.UUID,
    payload: CaptureConvert,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    item = db.get(CaptureItem, capture_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Capture not found")
    if item.status == "converted":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Capture already converted")

    target = _create_target(payload.target_type, payload.payload, db)
    db.add(target)
    db.flush()

    item.status = "converted"
    item.target_type = payload.target_type
    item.target_id = target.id
    item.converted_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(item)
    return item
