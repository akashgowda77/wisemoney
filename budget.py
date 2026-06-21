from unicodedata import category

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from auth import get_db, get_current_user
from models import Transaction, User

router = APIRouter()

@router.get("/recommendation")
def budget_recommendation(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    expenses = (
        db.query(
            Transaction.category,
            func.sum(Transaction.amount).label("total")
        )
        .filter(
            Transaction.user_id == current_user.id,
            Transaction.transaction_type == "expense"
        )
        .group_by(Transaction.category)
        .all()
    )

    recommendations = {}

    for category, amount in expenses:
        if amount > 5000:
            recommendations[category] = {
                "current_spending": round(amount, 2),
                "recommended_budget": round(amount * 0.9, 2),
                "suggested_reduction": round(amount * 0.1, 2)
            }
        else:
            recommendations[category] = {
            "current_spending": round(amount, 2),
            "recommended_budget": round(amount, 2),
            "suggested_reduction": 0
        }
    return {
        "recommended_budget": recommendations
    }
