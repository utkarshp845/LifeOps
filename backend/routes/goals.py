import uuid
from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from auth import get_current_user
from database import get_db
from models.goals import Goal, LifeArea, Review
from models.user import User
from schemas.goals import (
    GoalCreate,
    GoalPatch,
    GoalsSummary,
    LifeAreaCreate,
    LifeAreaPatch,
    LifeAreaRead,
    ReviewCreate,
    ReviewDue,
    ReviewKind,
    ReviewPatch,
    ReviewRead,
)

router = APIRouter(tags=["goals"], dependencies=[Depends(get_current_user)])


def _progress(goal: Goal) -> float | None:
    if goal.current_value is None or goal.target_value is None or goal.target_value == 0:
        return None
    return (goal.current_value / goal.target_value) * 100


def _goal_response(goal: Goal) -> dict:
    return {
        "id": goal.id,
        "area_id": goal.area_id,
        "title": goal.title,
        "why": goal.why,
        "status": goal.status,
        "target_date": goal.target_date,
        "metric_name": goal.metric_name,
        "target_value": goal.target_value,
        "current_value": goal.current_value,
        "unit": goal.unit,
        "notes": goal.notes,
        "created_at": goal.created_at,
        "updated_at": goal.updated_at,
        "area": goal.area,
        "progress_pct": _progress(goal),
    }


def _review_response(review: Review) -> dict:
    return {
        "id": review.id,
        "kind": review.kind,
        "date": review.date,
        "goal_id": review.goal_id,
        "wins": review.wins,
        "friction": review.friction,
        "lessons": review.lessons,
        "next_actions": review.next_actions,
        "notes": review.notes,
        "created_at": review.created_at,
        "goal": _goal_response(review.goal) if review.goal else None,
    }


