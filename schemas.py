# schemas.py
from pydantic import BaseModel
from typing import Optional

class IncomeCreate(BaseModel):
    amount: float
    source: str
    date: Optional[str] = None

class ExpenseCreate(BaseModel):
    amount: float
    category: str
    date: Optional[str] = None

class WalletCreate(BaseModel):
    name: str
    balance: float
