"""
WiseMoney Anomaly Detection Engine

Purpose:
Detect unusual spending behavior using
Machine Learning (Isolation Forest).

Features:
- Anomaly Detection
- Severity Classification
- Risk Score
- Explainable AI Insights
- Anomaly Summary
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sklearn.ensemble import IsolationForest
import pandas as pd

from auth import get_db, get_current_user

from models import (
    Expense,
    User
)

router = APIRouter()


# ==================================================
# Dynamic Contamination Helper (Standard Deviation)
# ==================================================

def get_dynamic_contamination(amounts: list) -> float:
    """
    Calculates dynamic contamination rate for Isolation Forest
    based on Standard Deviation (Z-score > 2.0).
    Prevents false positives when spending is consistent.
    """
    if not amounts or len(amounts) < 5:
        return 0.1

    s = pd.Series(amounts)
    mean_val = s.mean()
    std_val = s.std()

    if std_val == 0 or pd.isna(std_val):
        return 0.01  # All transactions identical, minimal anomaly rate

    # Count transactions exceeding 2 standard deviations above mean
    outliers_count = (s > (mean_val + 2 * std_val)).sum()
    calculated_rate = outliers_count / len(s)

    # Scikit-learn requires 0 < contamination <= 0.5
    return max(0.01, min(0.30, calculated_rate))


# ==================================================
# Detect Spending Anomalies
# ==================================================

@router.get("/detect")
def detect_anomalies(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Detect unusual expenses using
    Isolation Forest with Dynamic Contamination.
    """

    expenses = (
        db.query(Expense)
        .filter(
            Expense.user_id == current_user.id
        )
        .all()
    )

    if len(expenses) < 5:
        return {
            "message":
                "Need at least 5 expenses for anomaly detection"
        }

    amounts = [
        expense.amount
        for expense in expenses
    ]

    df = pd.DataFrame(
        amounts,
        columns=["amount"]
    )

    contamination_rate = get_dynamic_contamination(amounts)

    model = IsolationForest(
        contamination=contamination_rate,
        random_state=42
    )

    df["anomaly"] = model.fit_predict(df)

    average_expense = df["amount"].mean()

    results = []

    for expense, anomaly in zip(
        expenses,
        df["anomaly"]
    ):

        if anomaly == -1:

            # ----------------------------------
            # Severity Calculation
            # ----------------------------------

            if expense.amount >= average_expense * 3:

                severity = "High"
                risk_score = 95

            elif expense.amount >= average_expense * 2:

                severity = "Medium"
                risk_score = 75

            else:

                severity = "Low"
                risk_score = 55

            # ----------------------------------
            # Explainable AI Insight
            # ----------------------------------

            reason = (
                "Expense significantly exceeds "
                "your normal spending pattern."
            )

            results.append({
                "expense_id": expense.id,
                "amount": round(
                    expense.amount,
                    2
                ),
                "category": expense.category,
                "severity": severity,
                "risk_score": risk_score,
                "reason": reason,
                "anomaly": True
            })

    return {
        "total_expenses": len(expenses),
        "anomalies_detected": len(results),
        "anomalies": results
    }


# ==================================================
# Anomaly Summary
# ==================================================

@router.get("/summary")
def anomaly_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Provides anomaly overview for dashboard.
    """

    expenses = (
        db.query(Expense)
        .filter(
            Expense.user_id == current_user.id
        )
        .all()
    )

    if len(expenses) < 5:
        return {
            "message":
                "Need at least 5 expenses for anomaly detection"
        }

    amounts = [
        expense.amount
        for expense in expenses
    ]

    df = pd.DataFrame(
        amounts,
        columns=["amount"]
    )

    contamination_rate = get_dynamic_contamination(amounts)

    model = IsolationForest(
        contamination=contamination_rate,
        random_state=42
    )

    df["anomaly"] = model.fit_predict(df)

    anomaly_count = len(
        df[df["anomaly"] == -1]
    )

    anomaly_percentage = (
        anomaly_count / len(df)
    ) * 100

    # ----------------------------------
    # Risk Level
    # ----------------------------------

    if anomaly_percentage >= 20:

        risk_level = "High"

    elif anomaly_percentage >= 10:

        risk_level = "Medium"

    else:

        risk_level = "Low"

    return {
        "total_expenses": len(df),
        "anomalies_detected": anomaly_count,
        "anomaly_percentage": round(
            anomaly_percentage,
            2
        ),
        "risk_level": risk_level
    }


# ==================================================
# Largest Anomaly
# ==================================================

@router.get("/largest")
def largest_anomaly(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns highest anomalous expense.
    """

    expenses = (
        db.query(Expense)
        .filter(
            Expense.user_id == current_user.id
        )
        .all()
    )

    if len(expenses) < 5:
        return {
            "message":
                "Need at least 5 expenses for anomaly detection"
        }

    amounts = [
        expense.amount
        for expense in expenses
    ]

    df = pd.DataFrame(
        amounts,
        columns=["amount"]
    )

    contamination_rate = get_dynamic_contamination(amounts)

    model = IsolationForest(
        contamination=contamination_rate,
        random_state=42
    )

    df["anomaly"] = model.fit_predict(df)

    anomalies = []

    for expense, anomaly in zip(
        expenses,
        df["anomaly"]
    ):

        if anomaly == -1:

            anomalies.append(expense)

    if not anomalies:

        return {
            "message":
                "No anomalies detected"
        }

    largest = max(
        anomalies,
        key=lambda x: x.amount
    )

    return {
        "expense_id": largest.id,
        "category": largest.category,
        "amount": round(
            largest.amount,
            2
        ),
        "message":
            "Largest detected spending anomaly."
    }