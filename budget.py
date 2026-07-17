"""
WiseMoney Budget Intelligence Module

Responsibilities
----------------
• Include Budget CRUD Router
• Budget Recommendations
• Budget Health Analysis
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

# Import CRUD router
from budget_crud import router as budget_crud_router

router = APIRouter()

# ==========================================================
# Budget Recommendation
# ==========================================================

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

    if not expenses:

        return {

            "total_spending": 0,

            "recommended_budget": {}

        }

    total_spending = sum(

        row.total

        for row in expenses

    )

    recommendations = {}

    for category, amount in expenses:

        percentage = 0

        if total_spending > 0:

            percentage = (

                amount /

                total_spending

            ) * 100

        if percentage >= 40:

            risk = "High"

            recommended = amount * 0.85

        elif percentage >= 20:

            risk = "Medium"

            recommended = amount * 0.95

        else:

            risk = "Low"

            recommended = amount

        recommendations[category] = {

            "current_spending":

                round(amount, 2),

            "spending_percentage":

                round(percentage, 2),

            "risk_level":

                risk,

            "recommended_budget":

                round(recommended, 2),

            "suggested_reduction":

                round(

                    amount - recommended,

                    2

                )

        }

    return {

        "total_spending":

            round(total_spending, 2),

        "recommended_budget":

            recommendations

    }

# ==========================================================
# Budget Health
# ==========================================================

@router.get("/health")
def budget_health(

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)

):

    budgets = (

        db.query(Budget)

        .filter(
            Budget.user_id == current_user.id
        )

        .all()

    )

    if not budgets:

        return {

            "budget_health_score": 0,

            "status": "No Budgets",

            "total_categories": 0,

            "breached_categories": 0,

            "budget_details": []

        }
    
    start, end = month_range()

    for budget in budgets:
        spent = (
            db.query(func.sum(Expense.amount))
            .filter(
                Expense.user_id == current_user.id,
                Expense.category == budget.category,
                Expense.date >= start,  # <-- Added month start filter
                Expense.date < end     # <-- Added month end filter
            )
            .scalar() or 0
        )
        
    breached = 0

    details = []

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

            utilization = round(

                (spent / budget.monthly_limit) * 100,

                2

            )

        if spent > budget.monthly_limit:

            breached += 1

        details.append({

            "category": budget.category,

            "limit": round(
                budget.monthly_limit,
                2
            ),

            "spent": round(
                spent,
                2
            ),

            "utilization": utilization

        })

    score = round(

        max(

            0,

            100 -

            (

                breached /

                len(budgets)

            ) * 100

        )

    )

    if score >= 90:

        status = "Excellent"

    elif score >= 75:

        status = "Good"

    elif score >= 60:

        status = "Needs Improvement"

    else:

        status = "Poor"

    return {

        "budget_health_score": score,

        "status": status,

        "total_categories": len(budgets),

        "breached_categories": breached,

        "budget_details": details

    }


# ==========================================================
# Include CRUD Router
# KEEP THIS AT THE VERY END
# ==========================================================

router.include_router(
    budget_crud_router
)