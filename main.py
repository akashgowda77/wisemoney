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

# Initialize database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="WiseMoney Backend",
    description="API for user authentication and finance tracking",
    version="1.0.0"
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