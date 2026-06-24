from collections import defaultdict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from auth import get_db, get_current_user

from models import (
    User,
    Wallet,
    Goal,
    Transaction
)

from financial_engine import FinancialEngine
from ml_engine import ExpenseForecaster

router = APIRouter()


# ==================================================
# Summary Report
# ==================================================

@router.get("/summary")
def get_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    health = FinancialEngine.calculate(
        db,
        current_user
    )

    return {
        "total_income": health["income"],
        "total_expense": health["expense"],
        "wallet_balance": health["wallet_balance"],
        "net_savings":
            health["income"] - health["expense"],

        "financial_score":
            health["financial_score"],

        "grade":
            health["grade"],

        "health_status":
            health["health_status"]
    }


# ==================================================
# Financial Score Report
# ==================================================

@router.get("/score")
def financial_score_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return FinancialEngine.calculate(
        db,
        current_user
    )


# ==================================================
# Monthly Trend Report
# ==================================================

@router.get("/trend")
def get_trend(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    transactions = (
        db.query(Transaction)
        .filter(
            Transaction.user_id == current_user.id
        )
        .all()
    )

    monthly_data = defaultdict(
        lambda: {
            "income": 0,
            "expense": 0
        }
    )

    for tx in transactions:

        month = tx.date.strftime("%Y-%m")

        if tx.transaction_type == "income":
            monthly_data[month]["income"] += tx.amount

        elif tx.transaction_type == "expense":
            monthly_data[month]["expense"] += tx.amount

    result = []

    for month, values in monthly_data.items():

        result.append({
            "month": month,
            "income": round(
                values["income"],
                2
            ),
            "expense": round(
                values["expense"],
                2
            ),
            "savings": round(
                values["income"]
                - values["expense"],
                2
            )
        })

    return sorted(
        result,
        key=lambda x: x["month"]
    )


# ==================================================
# Goal Funding Report
# ==================================================

@router.get("/goal-funding")
def goal_funding_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    transactions = (
        db.query(Transaction)
        .filter(
            Transaction.user_id == current_user.id,
            Transaction.transaction_type == "goal_funding"
        )
        .order_by(Transaction.date.desc())
        .all()
    )

    return [
        {
            "date": tx.date,
            "amount": tx.amount,
            "description": tx.description
        }
        for tx in transactions
    ]


# ==================================================
# Wallet Transfer Report
# ==================================================

@router.get("/wallet-transfers")
def wallet_transfer_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    transfers = (
        db.query(Transaction)
        .filter(
            Transaction.user_id == current_user.id,
            Transaction.transaction_type == "wallet_transfer"
        )
        .order_by(Transaction.date.desc())
        .all()
    )

    return [
        {
            "date": tx.date,
            "amount": tx.amount,
            "description": tx.description,
            "from_wallet": tx.wallet_id,
            "to_wallet": tx.to_wallet_id
        }
        for tx in transfers
    ]


# ==================================================
# Export Complete Ledger
# ==================================================

@router.get("/export")
def export_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    transactions = (
        db.query(Transaction)
        .filter(
            Transaction.user_id == current_user.id
        )
        .order_by(Transaction.date.desc())
        .all()
    )

    return [
        {
            "date": tx.date,
            "type": tx.transaction_type,
            "category": tx.category,
            "amount": tx.amount,
            "description": tx.description
        }
        for tx in transactions
    ]


# ==================================================
# Expense Forecast
# ==================================================

@router.get("/forecast")
def get_forecast(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    forecaster = ExpenseForecaster(
        db,
        current_user.id
    )

    predictions = (
        forecaster.predict_next_days(days)
    )

    return {
        "forecast": predictions
    }