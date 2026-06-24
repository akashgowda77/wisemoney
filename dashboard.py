"""
WiseMoney Dashboard Module

Purpose:
Provides a complete financial overview of the user.

Features:
- Total Income
- Total Expense
- Wallet Balance
- Net Savings
- Goal Statistics
- Budget Statistics
- Financial Score
- Financial Health

Uses:
FinancialEngine as the single source of truth
for financial scoring and recommendations.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from auth import get_db, get_current_user
from models import (
    Transaction,
    Wallet,
    Goal,
    Budget,
    User
)

from financial_engine import FinancialEngine

router = APIRouter()


# ==================================================
# Dashboard Overview
# ==================================================

@router.get("/")
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Main dashboard endpoint.

    Returns:
    - Income
    - Expense
    - Wallet Balance
    - Savings
    - Goal Summary
    - Budget Summary
    - Financial Score
    - Grade
    - Health Status
    """

    # ----------------------------------
    # Total Income
    # ----------------------------------

    total_income = (
        db.query(func.sum(Transaction.amount))
        .filter(
            Transaction.user_id == current_user.id,
            Transaction.transaction_type == "income"
        )
        .scalar()
        or 0
    )

    # ----------------------------------
    # Total Expense
    # ----------------------------------

    total_expense = (
        db.query(func.sum(Transaction.amount))
        .filter(
            Transaction.user_id == current_user.id,
            Transaction.transaction_type == "expense"
        )
        .scalar()
        or 0
    )

    # ----------------------------------
    # Total Wallet Balance
    # ----------------------------------

    wallet_balance = (
        db.query(func.sum(Wallet.balance))
        .filter(
            Wallet.user_id == current_user.id
        )
        .scalar()
        or 0
    )

    # ----------------------------------
    # Goal Statistics
    # ----------------------------------

    active_goals = (
        db.query(Goal)
        .filter(
            Goal.user_id == current_user.id,
            Goal.status == "active"
        )
        .count()
    )

    achieved_goals = (
        db.query(Goal)
        .filter(
            Goal.user_id == current_user.id,
            Goal.status == "achieved"
        )
        .count()
    )

    total_goals = (
        db.query(Goal)
        .filter(
            Goal.user_id == current_user.id
        )
        .count()
    )

    # ----------------------------------
    # Budget Statistics
    # ----------------------------------

    total_budgets = (
        db.query(Budget)
        .filter(
            Budget.user_id == current_user.id
        )
        .count()
    )

    # ----------------------------------
    # Financial Health Engine
    # Single Source Of Truth
    # ----------------------------------

    financial_data = FinancialEngine.calculate(
        db,
        current_user
    )

    # ----------------------------------
    # Dashboard Response
    # ----------------------------------

    return {
        "financial_overview": {
            "total_income": round(total_income, 2),
            "total_expense": round(total_expense, 2),
            "wallet_balance": round(wallet_balance, 2),
            "net_savings": round(
                total_income - total_expense,
                2
            )
        },

        "goals": {
            "total_goals": total_goals,
            "active_goals": active_goals,
            "achieved_goals": achieved_goals
        },

        "budgets": {
            "total_budgets": total_budgets
        },

        "financial_health": {
            "financial_score": financial_data["financial_score"],
            "grade": financial_data["grade"],
            "health_status": financial_data["health_status"]
        }
    }


# ==================================================
# Financial Score Endpoint
# ==================================================

@router.get("/score")
def get_financial_score(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns complete financial score details.
    """

    return FinancialEngine.calculate(
        db,
        current_user
    )


# ==================================================
# Financial Health Endpoint
# ==================================================

@router.get("/health")
def get_financial_health(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns detailed financial health report.
    """

    health = FinancialEngine.calculate(
        db,
        current_user
    )

    return {
        "financial_score": health["financial_score"],
        "grade": health["grade"],
        "health_status": health["health_status"],

        "savings_ratio": health["savings_ratio"],
        "goal_progress": health["goal_progress"],

        "recommended_emergency_fund":
            health["recommended_emergency_fund"],

        "emergency_fund_completion":
            health["emergency_fund_completion"],

        "score_breakdown":
            health["score_breakdown"],

        "recommendations":
            health["recommendations"]
    }


# ==================================================
# Financial Snapshot
# ==================================================

@router.get("/snapshot")
def get_snapshot(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lightweight dashboard summary.

    Useful for:
    - Home Screen
    - Mobile App
    - Widgets
    - Quick Overview Cards
    """

    health = FinancialEngine.calculate(
        db,
        current_user
    )

    return {
        "total_balance": round(
            health["wallet_balance"],
            2
        ),

        "monthly_income": round(
            health["income"],
            2
        ),

        "monthly_expense": round(
            health["expense"],
            2
        ),

        "net_savings": round(
            health["income"] - health["expense"],
            2
        ),

        "financial_score":
            health["financial_score"],

        "grade":
            health["grade"],

        "health_status":
            health["health_status"]
    }