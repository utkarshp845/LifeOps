from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from auth import get_current_user
from database import get_db
from models.user import User
from models.wealth import WealthSnapshot
from schemas.wealth import WealthSnapshotCreate, WealthSnapshotRead, WealthSummary

router = APIRouter(prefix="/wealth", tags=["wealth"], dependencies=[Depends(get_current_user)])


def _value(value: float | None) -> float:
    return 0.0 if value is None else float(value)


def _net_worth(snapshot: WealthSnapshot) -> float:
    return (
        _value(snapshot.cash)
        + _value(snapshot.investments)
        + _value(snapshot.retirement)
        + _value(snapshot.crypto)
        + _value(snapshot.other_assets)
        - _value(snapshot.debt)
    )


def _snapshot_response(snapshot: WealthSnapshot) -> dict:
    net_worth = _net_worth(snapshot)
    progress_pct = None
    if snapshot.financial_freedom_number and snapshot.financial_freedom_number > 0:
        progress_pct = (net_worth / snapshot.financial_freedom_number) * 100
    runway_years = None
    if snapshot.annual_expenses and snapshot.annual_expenses > 0:
        runway_years = net_worth / snapshot.annual_expenses
    return {
        "id": snapshot.id,
        "date": snapshot.date,
        "cash": snapshot.cash,
        "investments": snapshot.investments,
        "retirement": snapshot.retirement,
        "crypto": snapshot.crypto,
        "other_assets": snapshot.other_assets,
        "debt": snapshot.debt,
        "annual_expenses": snapshot.annual_expenses,
        "financial_freedom_number": snapshot.financial_freedom_number,
        "notes": snapshot.notes,
        "created_at": snapshot.created_at,
        "net_worth": net_worth,
        "progress_pct": progress_pct,
        "runway_years": runway_years,
    }


@router.get("/snapshots", response_model=list[WealthSnapshotRead])
def list_snapshots(
    limit: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    snapshots = db.scalars(select(WealthSnapshot).order_by(WealthSnapshot.date.desc()).limit(limit)).all()
    return [_snapshot_response(snapshot) for snapshot in snapshots]


@router.post("/snapshots", response_model=WealthSnapshotRead, status_code=status.HTTP_201_CREATED)
def create_or_update_snapshot(
    payload: WealthSnapshotCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    snapshot = db.scalar(select(WealthSnapshot).where(WealthSnapshot.date == payload.date))
    if snapshot is None:
        snapshot = WealthSnapshot(**payload.model_dump())
        db.add(snapshot)
    else:
        for key, value in payload.model_dump().items():
            setattr(snapshot, key, value)
    db.commit()
    db.refresh(snapshot)
    return _snapshot_response(snapshot)


@router.get("/summary", response_model=WealthSummary)
def wealth_summary(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    snapshot = db.scalar(select(WealthSnapshot).order_by(WealthSnapshot.date.desc()).limit(1))
    if snapshot is None:
        return WealthSummary(
            latest=None,
            net_worth=0,
            financial_freedom_number=None,
            progress_pct=None,
            runway_years=None,
        )
    latest = _snapshot_response(snapshot)
    return WealthSummary(
        latest=latest,
        net_worth=latest["net_worth"],
        financial_freedom_number=latest["financial_freedom_number"],
        progress_pct=latest["progress_pct"],
        runway_years=latest["runway_years"],
    )
