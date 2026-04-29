import os
import uuid
from datetime import datetime, timezone

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from auth import get_current_user
from database import get_db
from models.markets import MarketQuote, MarketStock
from models.user import User
from schemas.markets import MarketQuoteRead, MarketStockCreate, MarketStockPatch, MarketStockRead

router = APIRouter(prefix="/markets", tags=["markets"], dependencies=[Depends(get_current_user)])


def _normalize_ticker(ticker: str) -> str:
    return ticker.strip().upper()


def _latest_quote(db: Session, ticker: str) -> MarketQuote | None:
    return db.scalar(
        select(MarketQuote)
        .where(MarketQuote.ticker == ticker)
        .order_by(MarketQuote.fetched_at.desc())
        .limit(1)
    )


def _stock_response(db: Session, stock: MarketStock) -> dict:
    data = {
        "id": stock.id,
        "ticker": stock.ticker,
        "company_name": stock.company_name,
        "shares": stock.shares,
        "average_cost": stock.average_cost,
        "watchlist": stock.watchlist,
        "thesis": stock.thesis,
        "notes": stock.notes,
        "created_at": stock.created_at,
        "latest_quote": _latest_quote(db, stock.ticker),
    }
    return data


@router.get("/stocks", response_model=list[MarketStockRead])
def list_stocks(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    stocks = db.scalars(select(MarketStock).order_by(MarketStock.ticker.asc())).all()
    return [_stock_response(db, stock) for stock in stocks]


@router.post("/stocks", response_model=MarketStockRead, status_code=status.HTTP_201_CREATED)
def create_stock(payload: MarketStockCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    stock = MarketStock(**payload.model_dump())
    stock.ticker = _normalize_ticker(stock.ticker)
    db.add(stock)
    db.commit()
    db.refresh(stock)
    return _stock_response(db, stock)


@router.get("/stocks/{stock_id}", response_model=MarketStockRead)
def get_stock(stock_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    stock = db.get(MarketStock, stock_id)
    if stock is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stock not found")
    return _stock_response(db, stock)


@router.patch("/stocks/{stock_id}", response_model=MarketStockRead)
def patch_stock(
    stock_id: uuid.UUID,
    payload: MarketStockPatch,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    stock = db.get(MarketStock, stock_id)
    if stock is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stock not found")
    values = payload.model_dump(exclude_unset=True)
    if "ticker" in values and values["ticker"] is not None:
        values["ticker"] = _normalize_ticker(values["ticker"])
    for key, value in values.items():
        setattr(stock, key, value)
    db.commit()
    db.refresh(stock)
    return _stock_response(db, stock)


def fetch_quote_from_provider(ticker: str) -> dict:
    provider = os.getenv("MARKET_DATA_PROVIDER")
    api_key = os.getenv("MARKET_DATA_API_KEY")
    if provider != "alphavantage" or not api_key or api_key.startswith("replace-"):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Configure MARKET_DATA_PROVIDER=alphavantage and MARKET_DATA_API_KEY to refresh stock quotes",
        )

    try:
        response = httpx.get(
            "https://www.alphavantage.co/query",
            params={"function": "GLOBAL_QUOTE", "symbol": ticker, "apikey": api_key},
            timeout=10,
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Market data provider request failed") from exc

    data = response.json()
    quote = data.get("Global Quote") or {}
    try:
        price = float(quote["05. price"])
        change_amount = float(quote.get("09. change") or 0)
        change_percent = float((quote.get("10. change percent") or "0%").replace("%", ""))
    except (KeyError, TypeError, ValueError):
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Market data provider returned no quote")

    return {
        "ticker": ticker,
        "price": price,
        "change_amount": change_amount,
        "change_percent": change_percent,
        "currency": "USD",
        "provider": provider,
    }


@router.get("/stocks/{stock_id}/quote", response_model=MarketQuoteRead)
def refresh_stock_quote(stock_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    stock = db.get(MarketStock, stock_id)
    if stock is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stock not found")

    quote_data = fetch_quote_from_provider(stock.ticker)
    quote = MarketQuote(**quote_data, fetched_at=datetime.now(timezone.utc))
    db.add(quote)
    db.commit()
    db.refresh(quote)
    return quote
