from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from auth import get_db, get_current_user
from models import User, Income, Expense, Wallet, Goal

router = APIRouter()

@router.get("/recommend")
def financial_advisor(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Income
    total_income = (
        db.query(func.sum(Income.amount))
        .filter(Income.user_id == current_user.id)
        .scalar()
        or 0
    )

    # Expense
    total_expense = (
        db.query(func.sum(Expense.amount))
        .filter(Expense.user_id == current_user.id)
        .scalar()
        or 0
    )

    # Wallet Balance
    wallet_balance = (
        db.query(func.sum(Wallet.balance))
        .filter(Wallet.user_id == current_user.id)
        .scalar()
        or 0
    )

    # Goals
    goals = (
        db.query(Goal)
        .filter(Goal.user_id == current_user.id)
        .all()
    )

    recommendations = []

    # Financial Score Logic
    if total_income > 0:
        savings_ratio = (
            (total_income - total_expense)
            / total_income
        ) * 100
    else:
        savings_ratio = 0

    if savings_ratio >= 40:
        financial_score = 90
        recommendations.append(
            "Excellent savings rate. Consider investing part of your savings."
        )
    elif savings_ratio >= 20:
        financial_score = 70
        recommendations.append(
            "Good financial health. Increase savings by 5-10% monthly."
        )
    else:
        financial_score = 40
        recommendations.append(
            "Expenses are consuming most of your income. Focus on cost reduction."
        )

    # Spending Insights
    category_expenses = (
        db.query(
            Expense.category,
            func.sum(Expense.amount).label("total")
        )
        .filter(Expense.user_id == current_user.id)
        .group_by(Expense.category)
        .all()
    )

    top_category = None

    if category_expenses:
        top_category = max(
            category_expenses,
            key=lambda x: x.total
        )

        recommendations.append(
            f"Highest spending category is {top_category.category}. Review this category for optimization."
        )

    # Goal Analysis
    goal_data = []

    for goal in goals:

        progress = (
            goal.current_savings
            / goal.target_amount
        ) * 100

        goal_data.append({
            "goal": goal.goal_name,
            "progress": round(progress, 2)
        })

        if progress < 50:
            recommendations.append(
                f"Goal '{goal.goal_name}' is below 50% completion. Consider allocating more monthly savings."
            )

    # Emergency Fund Check
    if wallet_balance < (total_expense * 3):
        recommendations.append(
            "Emergency fund appears low. Aim for 3-6 months of expenses."
        )

    return {
        "financial_score": financial_score,
        "income": total_income,
        "expense": total_expense,
        "wallet_balance": wallet_balance,
        "goals": goal_data,
        "top_spending_category":
            top_category.category if top_category else None,
        "recommendations": recommendations
    }