from fastapi import APIRouter, Depends, HTTPException
from auth import get_current_user
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from database import SessionLocal
from models import Income, User
from auth import get_db, create_access_token, SECRET_KEY, ALGORITHM
from jose import jwt, JWTError
from pydantic import BaseModel

# Pydantic schema
class IncomeCreate(BaseModel):
    amount: float
    source: str
    date: datetime = datetime.utcnow()
    wallet_id: int = None

class IncomeResponse(BaseModel):
    id: int
    amount: float
    source: str
    date: datetime
    user_id: int
    wallet_id: int = None

    class Config:
        from_attributes = True

router = APIRouter()

# Create new income
@router.post("/", response_model=IncomeResponse)
def create_income(income: IncomeCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_income = Income(
        amount=income.amount,
        source=income.source,
        date=income.date,
        user_id=current_user.id,
        wallet_id=income.wallet_id
    )
    db.add(new_income)
    
    # Update wallet balance if wallet_id is provided
    if income.wallet_id:
        from models import Wallet
        wallet = db.query(Wallet).filter(Wallet.id == income.wallet_id, Wallet.user_id == current_user.id).first()
        if wallet:
            wallet.balance += income.amount
        else:
            raise HTTPException(status_code=404, detail="Wallet not found")

    db.commit()
    db.refresh(new_income)
    return new_income

# Get all incomes for current user
@router.get("/", response_model=List[IncomeResponse])
def get_incomes(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    incomes = db.query(Income).filter(Income.user_id == current_user.id).all()
    return incomes
