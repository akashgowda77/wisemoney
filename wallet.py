from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import SessionLocal
from models import Wallet, User
from auth import get_db, SECRET_KEY, ALGORITHM
from jose import jwt, JWTError
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer

# Pydantic schema
class WalletCreate(BaseModel):
    name: str
    balance: float

class WalletResponse(BaseModel):
    id: int
    name: str
    balance: float
    user_id: int

    class Config:
        from_attributes = True

router = APIRouter()
# Get current user
from auth import get_current_user

# Create wallet
@router.post("/", response_model=WalletResponse)
def create_wallet(wallet: WalletCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_wallet = Wallet(
        name=wallet.name,
        balance=wallet.balance,
        user_id=current_user.id
    )
    db.add(new_wallet)
    db.commit()
    db.refresh(new_wallet)
    return new_wallet

# Get all wallets for current user
@router.get("/", response_model=List[WalletResponse])
def get_wallets(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    wallets = db.query(Wallet).filter(Wallet.user_id == current_user.id).all()
    return wallets
