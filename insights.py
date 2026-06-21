from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from auth import get_db, get_current_user
from models import Transaction, User

router = APIRouter()

@router.get("/")
def spending_insights(
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

    if not expenses:
        return {"message": "No expense data available"}

    total_spend = sum(x.total for x in expenses)

    top_category = max(expenses, key=lambda x: x.total)

    percentage = round((top_category.total / total_spend) * 100, 2)

    return {
        "top_category": top_category.category,
        "amount_spent": round(top_category.total, 2),
        "percentage": percentage,
        "insight":
            f"{top_category.category} accounts for {percentage}% of your total spending.",
        "recommendation":
            f"Consider reducing {top_category.category} expenses by 10-15% to improve savings."
    }