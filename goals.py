from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from auth import get_db, get_current_user
from models import Goal, Wallet, Transaction, User

router = APIRouter()


# ----------------------------------
# Request / Response Schemas
# ----------------------------------

class GoalCreate(BaseModel):
    goal_name: str
    target_amount: float
    current_savings: float = 0
    priority: str = "medium"
    notes: str | None = None


class GoalFundRequest(BaseModel):
    wallet_id: int
    amount: float


class GoalResponse(BaseModel):
    id: int
    goal_name: str
    target_amount: float
    current_savings: float

    priority: str
    notes: str | None

    status: str

    created_at: datetime
    achieved_at: datetime | None

    user_id: int

    class Config:
        from_attributes = True


# ----------------------------------
# Create Goal
# ----------------------------------

@router.post("/", response_model=GoalResponse)
def create_goal(
    goal: GoalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Basic validation
    if goal.target_amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Target amount must be greater than zero"
        )

    if goal.current_savings < 0:
        raise HTTPException(
            status_code=400,
            detail="Current savings cannot be negative"
        )

    new_goal = Goal(
        goal_name=goal.goal_name,
        target_amount=goal.target_amount,
        current_savings=goal.current_savings,
        priority=goal.priority,
        notes=goal.notes,
        user_id=current_user.id
    )

    db.add(new_goal)
    db.commit()
    db.refresh(new_goal)

    return new_goal


# ----------------------------------
# Get All Goals
# ----------------------------------

@router.get("/", response_model=List[GoalResponse])
def get_goals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return (
        db.query(Goal)
        .filter(Goal.user_id == current_user.id)
        .all()
    )


# ----------------------------------
# Get Active Goals
# ----------------------------------

@router.get("/active", response_model=List[GoalResponse])
def get_active_goals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return (
        db.query(Goal)
        .filter(
            Goal.user_id == current_user.id,
            Goal.status == "active"
        )
        .all()
    )


# ----------------------------------
# Get Achieved Goals
# ----------------------------------

@router.get("/achieved", response_model=List[GoalResponse])
def get_achieved_goals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return (
        db.query(Goal)
        .filter(
            Goal.user_id == current_user.id,
            Goal.status == "achieved"
        )
        .all()
    )


# ----------------------------------
# Goal Progress
# ----------------------------------

@router.get("/{goal_id}")
def goal_progress(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    goal = (
        db.query(Goal)
        .filter(
            Goal.id == goal_id,
            Goal.user_id == current_user.id
        )
        .first()
    )

    if not goal:
        raise HTTPException(
            status_code=404,
            detail="Goal not found"
        )

    progress = (
        goal.current_savings /
        goal.target_amount
    ) * 100

    return {
        "id": goal.id,
        "goal_name": goal.goal_name,
        "target_amount": goal.target_amount,
        "current_savings": goal.current_savings,
        "status": goal.status,
        "priority": goal.priority,
        "progress_percentage": round(progress, 2)
    }


# ----------------------------------
# Fund Goal From Wallet
# ----------------------------------

@router.post("/{goal_id}/fund")
def fund_goal(
    goal_id: int,
    funding: GoalFundRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if funding.amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Amount must be greater than zero"
        )

    goal = (
        db.query(Goal)
        .filter(
            Goal.id == goal_id,
            Goal.user_id == current_user.id
        )
        .first()
    )

    if not goal:
        raise HTTPException(
            status_code=404,
            detail="Goal not found"
        )

    if goal.status == "achieved":
        raise HTTPException(
            status_code=400,
            detail="Goal already achieved"
        )
    
    remaining_needed = goal.target_amount - goal.current_savings
    if funding.amount > remaining_needed:
        raise HTTPException(
            status_code=400,
            detail=f"Funding amount ({funding.amount}) exceeds the remaining required amount ({remaining_needed}) to achieve this goal."
        )
    
    wallet = (
        db.query(Wallet)
        .filter(
            Wallet.id == funding.wallet_id,
            Wallet.user_id == current_user.id
        )
        .first()
    )

    if not wallet:
        raise HTTPException(
            status_code=404,
            detail="Wallet not found"
        )

    if wallet.balance < funding.amount:
        raise HTTPException(
            status_code=400,
            detail="Insufficient wallet balance"
        )

    # Deduct money from wallet
    wallet.balance -= funding.amount

    # Add money to goal
    goal.current_savings += funding.amount

    # Record transaction
    transaction = Transaction(
        amount=funding.amount,
        transaction_type="goal_funding",
        category="Goal Funding",
        description=f"Funded goal: {goal.goal_name}",
        wallet_id=wallet.id,
        user_id=current_user.id
    )

    db.add(transaction)

    # Auto mark as achieved
    if goal.current_savings >= goal.target_amount:
        goal.status = "achieved"
        goal.achieved_at = datetime.utcnow()

    db.commit()

    return {
        "message": "Goal funded successfully",
        "goal_name": goal.goal_name,
        "current_savings": goal.current_savings,
        "target_amount": goal.target_amount,
        "status": goal.status
    }


# ----------------------------------
# Delete Goal
# ----------------------------------

@router.delete("/{goal_id}")
def delete_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    goal = (
        db.query(Goal)
        .filter(
            Goal.id == goal_id,
            Goal.user_id == current_user.id
        )
        .first()
    )
    
    # 1. Query the ledger for all transaction records funding this goal
    funding_transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user.id,
        Transaction.transaction_type == "goal_funding",
        Transaction.description == f"Funded goal: {goal.goal_name}"
    ).all()

    # 2. Refund each transaction's amount back to its original wallet
    for tx in funding_transactions:
        # Find original wallet
        wallet = db.query(Wallet).filter(Wallet.id == tx.wallet_id, Wallet.user_id == current_user.id).first()
        if wallet:
            wallet.balance += tx.amount
            # Log the refund in the central ledger
            refund_tx = Transaction(
                amount=tx.amount,
                transaction_type="goal-refund",
                category="Goal Refund",
                description=f"Refund from deleted goal: {goal.goal_name}",
                wallet_id=wallet.id,
                user_id=current_user.id
            )
            db.add(refund_tx)
        else:
            # Fallback: if the original wallet was deleted, refund to the first active wallet
            fallback_wallet = db.query(Wallet).filter(Wallet.user_id == current_user.id).first()
            if fallback_wallet:
                fallback_wallet.balance += tx.amount
                refund_tx = Transaction(
                    amount=tx.amount,
                    transaction_type="goal-refund",
                    category="Goal Refund",
                    description=f"Refund from deleted goal (fallback): {goal.goal_name}",
                    wallet_id=fallback_wallet.id,
                    user_id=current_user.id
                )
                db.add(refund_tx)
    if not goal:
        raise HTTPException(
            status_code=404,
            detail="Goal not found"
        )

    db.delete(goal)
    db.commit()

    return {
        "message": "Goal deleted successfully"
    }
