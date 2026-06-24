
"""
WiseMoney Backend Application

Purpose:
Main entry point of the WiseMoney Fintech Platform.

Responsibilities:
- Initialize database
- Configure middleware
- Register API routes
- Start FastAPI application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine

# Models
from models import (
    User,
    Income,
    Expense,
    Wallet,
    Goal,
    Transaction
)

# Routers
from auth import router as auth_router
from income import router as income_router
from expense import router as expense_router
from wallet import router as wallet_router
from report import router as report_router
from nlp_engine import router as nlp_router
from dashboard import router as dashboard_router
from budget import router as budget_router
from anomaly import router as anomaly_router
from insights import router as insights_router
from goals import router as goals_router
from advisor import router as advisor_router
from transaction import router as transaction_router


# --------------------------------------------------
# Create database tables if they do not exist
# --------------------------------------------------
Base.metadata.create_all(bind=engine)


# --------------------------------------------------
# FastAPI Application
# --------------------------------------------------
app = FastAPI(
    title="WiseMoney Backend",
    description="Personal Finance Management and Analytics Platform",
    version="1.0.0"
)


# --------------------------------------------------
# CORS Configuration
#
# Allows frontend applications running on
# local development servers to access APIs.
# --------------------------------------------------
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


# --------------------------------------------------
# Health Check Endpoint
#
# Used to verify backend availability.
# --------------------------------------------------
@app.get("/")
def root():
    return {
        "message": "WiseMoney Backend Running"
    }


# --------------------------------------------------
# Authentication Module
# User Registration & Login
# --------------------------------------------------
app.include_router(
    auth_router,
    prefix="/auth",
    tags=["Authentication"]
)


# --------------------------------------------------
# Income Management
# --------------------------------------------------
app.include_router(
    income_router,
    prefix="/income",
    tags=["Income"]
)


# --------------------------------------------------
# Expense Management
# --------------------------------------------------
app.include_router(
    expense_router,
    prefix="/expense",
    tags=["Expense"]
)


# --------------------------------------------------
# Wallet Management
# --------------------------------------------------
app.include_router(
    wallet_router,
    prefix="/wallet",
    tags=["Wallet"]
)


# --------------------------------------------------
# Financial Reports & Forecasting
# --------------------------------------------------
app.include_router(
    report_router,
    prefix="/report",
    tags=["Report"]
)


# --------------------------------------------------
# Natural Language Processing Module
# --------------------------------------------------
app.include_router(
    nlp_router,
    prefix="/nlp",
    tags=["NLP"]
)


# --------------------------------------------------
# Dashboard Analytics
# --------------------------------------------------
app.include_router(
    dashboard_router,
    prefix="/dashboard",
    tags=["Dashboard"]
)


# --------------------------------------------------
# Budget Planning Module
# --------------------------------------------------
app.include_router(
    budget_router,
    prefix="/budget",
    tags=["Budget"]
)


# --------------------------------------------------
# Anomaly Detection
#
# Identifies unusual spending patterns.
# --------------------------------------------------
app.include_router(
    anomaly_router,
    prefix="/anomaly",
    tags=["Anomaly Detection"]
)


# --------------------------------------------------
# Financial Insights Engine
# --------------------------------------------------
app.include_router(
    insights_router,
    prefix="/insights",
    tags=["AI Insights"]
)


# --------------------------------------------------
# Goal Tracking Module
# --------------------------------------------------
app.include_router(
    goals_router,
    prefix="/goals",
    tags=["Goal Tracking"]
)


# --------------------------------------------------
# AI Financial Advisor
# --------------------------------------------------
app.include_router(
    advisor_router,
    prefix="/advisor",
    tags=["AI Financial Advisor"]
)


# --------------------------------------------------
# Transaction Ledger
#
# Central financial audit trail used by
# reports, insights, dashboards and analytics.
# --------------------------------------------------
app.include_router(
    transaction_router,
    prefix="/transactions",
    tags=["Transactions"]
)
