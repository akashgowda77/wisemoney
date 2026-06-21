from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from auth import get_db, get_current_user
from models import Expense, User

router = APIRouter()

@router.get("/recommendation")
def budget_recommendation(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    expenses = (
        db.query(
            Expense.category,
            func.sum(Expense.amount).label("total")
        )
        .filter(Expense.user_id == current_user.id)
        .group_by(Expense.category)
        .all()
    )

    recommendations = {}

    for category, amount in expenses:
        recommendations[category] = round(amount * 0.9, 2)

    return {
        "recommended_budget": recommendations
    }
