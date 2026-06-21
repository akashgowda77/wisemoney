from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from auth import get_db, get_current_user
from models import Income, Expense, Wallet, User

router = APIRouter()

@router.get("/")
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    total_income = (
        db.query(func.sum(Income.amount))
        .filter(Income.user_id == current_user.id)
        .scalar()
        or 0
    )

    total_expense = (
        db.query(func.sum(Expense.amount))
        .filter(Expense.user_id == current_user.id)
        .scalar()
        or 0
    )

    total_wallet_balance = (
        db.query(func.sum(Wallet.balance))
        .filter(Wallet.user_id == current_user.id)
        .scalar()
        or 0
    )

    net_savings = total_income - total_expense

    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "wallet_balance": total_wallet_balance,
        "net_savings": net_savings
    }

@router.get("/score")
def get_financial_score(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    total_income = (
        db.query(func.sum(Income.amount))
        .filter(Income.user_id == current_user.id)
        .scalar()
        or 0
    )

    total_expense = (
        db.query(func.sum(Expense.amount))
        .filter(Expense.user_id == current_user.id)
        .scalar()
        or 0
    )

    if total_income == 0:
        return {
            "financial_score": 0,
            "status": "No Data"
        }

    savings_ratio = (total_income - total_expense) / total_income

    score = max(0, min(100, int(savings_ratio * 100)))

    if score >= 85:
        status = "Excellent"
    elif score >= 70:
        status = "Good"
    elif score >= 50:
        status = "Average"
    else:
        status = "Poor"

    return {
    "financial_score": score,
    "status": status,
    "income": total_income,
    "expense": total_expense,
    "savings_ratio": round(savings_ratio * 100, 2)
}
