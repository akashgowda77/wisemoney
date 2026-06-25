"""
WiseMoney Budget CRUD Module

Handles:
- Create Budget
- List Budgets
- Budget Summary
- Budget Breaches
- Get Budget
- Update Budget
- Delete Budget

Mounted by budget.py
"""

from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel,Field
from sqlalchemy import func
from sqlalchemy.orm import Session

from auth import get_db, get_current_user
from models import Budget, Expense, User

router = APIRouter()

# ============================================================
# Schemas
# ============================================================

class BudgetCreate(BaseModel):
    category: str
    monthly_limit: float


class BudgetUpdate(BaseModel):
    category: str | None = None
    monthly_limit: float | None = None


class BudgetResponse(BaseModel):

    id: int
    user_id: int

    category: str
    monthly_limit: float

    created_at: datetime

    current_spend: float
    remaining_budget: float
    utilization_percentage: float

    class Config:
        from_attributes = True

class ExpenseCreate(BaseModel):
    amount: float
    category: str
    date: datetime = Field(default_factory=datetime.utcnow)
    wallet_id: int | None = None


# ============================================================
# Helpers
# ============================================================

def month_range():

    now = datetime.utcnow()

    start = datetime(
        now.year,
        now.month,
        1
    )

    if now.month == 12:

        end = datetime(
            now.year + 1,
            1,
            1
        )

    else:

        end = datetime(
            now.year,
            now.month + 1,
            1
        )

    return start, end


def calculate_metrics(
    db: Session,
    budget: Budget
):

    start, end = month_range()

    spent = (

        db.query(
            func.sum(Expense.amount)
        )

        .filter(

            Expense.user_id == budget.user_id,

            func.lower(Expense.category) == func.lower(budget.category),

            Expense.date >= start,

            Expense.date < end

        )

        .scalar()

        or 0

    )

    remaining = max(
        0,
        budget.monthly_limit - spent
    )

    utilization = 0

    if budget.monthly_limit > 0:

        utilization = round(

            (spent / budget.monthly_limit) * 100,

            2

        )

    return (

        float(spent),

        float(remaining),

        float(utilization)

    )


def get_budget(

    db: Session,

    budget_id: int,

    user_id: int

):

    return (

        db.query(Budget)

        .filter(

            Budget.id == budget_id,

            Budget.user_id == user_id

        )

        .first()

    )
# ============================================================
# Create Budget
# ============================================================

@router.post(
    "/",
    response_model=BudgetResponse
)
def create_budget(

    payload: BudgetCreate,

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)

):

    category = payload.category.strip().title()

    if not category:

        raise HTTPException(
            status_code=400,
            detail="Category is required."
        )

    if payload.monthly_limit <= 0:

        raise HTTPException(
            status_code=400,
            detail="Monthly limit must be greater than zero."
        )

    duplicate = (

        db.query(Budget)

        .filter(

            Budget.user_id == current_user.id,

            Budget.category == category

        )

        .first()

    )

    if duplicate:

        raise HTTPException(
            status_code=400,
            detail="Budget already exists for this category."
        )

    budget = Budget(

        user_id=current_user.id,

        category=category,

        monthly_limit=float(payload.monthly_limit)

    )

    db.add(budget)

    db.commit()

    db.refresh(budget)

    spent, remaining, utilization = calculate_metrics(
        db,
        budget
    )

    return BudgetResponse(

        id=budget.id,

        user_id=budget.user_id,

        category=budget.category,

        monthly_limit=budget.monthly_limit,

        created_at=budget.created_at,

        current_spend=spent,

        remaining_budget=remaining,

        utilization_percentage=utilization

    )


# ============================================================
# List Budgets
# ============================================================

@router.get(
    "/",
    response_model=List[BudgetResponse]
)
def list_budgets(

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)

):

    budgets = (

        db.query(Budget)

        .filter(
            Budget.user_id == current_user.id
        )

        .order_by(Budget.category)

        .all()

    )

    result = []

    for budget in budgets:

        spent, remaining, utilization = calculate_metrics(
            db,
            budget
        )

        result.append(

            BudgetResponse(

                id=budget.id,

                user_id=budget.user_id,

                category=budget.category,

                monthly_limit=budget.monthly_limit,

                created_at=budget.created_at,

                current_spend=spent,

                remaining_budget=remaining,

                utilization_percentage=utilization

            )

        )

    return result


# ============================================================
# Budget Summary
# ============================================================

