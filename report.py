from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import SessionLocal
from models import Income, Expense, Wallet, User
from auth import get_db, SECRET_KEY, ALGORITHM
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException

router = APIRouter()
# Get current user
from auth import get_current_user

# Total income, total expense, total balance across wallets
@router.get("/summary")
def get_summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    total_income = db.query(Income).filter(Income.user_id == current_user.id).with_entities(Income.amount).all()
    total_income = sum([i[0] for i in total_income])

    total_expense = db.query(Expense).filter(Expense.user_id == current_user.id).with_entities(Expense.amount).all()
    total_expense = sum([e[0] for e in total_expense])

    total_wallet_balance = db.query(Wallet).filter(Wallet.user_id == current_user.id).with_entities(Wallet.balance).all()
    total_wallet_balance = sum([w[0] for w in total_wallet_balance])

    expense_by_category = db.query(Expense.category, func.sum(Expense.amount)).filter(Expense.user_id == current_user.id).group_by(Expense.category).all()
    category_data = [{"category": c, "amount": a} for c, a in expense_by_category]

    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "total_wallet_balance": total_wallet_balance,
        "net_balance": total_wallet_balance, # Simple balance
        "expense_by_category": category_data
    }

from ml_engine import ExpenseForecaster

@router.get("/forecast")
def get_forecast(days: int = 30, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    forecaster = ExpenseForecaster(db, current_user.id)
    predictions = forecaster.predict_next_days(days)
    return {"forecast": predictions}

@router.get("/export")
def export_data(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    incomes = db.query(Income).filter(Income.user_id == current_user.id).all()
    expenses = db.query(Expense).filter(Expense.user_id == current_user.id).all()
    
    data = []
    for i in incomes:
        data.append({
            "date": i.date,
            "type": "Income",
            "category": i.source,
            "amount": i.amount
        })
    for e in expenses:
        data.append({
            "date": e.date,
            "type": "Expense",
            "category": e.category,
            "amount": e.amount
        })
    # Sort by date descending
    return sorted(data, key=lambda x: x['date'], reverse=True)

@router.get("/trend")
def get_trend(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Aggregate in Python for simplicity
    incomes = db.query(Income).filter(Income.user_id == current_user.id).all()
    expenses = db.query(Expense).filter(Expense.user_id == current_user.id).all()
    
    monthly_data = {}
    
    for i in incomes:
        month = i.date.strftime("%Y-%m")
        if month not in monthly_data: monthly_data[month] = {"income": 0, "expense": 0}
        monthly_data[month]["income"] += i.amount

    for e in expenses:
        month = e.date.strftime("%Y-%m")
        if month not in monthly_data: monthly_data[month] = {"income": 0, "expense": 0}
        monthly_data[month]["expense"] += e.amount
        
    result = [{"month": k, "income": v["income"], "expense": v["expense"]} for k,v in monthly_data.items()]
    return sorted(result, key=lambda x: x['month'])
