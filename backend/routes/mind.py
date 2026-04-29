import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from auth import get_current_user
from database import get_db
from models.mind import Book, Decision, PhilosophyNote
from models.user import User
from schemas.mind import (
    BookCreate,
    BookPatch,
    BookRead,
    DecisionCreate,
    DecisionPatch,
    DecisionRead,
    PhilosophyNoteCreate,
    PhilosophyNoteRead,
)

router = APIRouter(tags=["mind"], dependencies=[Depends(get_current_user)])


@router.get("/books", response_model=list[BookRead])
def list_books(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.scalars(select(Book).order_by(Book.created_at.desc(), Book.title.asc())).all()


@router.post("/books", response_model=BookRead, status_code=status.HTTP_201_CREATED)
def create_book(payload: BookCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    book = Book(**payload.model_dump())
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


@router.get("/books/{book_id}", response_model=BookRead)
def get_book(book_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    book = db.get(Book, book_id)
    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return book


@router.patch("/books/{book_id}", response_model=BookRead)
def patch_book(
    book_id: uuid.UUID,
    payload: BookPatch,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    book = db.get(Book, book_id)
    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(book, key, value)
    db.commit()
    db.refresh(book)
    return book


@router.get("/philosophy", response_model=list[PhilosophyNoteRead])
def list_philosophy_notes(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.scalars(select(PhilosophyNote).order_by(PhilosophyNote.date.desc(), PhilosophyNote.created_at.desc())).all()


@router.post("/philosophy", response_model=PhilosophyNoteRead, status_code=status.HTTP_201_CREATED)
def create_philosophy_note(
    payload: PhilosophyNoteCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    note = PhilosophyNote(**payload.model_dump())
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@router.get("/decisions", response_model=list[DecisionRead])
def list_decisions(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.scalars(select(Decision).order_by(Decision.date.desc(), Decision.created_at.desc())).all()


@router.post("/decisions", response_model=DecisionRead, status_code=status.HTTP_201_CREATED)
def create_decision(payload: DecisionCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    decision = Decision(**payload.model_dump())
    db.add(decision)
    db.commit()
    db.refresh(decision)
    return decision


@router.get("/decisions/{decision_id}", response_model=DecisionRead)
def get_decision(decision_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    decision = db.get(Decision, decision_id)
    if decision is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Decision not found")
    return decision


@router.patch("/decisions/{decision_id}", response_model=DecisionRead)
def patch_decision(
    decision_id: uuid.UUID,
    payload: DecisionPatch,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    decision = db.get(Decision, decision_id)
    if decision is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Decision not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(decision, key, value)
    db.commit()
    db.refresh(decision)
    return decision
