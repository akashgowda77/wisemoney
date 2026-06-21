from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database import Base

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
