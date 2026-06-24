"""
WiseMoney AI Financial Advisor

Purpose:
Provides personalized financial recommendations
based on user's financial health, goals,
spending patterns and wallet balances.

Uses:
FinancialEngine as the single source of truth.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from auth import get_db, get_current_user

from models import (
    User,
    Transaction,
    Goal
)

from financial_engine import FinancialEngine

router = APIRouter()


# ==================================================
# AI Financial Advisor
# ==================================================

@router.get("/recommend")
def financial_advisor(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generates financial recommendations
    using FinancialEngine and spending analysis.
    """

    # ----------------------------------
    # Financial Health Engine
    # ----------------------------------

    health = FinancialEngine.calculate(
        db,
        current_user
    )

    # ----------------------------------
    # Spending Categories
    # ----------------------------------

    category_expenses = (
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

    top_category = None

    if category_expenses:
        top_category = max(
            category_expenses,
            key=lambda x: x.total
        )

    # ----------------------------------
    # Goals Analysis
    # ----------------------------------

    goals = (
        db.query(Goal)
        .filter(
            Goal.user_id == current_user.id
        )
        .all()
    )

    goal_data = []

    for goal in goals:

        progress = 0

        if goal.target_amount > 0:
            progress = (
                goal.current_savings
                / goal.target_amount
            ) * 100

        remaining_amount = max(
            0,
            goal.target_amount -
            goal.current_savings
        )

        monthly_surplus = max(
            health["income"] -
            health["expense"],
            0
        )

        if monthly_surplus > 0:
            estimated_months = round(
                remaining_amount /
                monthly_surplus,
                1
            )
        else:
            estimated_months = None

        goal_data.append({
            "goal_name": goal.goal_name,
            "status": goal.status,
            "progress_percentage": round(
                progress,
                2
            ),
            "remaining_amount": round(
                remaining_amount,
                2
            ),
            "estimated_months": estimated_months
        })

    # ----------------------------------
    # Advisor Recommendations
    # ----------------------------------

    recommendations = list(
        health["recommendations"]
    )

    if top_category:
        recommendations.append(
            f"Highest spending category is "
            f"'{top_category.category}'. "
            f"Review spending in this category."
        )

    for goal in goals:

        if goal.target_amount <= 0:
            continue

        progress = (
            goal.current_savings
            / goal.target_amount
        ) * 100

        if progress < 50:
            recommendations.append(
                f"Goal '{goal.goal_name}' is below "
                f"50% completion. Consider increasing "
                f"monthly contributions."
            )

    # Remove duplicate recommendations
    recommendations = list(
        dict.fromkeys(recommendations)
    )

    # ----------------------------------
    # Response
    # ----------------------------------

    return {
        "financial_health": {
            "financial_score":
                health["financial_score"],

            "grade":
                health["grade"],

            "health_status":
                health["health_status"]
        },

        "financial_summary": {
            "income":
                round(health["income"], 2),

            "expense":
                round(health["expense"], 2),

            "wallet_balance":
                round(health["wallet_balance"], 2),

            "savings_ratio":
                health["savings_ratio"]
        },

        "top_spending_category":
            top_category.category
            if top_category else None,

        "goal_analysis":
            goal_data,

        "recommendations":
            recommendations
    }