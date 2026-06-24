from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from models import Wallet, User
from auth import get_db, get_current_user

router = APIRouter()


# -------------------------
# Pydantic Schemas
# -------------------------

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


# -------------------------
# Create Wallet
# -------------------------

@router.post("/", response_model=WalletResponse)
def create_wallet(
    wallet: WalletCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # Prevent negative balance
    if wallet.balance < 0:
        raise HTTPException(
            status_code=400,
            detail="Balance cannot be negative"
        )

    # Prevent duplicate wallet names
    existing_wallet = db.query(Wallet).filter(
        Wallet.name == wallet.name,
        Wallet.user_id == current_user.id
    ).first()

    if existing_wallet:
        raise HTTPException(
            status_code=400,
            detail="Wallet already exists"
        )

    new_wallet = Wallet(
        name=wallet.name,
        balance=wallet.balance,
        user_id=current_user.id
    )

    db.add(new_wallet)
    db.commit()
    db.refresh(new_wallet)

    return new_wallet


# -------------------------
# Get All Wallets
# -------------------------

@router.get("/", response_model=List[WalletResponse])
def get_wallets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    wallets = db.query(Wallet).filter(
        Wallet.user_id == current_user.id
    ).all()

    return wallets


# -------------------------
# Get Wallet By ID
# -------------------------

@router.get("/{wallet_id}", response_model=WalletResponse)
def get_wallet(
    wallet_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    wallet = db.query(Wallet).filter(
        Wallet.id == wallet_id,
        Wallet.user_id == current_user.id
    ).first()

    if not wallet:
        raise HTTPException(
            status_code=404,
            detail="Wallet not found"
        )

    return wallet