"""
WiseMoney Budget Intelligence Module

Purpose:
- Budget CRUD Operations
- Budget Recommendations
- Budget Health Analysis

Features:
- Dynamic Budget Recommendations
- Spending Distribution Analysis
- Budget Health Score
- Budget Risk Detection
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from auth import get_db, get_current_user
from models import (
    Transaction,
    Budget,
    Expense,
    User
)

from budget_module import router as budget_crud_router

router = APIRouter()

# --------------------------------------------------
# Include Budget CRUD Endpoints
# --------------------------------------------------

router.include_router(budget_crud_router)


# ==================================================
# Budget Recommendations
# ==================================================

@router.get("/recommendation")
def budget_recommendation(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generates intelligent budget recommendations
    based on spending distribution.
    """

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
        return {
            "message": "No expense data available"
        }

    total_spending = sum(
        expense.total
        for expense in expenses
    )

    recommendations = {}

    for category, amount in expenses:

        percentage = 0

        if total_spending > 0:
            percentage = (
                amount / total_spending
            ) * 100

        # ----------------------------------
        # Risk Detection
        # ----------------------------------

        if percentage >= 40:

            risk_level = "High"

            recommended_budget = amount * 0.85

            recommendations[category] = {
                "current_spending": round(amount, 2),
                "spending_percentage": round(
                    percentage,
                    2
                ),
                "risk_level": risk_level,
                "recommended_budget": round(
                    recommended_budget,
                    2
                ),
                "suggested_reduction": round(
                    amount - recommended_budget,
                    2
                )
            }

        elif percentage >= 20:

            risk_level = "Medium"

            recommended_budget = amount * 0.95

            recommendations[category] = {
                "current_spending": round(amount, 2),
                "spending_percentage": round(
                    percentage,
                    2
                ),
                "risk_level": risk_level,
                "recommended_budget": round(
                    recommended_budget,
                    2
                ),
                "suggested_reduction": round(
                    amount - recommended_budget,
                    2
                )
            }

        else:

            risk_level = "Low"

            recommendations[category] = {
                "current_spending": round(amount, 2),
                "spending_percentage": round(
                    percentage,
                    2
                ),
                "risk_level": risk_level,
                "recommended_budget": round(
                    amount,
                    2
                ),
                "suggested_reduction": 0
            }

    return {
        "total_spending": round(
            total_spending,
            2
        ),
        "recommended_budget": recommendations
    }


# ==================================================
# Budget Health Score
# ==================================================

@router.get("/health")
def budget_health(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Calculates budget discipline score.

    Score Range:
    0 - 100
    """

    budgets = (
        db.query(Budget)
        .filter(
            Budget.user_id == current_user.id
        )
        .all()
    )

    if not budgets:
        return {
            "message": "No budgets created yet"
        }

    breached_categories = 0

    budget_details = []

    for budget in budgets:

        spent = (
            db.query(
                func.sum(Expense.amount)
            )
            .filter(
                Expense.user_id == current_user.id,
                Expense.category == budget.category
            )
            .scalar()
            or 0
        )

        utilization = 0

        if budget.monthly_limit > 0:
            utilization = (
                spent /
                budget.monthly_limit
            ) * 100

        if spent > budget.monthly_limit:
            breached_categories += 1

        budget_details.append({
            "category": budget.category,
            "limit": round(
                budget.monthly_limit,
                2
            ),
            "spent": round(
                spent,
                2
            ),
            "utilization": round(
                utilization,
                2
            )
        })

    health_score = max(
        0,
        round(
            100 -
            (
                breached_categories /
                len(budgets)
            ) * 100
        )
    )

    # ----------------------------------
    # Health Status
    # ----------------------------------

    if health_score >= 90:
        status = "Excellent"

    elif health_score >= 75:
        status = "Good"

    elif health_score >= 60:
        status = "Needs Improvement"

    else:
        status = "Poor"

    return {
        "budget_health_score": health_score,
        "status": status,
        "total_categories": len(budgets),
        "breached_categories": breached_categories,
        "budget_details": budget_details
    }