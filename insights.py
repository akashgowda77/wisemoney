from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from auth import get_db, get_current_user
from models import Expense, User

router = APIRouter()

@router.get("/")
def spending_insights(
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

    if not expenses:
        return {"message": "No expense data available"}

    total_spend = sum(x.total for x in expenses)

    top_category = max(expenses, key=lambda x: x.total)

    percentage = round((top_category.total / total_spend) * 100, 2)

    return {
        "top_category": top_category.category,
        "amount_spent": top_category.total,
        "percentage": percentage,
        "insight":
            f"{top_category.category} accounts for {percentage}% of your total spending."
    }