def _ensure_area(db: Session, area_id: uuid.UUID | None) -> None:
    if area_id is not None and db.get(LifeArea, area_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Life area not found")


def _ensure_goal(db: Session, goal_id: uuid.UUID | None) -> None:
    if goal_id is not None and db.get(Goal, goal_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")


@router.get("/goals/areas", response_model=list[LifeAreaRead])
def list_areas(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.scalars(select(LifeArea).order_by(LifeArea.position.asc(), LifeArea.name.asc())).all()


@router.post("/goals/areas", response_model=LifeAreaRead, status_code=status.HTTP_201_CREATED)
def create_area(payload: LifeAreaCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    area = LifeArea(**payload.model_dump())
    db.add(area)
    db.commit()
    db.refresh(area)
    return area


@router.patch("/goals/areas/{area_id}", response_model=LifeAreaRead)
def patch_area(area_id: uuid.UUID, payload: LifeAreaPatch, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    area = db.get(LifeArea, area_id)
    if area is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Life area not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(area, key, value)
    db.commit()
    db.refresh(area)
    return area


@router.get("/goals/summary", response_model=GoalsSummary)
def goals_summary(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    today = date.today()
    soon = today + timedelta(days=30)
    active_goals = db.scalars(
        select(Goal)
        .where(Goal.status == "active")
        .options(joinedload(Goal.area))
        .order_by(Goal.target_date.asc().nulls_last(), Goal.created_at.desc())
    ).all()
    achieved_count = db.scalar(select(func.count()).select_from(Goal).where(Goal.status == "achieved")) or 0
    paused_count = db.scalar(select(func.count()).select_from(Goal).where(Goal.status == "paused")) or 0
    due_soon_count = db.scalar(
        select(func.count())
        .select_from(Goal)
        .where(Goal.status == "active", Goal.target_date.is_not(None), Goal.target_date <= soon)
    ) or 0
    return GoalsSummary(
        active_count=len(active_goals),
        achieved_count=achieved_count,
        paused_count=paused_count,
        due_soon_count=due_soon_count,
        active_goals=[_goal_response(goal) for goal in active_goals],
    )


@router.get("/goals")
def list_goals(status_filter: str | None = Query(None, alias="status"), db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    statement = select(Goal).options(joinedload(Goal.area)).order_by(Goal.created_at.desc())
    if status_filter:
        statement = statement.where(Goal.status == status_filter)
    return [_goal_response(goal) for goal in db.scalars(statement).all()]


@router.post("/goals", status_code=status.HTTP_201_CREATED)
def create_goal(payload: GoalCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    _ensure_area(db, payload.area_id)
    goal = Goal(**payload.model_dump())
    db.add(goal)
    db.commit()
    goal = db.scalar(select(Goal).where(Goal.id == goal.id).options(joinedload(Goal.area)))
    return _goal_response(goal)


@router.get("/goals/{goal_id}")
def get_goal(goal_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    goal = db.scalar(select(Goal).where(Goal.id == goal_id).options(joinedload(Goal.area)))
    if goal is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    return _goal_response(goal)


@router.patch("/goals/{goal_id}")
def patch_goal(goal_id: uuid.UUID, payload: GoalPatch, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    goal = db.get(Goal, goal_id)
    if goal is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    values = payload.model_dump(exclude_unset=True)
    _ensure_area(db, values.get("area_id"))
    for key, value in values.items():
        setattr(goal, key, value)
    db.commit()
    goal = db.scalar(select(Goal).where(Goal.id == goal_id).options(joinedload(Goal.area)))
    return _goal_response(goal)


@router.get("/reviews", response_model=list[ReviewRead])
def list_reviews(kind: ReviewKind | None = None, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    statement = select(Review).options(joinedload(Review.goal).joinedload(Goal.area)).order_by(Review.date.desc(), Review.created_at.desc())
    if kind:
        statement = statement.where(Review.kind == kind)
    return [_review_response(review) for review in db.scalars(statement).all()]


@router.post("/reviews", response_model=ReviewRead, status_code=status.HTTP_201_CREATED)
def create_review(payload: ReviewCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    _ensure_goal(db, payload.goal_id)
    review = Review(**payload.model_dump())
    db.add(review)
    db.commit()
    review = db.scalar(select(Review).where(Review.id == review.id).options(joinedload(Review.goal).joinedload(Goal.area)))
    return _review_response(review)


@router.get("/reviews/due", response_model=ReviewDue)
def reviews_due(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)

    latest_daily = db.scalar(select(Review).where(Review.kind == "daily").options(joinedload(Review.goal).joinedload(Goal.area)).order_by(Review.date.desc()).limit(1))
    latest_weekly = db.scalar(select(Review).where(Review.kind == "weekly").options(joinedload(Review.goal).joinedload(Goal.area)).order_by(Review.date.desc()).limit(1))
    latest_monthly = db.scalar(select(Review).where(Review.kind == "monthly").options(joinedload(Review.goal).joinedload(Goal.area)).order_by(Review.date.desc()).limit(1))

    return ReviewDue(
        daily_done=bool(latest_daily and latest_daily.date >= today),
        weekly_done=bool(latest_weekly and latest_weekly.date >= week_start),
        monthly_done=bool(latest_monthly and latest_monthly.date >= month_start),
        latest_daily=_review_response(latest_daily) if latest_daily else None,
        latest_weekly=_review_response(latest_weekly) if latest_weekly else None,
        latest_monthly=_review_response(latest_monthly) if latest_monthly else None,
    )


@router.get("/reviews/{review_id}", response_model=ReviewRead)
def get_review(review_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    review = db.scalar(select(Review).where(Review.id == review_id).options(joinedload(Review.goal).joinedload(Goal.area)))
    if review is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    return _review_response(review)


@router.patch("/reviews/{review_id}", response_model=ReviewRead)
def patch_review(review_id: uuid.UUID, payload: ReviewPatch, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    review = db.get(Review, review_id)
    if review is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    values = payload.model_dump(exclude_unset=True)
    _ensure_goal(db, values.get("goal_id"))
    for key, value in values.items():
        setattr(review, key, value)
    db.commit()
    review = db.scalar(select(Review).where(Review.id == review_id).options(joinedload(Review.goal).joinedload(Goal.area)))
    return _review_response(review)
