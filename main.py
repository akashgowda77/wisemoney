from fastapi import FastAPI
from auth import router as auth_router
from database import Base, engine
from models import User, Income, Expense, Wallet
from income import router as income_router
from expense import router as expense_router
from wallet import router as wallet_router
from fastapi.security import OAuth2PasswordBearer
from report import router as report_router
from nlp_engine import router as nlp_router
from fastapi.middleware.cors import CORSMiddleware
from dashboard import router as dashboard_router
from budget import router as budget_router
from anomaly import router as anomaly_router
from insights import router as insights_router
from goals import router as goals_router
from advisor import router as advisor_router
from models import (
    User,
    Income,
    Expense,
    Wallet,
    Goal,
    Transaction
)
from transaction import router as transaction_router
# Initialize database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="WiseMoney Backend",
    description="API for user authentication and finance tracking",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root route
@app.get("/")
def root():
    return {"message": "Test server running"}

# Register authentication routes
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])

app.include_router(income_router, prefix="/income", tags=["Income"])

app.include_router(expense_router, prefix="/expense", tags=["Expense"])

app.include_router(wallet_router, prefix="/wallet", tags=["Wallet"])

app.include_router(report_router, prefix="/report", tags=["Report"])

app.include_router(nlp_router, prefix="/nlp", tags=["NLP"])

app.include_router(
    dashboard_router,
    prefix="/dashboard",
    tags=["Dashboard"]
)

app.include_router(
    budget_router,
    prefix="/budget",
    tags=["Budget"]
)

app.include_router(
    anomaly_router,
    prefix="/anomaly",
    tags=["Anomaly-Detection"]
)

app.include_router(
    insights_router,
    prefix="/insights",
    tags=["AI Insights"]
)

app.include_router(
    goals_router,
    prefix="/goals",
    tags=["Goal Tracking"]
)

app.include_router(
    advisor_router,
    prefix="/advisor",
    tags=["AI Financial Advisor"]
)

app.include_router(
    transaction_router,
    prefix="/transactions",
    tags=["Transactions"]
)