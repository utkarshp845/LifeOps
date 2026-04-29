import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from auth import get_current_user
from database import get_db
from models.body import DailyMetric, Exercise, GolfRound, Workout
from models.user import User
from schemas.body import (
    DailyMetricCreate,
    DailyMetricRead,
    ExerciseCreate,
    ExerciseRead,
    GolfRoundCreate,
    GolfRoundRead,
    WorkoutCreate,
    WorkoutRead,
)

router = APIRouter(tags=["body"], dependencies=[Depends(get_current_user)])


def _workout_query():
    return select(Workout).options(selectinload(Workout.exercises)).order_by(Workout.date.desc(), Workout.created_at.desc())


@router.get("/workouts", response_model=list[WorkoutRead])
def list_workouts(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.scalars(_workout_query()).all()


@router.post("/workouts", response_model=WorkoutRead, status_code=status.HTTP_201_CREATED)
def create_workout(payload: WorkoutCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    workout = Workout(date=payload.date, notes=payload.notes)
    workout.exercises = [Exercise(**exercise.model_dump()) for exercise in payload.exercises]
    db.add(workout)
    db.commit()
    db.refresh(workout)
    return workout


@router.get("/workouts/history", response_model=list[WorkoutRead])
def workout_history(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.scalars(_workout_query()).all()


@router.get("/workouts/{workout_id}", response_model=WorkoutRead)
def get_workout(workout_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    workout = db.scalar(
        select(Workout)
        .where(Workout.id == workout_id)
        .options(selectinload(Workout.exercises))
    )
    if workout is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout not found")
    return workout


@router.post("/workouts/{workout_id}/exercises", response_model=ExerciseRead, status_code=status.HTTP_201_CREATED)
def add_exercise(
    workout_id: uuid.UUID,
    payload: ExerciseCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    workout = db.get(Workout, workout_id)
    if workout is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout not found")
    exercise = Exercise(workout_id=workout_id, **payload.model_dump())
    db.add(exercise)
    db.commit()
    db.refresh(exercise)
    return exercise


@router.get("/golf", response_model=list[GolfRoundRead])
def list_golf_rounds(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.scalars(select(GolfRound).order_by(GolfRound.date.desc(), GolfRound.id.desc())).all()


@router.post("/golf", response_model=GolfRoundRead, status_code=status.HTTP_201_CREATED)
def create_golf_round(payload: GolfRoundCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    round_ = GolfRound(**payload.model_dump())
    db.add(round_)
    db.commit()
    db.refresh(round_)
    return round_


@router.get("/metrics", response_model=list[DailyMetricRead])
def list_metrics(
    limit: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    statement = select(DailyMetric).order_by(DailyMetric.date.desc()).limit(limit)
    return db.scalars(statement).all()


@router.post("/metrics", response_model=DailyMetricRead, status_code=status.HTTP_201_CREATED)
def create_or_update_metric(
    payload: DailyMetricCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    metric = db.scalar(select(DailyMetric).where(DailyMetric.date == payload.date))
    if metric is None:
        metric = DailyMetric(**payload.model_dump())
        db.add(metric)
    else:
        for key, value in payload.model_dump().items():
            setattr(metric, key, value)
    db.commit()
    db.refresh(metric)
    return metric
