from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from auth import get_db, get_current_user
from models import Wallet, Transaction, User

router = APIRouter()


# ----------------------------------
# Schemas
# ----------------------------------

class WalletCreate(BaseModel):
    name: str
    balance: float


class WalletTransfer(BaseModel):
    from_wallet: int
    to_wallet: int
    amount: float


class WalletResponse(BaseModel):
    id: int
    name: str
    balance: float
    user_id: int

    class Config:
        from_attributes = True


# ----------------------------------
# Create Wallet
# ----------------------------------

@router.post("/", response_model=WalletResponse)
def create_wallet(
    wallet: WalletCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if wallet.balance < 0:
        raise HTTPException(
            status_code=400,
            detail="Balance cannot be negative"
        )

    existing_wallet = db.query(Wallet).filter(
        Wallet.user_id == current_user.id,
        Wallet.name == wallet.name
    ).first()

    if existing_wallet:
        raise HTTPException(
            status_code=400,
            detail="Wallet with this name already exists"
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


# ----------------------------------
# Get All Wallets
# ----------------------------------

@router.get("/", response_model=List[WalletResponse])
def get_wallets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return (
        db.query(Wallet)
        .filter(Wallet.user_id == current_user.id)
        .all()
    )


# ----------------------------------
# Get Wallet By ID
# ----------------------------------

@router.get("/{wallet_id}", response_model=WalletResponse)
def get_wallet(
    wallet_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    wallet = (
        db.query(Wallet)
        .filter(
            Wallet.id == wallet_id,
            Wallet.user_id == current_user.id
        )
        .first()
    )

    if not wallet:
        raise HTTPException(
            status_code=404,
            detail="Wallet not found"
        )

    return wallet


# ----------------------------------
# Transfer Money Between Wallets
# ----------------------------------

@router.post("/transfer")
def transfer_money(
    transfer: WalletTransfer,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if transfer.amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Transfer amount must be greater than zero"
        )

    if transfer.from_wallet == transfer.to_wallet:
        raise HTTPException(
            status_code=400,
            detail="Cannot transfer to the same wallet"
        )

    source_wallet = (
        db.query(Wallet)
        .filter(
            Wallet.id == transfer.from_wallet,
            Wallet.user_id == current_user.id
        )
        .first()
    )

    destination_wallet = (
        db.query(Wallet)
        .filter(
            Wallet.id == transfer.to_wallet,
            Wallet.user_id == current_user.id
        )
        .first()
    )

    if not source_wallet:
        raise HTTPException(
            status_code=404,
            detail="Source wallet not found"
        )

    if not destination_wallet:
        raise HTTPException(
            status_code=404,
            detail="Destination wallet not found"
        )

    if source_wallet.balance < transfer.amount:
        raise HTTPException(
            status_code=400,
            detail="Insufficient balance"
        )

    # Move funds
    source_wallet.balance -= transfer.amount
    destination_wallet.balance += transfer.amount

    # Record transfer in ledger
    transaction = Transaction(
        amount=transfer.amount,
        transaction_type="wallet_transfer",
        category="Wallet Transfer",
        description=f"{source_wallet.name} → {destination_wallet.name}",
        wallet_id=source_wallet.id,
        to_wallet_id=destination_wallet.id,
        user_id=current_user.id
    )

    db.add(transaction)
    db.commit()

    return {
        "message": "Transfer completed successfully"
    }


# ----------------------------------
# Wallet Transaction History
# ----------------------------------

@router.get("/{wallet_id}/transactions")
def wallet_transactions(
    wallet_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    wallet = (
        db.query(Wallet)
        .filter(
            Wallet.id == wallet_id,
            Wallet.user_id == current_user.id
        )
        .first()
    )

    if not wallet:
        raise HTTPException(
            status_code=404,
            detail="Wallet not found"
        )

    transactions = (
        db.query(Transaction)
        .filter(
            (Transaction.wallet_id == wallet_id) |
            (Transaction.to_wallet_id == wallet_id)
        )
        .order_by(Transaction.date.desc())
        .all()
    )

    return transactions


# ----------------------------------
# Wallet Statistics
# ----------------------------------

@router.get("/{wallet_id}/stats")
def wallet_stats(
    wallet_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    wallet = (
        db.query(Wallet)
        .filter(
            Wallet.id == wallet_id,
            Wallet.user_id == current_user.id
        )
        .first()
    )

    if not wallet:
        raise HTTPException(
            status_code=404,
            detail="Wallet not found"
        )

    income_total = sum(
        t.amount
        for t in db.query(Transaction).filter(
            Transaction.wallet_id == wallet_id,
            Transaction.transaction_type == "income"
        ).all()
    )

    expense_total = sum(
        t.amount
        for t in db.query(Transaction).filter(
            Transaction.wallet_id == wallet_id,
            Transaction.transaction_type == "expense"
        ).all()
    )

    goal_funding_total = sum(
        t.amount
        for t in db.query(Transaction).filter(
            Transaction.wallet_id == wallet_id,
            Transaction.transaction_type == "goal_funding"
        ).all()
    )

    transfer_out = sum(
        t.amount
        for t in db.query(Transaction).filter(
            Transaction.wallet_id == wallet_id,
            Transaction.transaction_type == "wallet_transfer"
        ).all()
    )

    transfer_in = sum(
        t.amount
        for t in db.query(Transaction).filter(
            Transaction.to_wallet_id == wallet_id,
            Transaction.transaction_type == "wallet_transfer"
        ).all()
    )

    return {
        "wallet_name": wallet.name,
        "current_balance": wallet.balance,
        "total_income": income_total,
        "total_expense": expense_total,
        "goal_funding": goal_funding_total,
        "transfer_out": transfer_out,
        "transfer_in": transfer_in
    }


# ----------------------------------
# Delete Wallet
# ----------------------------------

@router.delete("/{wallet_id}")
def delete_wallet(
    wallet_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    wallet = (
        db.query(Wallet)
        .filter(
            Wallet.id == wallet_id,
            Wallet.user_id == current_user.id
        )
        .first()
    )

    if not wallet:
        raise HTTPException(
            status_code=404,
            detail="Wallet not found"
        )

    if wallet.balance > 0:
        raise HTTPException(
            status_code=400,
            detail="Empty wallet before deleting it"
        )

    db.delete(wallet)
    db.commit()

    return {
        "message": "Wallet deleted successfully"
    }

