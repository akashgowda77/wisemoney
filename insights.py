from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from auth import get_db, get_current_user
from financial_engine import FinancialEngine

from models import (
    Transaction,
    User,
    Wallet,
    Goal,
    Budget,
    Expense
)

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

@router.get("/categories")
def expense_categories(
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

    return [
        {
            "category": x.category,
            "total": float(x.total)
        }
        for x in expenses
    ]

@router.get("/financial-health")
def financial_health_insights(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Comprehensive financial insights.
    Uses FinancialEngine as source of truth.
    """

    health = FinancialEngine.calculate(
        db,
        current_user
    )

    # ----------------------------------
    # Top Spending Category
    # ----------------------------------

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

    top_category = None

    if expenses:
        top_category = max(
            expenses,
            key=lambda x: x.total
        )

    # ----------------------------------
    # Goal Statistics
    # ----------------------------------

    goals = (
        db.query(Goal)
        .filter(
            Goal.user_id == current_user.id
        )
        .all()
    )

    average_goal_progress = 0

    if goals:

        progress_values = []

        for goal in goals:

            if goal.target_amount > 0:

                progress_values.append(
                    (
                        goal.current_savings
                        / goal.target_amount
                    ) * 100
                )

        if progress_values:

            average_goal_progress = round(
                sum(progress_values)
                / len(progress_values),
                2
            )

    # ----------------------------------
    # Budget Breaches
    # ----------------------------------

    budget_breaches = []

    budgets = (
        db.query(Budget)
        .filter(
            Budget.user_id == current_user.id
        )
        .all()
    )

    for budget in budgets:

        spent = (
            db.query(func.sum(Expense.amount))
            .filter(
                Expense.user_id == current_user.id,
                Expense.category == budget.category
            )
            .scalar()
            or 0
        )

        if spent > budget.monthly_limit:

            budget_breaches.append({
                "category": budget.category,
                "limit": budget.monthly_limit,
                "spent": spent,
                "exceeded_by": round(
                    spent - budget.monthly_limit,
                    2
                )
            })

    # ----------------------------------
    # Most Active Wallet
    # ----------------------------------

    wallets = (
        db.query(Wallet)
        .filter(
            Wallet.user_id == current_user.id
        )
        .all()
    )

    most_active_wallet = None

    if wallets:

        wallet_activity = []

        for wallet in wallets:

            tx_count = (
                db.query(Transaction)
                .filter(
                    Transaction.wallet_id == wallet.id
                )
                .count()
            )

            wallet_activity.append(
                (wallet.name, tx_count)
            )

        most_active_wallet = max(
            wallet_activity,
            key=lambda x: x[1]
        )[0]

    return {
        "financial_health": {
            "financial_score":
                health["financial_score"],

            "grade":
                health["grade"],

            "health_status":
                health["health_status"]
        },

        "spending_insights": {
            "top_category":
                top_category.category
                if top_category else None,

            "amount":
                round(top_category.total, 2)
                if top_category else 0
        },

        "goal_insights": {
            "total_goals": len(goals),

            "active_goals": len(
                [g for g in goals if g.status == "active"]
            ),

            "achieved_goals": len(
                [g for g in goals if g.status == "achieved"]
            ),

            "average_progress":
                average_goal_progress
        },

        "wallet_insights": {
            "most_active_wallet":
                most_active_wallet
        },

        "score_breakdown":
            health["score_breakdown"],

        "budget_breaches":
            budget_breaches,

        "recommendations":
            health["recommendations"]
    }