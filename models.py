
"""
WiseMoney Data Models

Purpose:
Defines the core database structure for the WiseMoney
Personal Finance Management Platform.

Modules Supported:
- Authentication
- Wallet Management
- Income & Expense Tracking
- Transaction Ledger
- Goal Management
- Budget Planning
- AI Advisor
- Reports & Insights
"""

from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Date,
    DateTime,
    Boolean,
    ForeignKey
)

from sqlalchemy.orm import relationship

from database import Base


# ==================================================
# Transaction Ledger
# ==================================================

class Transaction(Base):
    """
    Central financial ledger.

    Every money movement should be recorded here.

    Supported Types:
    - income
    - expense
    - goal_funding
    - wallet_transfer
    """

    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)

    amount = Column(
        Float,
        nullable=False
    )

    transaction_type = Column(
        String,
        nullable=False
    )

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
    # Destination wallet used for wallet transfers
    to_wallet_id = Column(
        Integer,
        ForeignKey("wallets.id"),
        nullable=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    # Source wallet
    wallet = relationship(
        "Wallet",
        foreign_keys=[wallet_id],
        back_populates="transactions"
    )

    # Destination wallet
    to_wallet = relationship(
        "Wallet",
        foreign_keys=[to_wallet_id],
        back_populates="transactions"
    )

    user = relationship(
        "User",
        back_populates="transactions"
    )


# ==================================================
# User
# ==================================================

class User(Base):
    """
    Registered WiseMoney user.
    """

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(String)

    email = Column(
        String,
        unique=True,
        index=True
    )

    password_hash = Column(String)

    is_active = Column(
        Boolean,
        default=True
    )

    # Relationships
    incomes = relationship(
        "Income",
        back_populates="user"
    )

    expenses = relationship(
        "Expense",
        back_populates="user"
    )

    wallets = relationship(
        "Wallet",
        back_populates="user"
    )

    goals = relationship(
        "Goal",
        back_populates="user"
    )

    budgets = relationship(
        "Budget",
        back_populates="user"
    )

    transactions = relationship(
        "Transaction",
        back_populates="user"
    )


# ==================================================
# Wallet
# ==================================================

class Wallet(Base):
    """
    Stores user's money.

    Examples:
    - Main Wallet
    - Savings Account
    - Emergency Fund Wallet
    """

    __tablename__ = "wallets"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    name = Column(
        String,
        nullable=False
    )

    balance = Column(
        Float,
        default=0,
        nullable=False
    )

    user = relationship(
        "User",
        back_populates="wallets"
    )

    incomes = relationship(
        "Income",
        back_populates="wallet"
    )

    expenses = relationship(
        "Expense",
        back_populates="wallet"
    )

   # Transactions where wallet is source
    transactions = relationship(
        "Transaction",
        foreign_keys="Transaction.wallet_id",
        back_populates="wallet"
    )

    # Transactions where wallet is destination
    received_transfers = relationship(
        "Transaction",
        foreign_keys="Transaction.to_wallet_id",
        back_populates="to_wallet"
    )


# ==================================================
# Income
# ==================================================

class Income(Base):
    """
    Stores income entries.
    """

    __tablename__ = "incomes"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    wallet_id = Column(
        Integer,
        ForeignKey("wallets.id"),
        nullable=True
    )

    source = Column(String)

    amount = Column(
        Float,
        nullable=False
    )

    date = Column(Date)

    user = relationship(
        "User",
        back_populates="incomes"
    )

    wallet = relationship(
        "Wallet",
        back_populates="incomes"
    )


# ==================================================
# Expense
# ==================================================

class Expense(Base):
    """
    Stores expense entries.
    """

    __tablename__ = "expenses"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    wallet_id = Column(
        Integer,
        ForeignKey("wallets.id"),
        nullable=True
    )

    category = Column(String)

    amount = Column(
        Float,
        nullable=False
    )

    date = Column(Date)

    user = relationship(
        "User",
        back_populates="expenses"
    )

    wallet = relationship(
        "Wallet",
        back_populates="expenses"
    )


# ==================================================
# Goal Tracking
# ==================================================

class Goal(Base):
    """
    Financial savings goal.

    Status:
    - active
    - achieved
    - cancelled
    """

    __tablename__ = "goals"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    goal_name = Column(
        String,
        nullable=False
    )

    target_amount = Column(
        Float,
        nullable=False
    )

    current_savings = Column(
        Float,
        default=0,
        nullable=False
    )

    target_date = Column(
        DateTime,
        nullable=True
    )

    # Goal Priority
    # high | medium | low
    priority = Column(
        String,
        default="medium"
    )

    # User Notes
    notes = Column(
        String,
        nullable=True
    )

    # Goal Status
    # active | achieved | cancelled
    status = Column(
        String,
        default="active"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    achieved_at = Column(
        DateTime,
        nullable=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    user = relationship(
        "User",
        back_populates="goals"
    )


# ==================================================
# Budget Management
# ==================================================

class Budget(Base):
    """
    Monthly category budget.

    Examples:
    - Food
    - Travel
    - Shopping
    - Entertainment
    """

    __tablename__ = "budgets"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    category = Column(
        String,
        nullable=False
    )

    monthly_limit = Column(
        Float,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    user = relationship(
        "User",
        back_populates="budgets"
    )
