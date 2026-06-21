from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sklearn.ensemble import IsolationForest
import pandas as pd

from auth import get_db, get_current_user
from models import Expense, User

router = APIRouter()

@router.get("/detect")
def detect_anomalies(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    expenses = (
        db.query(Expense)
        .filter(Expense.user_id == current_user.id)
        .all()
    )

    if len(expenses) < 5:
        return {
            "message": "Need at least 5 expenses for anomaly detection"
        }

    amounts = [e.amount for e in expenses]

    df = pd.DataFrame(amounts, columns=["amount"])

    model = IsolationForest(
        contamination=0.1,
        random_state=42
    )

    df["anomaly"] = model.fit_predict(df)

    results = []

    for expense, anomaly in zip(expenses, df["anomaly"]):
        if anomaly == -1:
            results.append({
                "expense_id": expense.id,
                "amount": expense.amount,
                "category": expense.category,
                "anomaly": True
            })

    return {
        "anomalies": results
    }
