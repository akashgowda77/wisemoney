from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from pydantic import BaseModel

from auth import get_db, get_current_user
from models import Transaction, User

router = APIRouter()

class TransactionCreate(BaseModel):
    amount: float
    transaction_type: str
    category: str | None = None
    description: str | None = None
    wallet_id: int

class TransactionResponse(BaseModel):
    id: int
    amount: float
    transaction_type: str
    category: str | None
    description: str | None
    wallet_id: int
    user_id: int

    class Config:
        from_attributes = True


@router.post("/", response_model=TransactionResponse)
def create_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_transaction = Transaction(
        amount=transaction.amount,
        transaction_type=transaction.transaction_type,
        category=transaction.category,
        description=transaction.description,
        wallet_id=transaction.wallet_id,
        user_id=current_user.id
    )

    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    return new_transaction


@router.get("/", response_model=List[TransactionResponse])
def get_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return (
        db.query(Transaction)
        .filter(Transaction.user_id == current_user.id)
        .all()
    )