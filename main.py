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
<<<<<<< HEAD
from fastapi.middleware.cors import CORSMiddleware
from dashboard import router as dashboard_router
=======
>>>>>>> 1f644a86d8fc830f3a1f4390faee4beb1f3fb0d9

# Initialize database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="WiseMoney Backend",
    description="API for user authentication and finance tracking",
    version="1.0.0"
)

<<<<<<< HEAD
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

=======
>>>>>>> 1f644a86d8fc830f3a1f4390faee4beb1f3fb0d9
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

<<<<<<< HEAD
app.include_router(nlp_router, prefix="/nlp", tags=["NLP"])

app.include_router(
    dashboard_router,
    prefix="/dashboard",
    tags=["Dashboard"]
)

=======
app.include_router(nlp_router, prefix="/nlp", tags=["NLP"])
>>>>>>> 1f644a86d8fc830f3a1f4390faee4beb1f3fb0d9