@router.get("/summary")
def budget_summary(

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)

):

    budgets = (

        db.query(Budget)

        .filter(
            Budget.user_id == current_user.id
        )

        .all()

    )

    total_budget = 0.0
    total_spent = 0.0

    categories = []

    for budget in budgets:

        spent, remaining, utilization = calculate_metrics(
            db,
            budget
        )

        total_budget += float(budget.monthly_limit)
        total_spent += spent

        categories.append({

            "budget_id": budget.id,

            "category": budget.category,

            "monthly_limit": float(
                budget.monthly_limit
            ),

            "current_spend": spent,

            "remaining_budget": remaining,

            "utilization_percentage": utilization

        })

    remaining_budget = max(
        0,
        total_budget - total_spent
    )

    utilization = 0

    if total_budget > 0:

        utilization = round(

            (total_spent / total_budget) * 100,

            2

        )

    return {

        "total_budget": round(
            total_budget,
            2
        ),

        "total_spent": round(
            total_spent,
            2
        ),

        "remaining_budget": round(
            remaining_budget,
            2
        ),

        "utilization_percentage": utilization,

        "categories": categories

    }
# ============================================================
# Budget Breaches
# IMPORTANT: Keep BEFORE /{budget_id}
# ============================================================

@router.get("/breaches")
def budget_breaches(

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)

):

    budgets = (

        db.query(Budget)

        .filter(
            Budget.user_id == current_user.id
        )

        .all()

    )

    breaches = []

    for budget in budgets:

        spent, remaining, utilization = calculate_metrics(
            db,
            budget
        )

        if spent > budget.monthly_limit:

            breaches.append({

                "budget_id": budget.id,

                "category": budget.category,

                "limit": round(
                    budget.monthly_limit,
                    2
                ),

                "spent": round(
                    spent,
                    2
                ),

                "remaining_budget": round(
                    remaining,
                    2
                ),

                "utilization_percentage": round(
                    utilization,
                    2
                ),

                "exceeded_by": round(
                    spent - budget.monthly_limit,
                    2
                )

            })

    return breaches


# ============================================================
# Get Budget By ID
# ============================================================

@router.get(
    "/{budget_id}",
    response_model=BudgetResponse
)
def get_budget_by_id(

    budget_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)

):

    budget = get_budget(
        db,
        budget_id,
        current_user.id
    )

    if not budget:

        raise HTTPException(
            status_code=404,
            detail="Budget not found."
        )

    spent, remaining, utilization = calculate_metrics(
        db,
        budget
    )

    return BudgetResponse(

        id=budget.id,

        user_id=budget.user_id,

        category=budget.category,

        monthly_limit=budget.monthly_limit,

        created_at=budget.created_at,

        current_spend=spent,

        remaining_budget=remaining,

        utilization_percentage=utilization

    )


# ============================================================
# Update Budget
# ============================================================

@router.put(
    "/{budget_id}",
    response_model=BudgetResponse
)
def update_budget(

    budget_id: int,

    payload: BudgetUpdate,

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)

):

    budget = get_budget(
        db,
        budget_id,
        current_user.id
    )

    if not budget:

        raise HTTPException(
            status_code=404,
            detail="Budget not found."
        )

    if payload.category is not None:

        category = payload.category.strip().title()

        duplicate = (

            db.query(Budget)

            .filter(

                Budget.user_id == current_user.id,

                Budget.category == category,

                Budget.id != budget.id

            )

            .first()

        )

        if duplicate:

            raise HTTPException(
                status_code=400,
                detail="Budget category already exists."
            )

        budget.category = category

    if payload.monthly_limit is not None:

        if payload.monthly_limit <= 0:

            raise HTTPException(
                status_code=400,
                detail="Monthly limit must be greater than zero."
            )

        budget.monthly_limit = float(
            payload.monthly_limit
        )

    db.commit()

    db.refresh(budget)

    spent, remaining, utilization = calculate_metrics(
        db,
        budget
    )

    return BudgetResponse(

        id=budget.id,

        user_id=budget.user_id,

        category=budget.category,

        monthly_limit=budget.monthly_limit,

        created_at=budget.created_at,

        current_spend=spent,

        remaining_budget=remaining,

        utilization_percentage=utilization

    )


# ============================================================
# Delete Budget
# ============================================================

@router.delete("/{budget_id}")
def delete_budget(

    budget_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)

):

    budget = get_budget(
        db,
        budget_id,
        current_user.id
    )

    if not budget:

        raise HTTPException(
            status_code=404,
            detail="Budget not found."
        )

    db.delete(budget)

    db.commit()

    return {

        "message": "Budget deleted successfully."

    }