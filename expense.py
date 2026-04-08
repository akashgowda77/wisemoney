from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from database import SessionLocal
from models import Expense, User
from auth import get_db, SECRET_KEY, ALGORITHM
from jose import jwt, JWTError
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer

# Pydantic schema
class ExpenseCreate(BaseModel):
    amount: float
    category: str
    date: datetime = datetime.utcnow()
    wallet_id: int = None

class ExpenseResponse(BaseModel):
    id: int
    amount: float
    category: str
    date: datetime
    user_id: int
    wallet_id: int = None

    class Config:
        from_attributes = True

router = APIRouter()

# Get current user
from auth import get_current_user

# Create expense
@router.post("/", response_model=ExpenseResponse)
def create_expense(expense: ExpenseCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_expense = Expense(
        amount=expense.amount,
        category=expense.category,
        date=expense.date,
        user_id=current_user.id,
        wallet_id=expense.wallet_id
    )
    db.add(new_expense)
    
    # Update wallet balance if wallet_id is provided
    if expense.wallet_id:
        from models import Wallet
        wallet = db.query(Wallet).filter(Wallet.id == expense.wallet_id, Wallet.user_id == current_user.id).first()
        if wallet:
            wallet.balance -= expense.amount
        else:
            raise HTTPException(status_code=404, detail="Wallet not found")

    db.commit()
    db.refresh(new_expense)
    return new_expense

# Get all expenses for current user
@router.get("/", response_model=List[ExpenseResponse])
def get_expenses(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    expenses = db.query(Expense).filter(Expense.user_id == current_user.id).all()
    return expenses
