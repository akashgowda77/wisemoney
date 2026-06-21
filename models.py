from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from database import Base

from datetime import datetime

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)

    amount = Column(Float, nullable=False)

    transaction_type = Column(
        String,
        nullable=False
    )  # income | expense

    category = Column(
        String,
        nullable=True
    )

    description = Column(
        String,
        nullable=True
    )

    date = Column(
        DateTime,
        default=datetime.utcnow
    )

    wallet_id = Column(
        Integer,
        ForeignKey("wallets.id")
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    is_active = Column(Boolean, default=True)
    incomes = relationship("Income", back_populates="user")
    expenses = relationship("Expense", back_populates="user")
    wallets = relationship("Wallet", back_populates="user")

class Wallet(Base):
    __tablename__ = "wallets"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)
    balance = Column(Float, default=0)
    user = relationship("User", back_populates="wallets")
    incomes = relationship("Income", back_populates="wallet")
    expenses = relationship("Expense", back_populates="wallet")

class Income(Base):
    __tablename__ = "incomes"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    wallet_id = Column(Integer, ForeignKey("wallets.id"), nullable=True)
    source = Column(String)
    amount = Column(Float)
    date = Column(Date)
    user = relationship("User", back_populates="incomes")
    wallet = relationship("Wallet", back_populates="incomes")

class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    wallet_id = Column(Integer, ForeignKey("wallets.id"), nullable=True)
    category = Column(String)
    amount = Column(Float)
    date = Column(Date)
    user = relationship("User", back_populates="expenses")
    wallet = relationship("Wallet", back_populates="expenses")

class Goal(Base):
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True, index=True)
    goal_name = Column(String, nullable=False)
    target_amount = Column(Float, nullable=False)
    current_savings = Column(Float, default=0)
    target_date = Column(DateTime, nullable=True)

    user_id = Column(Integer, ForeignKey("users.id"))