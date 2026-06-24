"""
WiseMoney - Budget Module (CRUD)

Purpose:
- Budget CRUD endpoints (create/list/get/update/delete)
- Computes current-month budget metrics:
  - current_spend
  - remaining_budget
  - utilization_percentage
- Computes metrics from Expense rows for the current month.

Mounted under /budget by budget.py wrapper.

Author: WiseMoney Team
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from datetime import datetime
from typing import List

from auth import get_db, get_current_user
from models import Budget, Expense, User

router = APIRouter()



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

    current_spend: float | None = None
    remaining_budget: float | None = None
    utilization_percentage: float | None = None

    class Config:
        from_attributes = True


def get_budget_for_user(db: Session, budget_id: int, user_id: int) -> Budget | None:
    return (
        db.query(Budget)
        .filter(Budget.id == budget_id, Budget.user_id == user_id)
        .first()
    )


def current_month_bounds():
    now = datetime.utcnow()
    start = datetime(now.year, now.month, 1)
    if now.month == 12:
        end = datetime(now.year + 1, 1, 1)
    else:
        end = datetime(now.year, now.month + 1, 1)
    return start, end


def compute_budget_metrics(db: Session, budget: Budget):
    """Compute budget utilization metrics for a single budget.

    Purpose:
    Provide the core calculations used by Budget CRUD endpoints.

    Calculation Model (current-month):
    - current_spend = SUM(Expense.amount) for the budget.category
      filtered to the current month date range.
    - remaining_budget = max(0, monthly_limit - current_spend)
    - utilization_percentage:
        if monthly_limit > 0:
            min(100, (current_spend / monthly_limit) * 100)
        else:
            0

    Inputs:
        db: SQLAlchemy session
        budget: Budget row owned by current user

    Outputs:
        (current_spend, remaining_budget, utilization_percentage)
    """

    start, end = current_month_bounds()


    current_spend = (
        db.query(func.sum(Expense.amount))
        .filter(
            Expense.user_id == budget.user_id,
            Expense.category == budget.category,
            Expense.date >= start,
            Expense.date < end,
        )
        .scalar()
        or 0
    )

    remaining_budget = max(0.0, float(budget.monthly_limit) - float(current_spend))

    utilization_percentage = 0.0
    if budget.monthly_limit and budget.monthly_limit > 0:
        utilization_percentage = min(100.0, (float(current_spend) / float(budget.monthly_limit)) * 100)

    if utilization_percentage <= 70:
        health = "Excellent"
    elif utilization_percentage <= 90:
        health = "Good"
    elif utilization_percentage <= 100:
        health = "Warning"
    else:
        health = "Breached"
        
    return (
    float(current_spend),
    float(remaining_budget),
    float(utilization_percentage),
    health
    )


@router.post("/", response_model=BudgetResponse)
def create_budget(
    payload: BudgetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    category = (payload.category or "").strip().title()
    if not category:
        raise HTTPException(status_code=400, detail="Category is required")

    if payload.monthly_limit is None or payload.monthly_limit <= 0:
        raise HTTPException(status_code=400, detail="monthly_limit must be > 0")

    dup = db.query(Budget).filter(
        Budget.user_id == current_user.id,
        Budget.category == category,
    ).first()

    if dup:
        raise HTTPException(status_code=400, detail="Budget category already exists for this user")

    budget = Budget(
        user_id=current_user.id,
        category=category,
        monthly_limit=float(payload.monthly_limit),
    )
    db.add(budget)
    db.commit()
    db.refresh(budget)

    current_spend, remaining_budget, utilization_percentage = compute_budget_metrics(db, budget)
    return BudgetResponse(
        id=budget.id,
        user_id=budget.user_id,
        category=budget.category,
        monthly_limit=budget.monthly_limit,
        created_at=budget.created_at,
        current_spend=current_spend,
        remaining_budget=remaining_budget,
        utilization_percentage=utilization_percentage,
    )


@router.get("/", response_model=List[BudgetResponse])
def list_budgets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    budgets = db.query(Budget).filter(Budget.user_id == current_user.id).all()
    result = []
    for b in budgets:
        current_spend, remaining_budget, utilization_percentage = compute_budget_metrics(db, b)
        result.append(
            BudgetResponse(
                id=b.id,
                user_id=b.user_id,
                category=b.category,
                monthly_limit=b.monthly_limit,
                created_at=b.created_at,
                current_spend=current_spend,
                remaining_budget=remaining_budget,
                utilization_percentage=utilization_percentage,
            )
        )
    return result


@router.get("/summary")
def budget_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    budgets = db.query(Budget).filter(Budget.user_id == current_user.id).all()

    total_budget = sum(float(b.monthly_limit) for b in budgets)

    categories = []
    total_spent = 0.0
    for b in budgets:
        current_spend, remaining_budget, utilization_percentage = compute_budget_metrics(db, b)
        total_spent += float(current_spend)
        categories.append(
            {
                "budget_id": b.id,
                "category": b.category,
                "monthly_limit": float(b.monthly_limit),
                "current_spend": current_spend,
                "remaining_budget": remaining_budget,
                "utilization_percentage": utilization_percentage,
            }
        )

    remaining_budget = max(0.0, total_budget - total_spent)
    utilization_percentage = 0.0
    if total_budget > 0:
        utilization_percentage = min(100.0, (total_spent / total_budget) * 100)

    return {
        "total_budget": float(total_budget),
        "total_spent": float(total_spent),
        "remaining_budget": float(remaining_budget),
        "utilization_percentage": float(utilization_percentage),
        "categories": categories,
    }


@router.get("/{budget_id}", response_model=BudgetResponse)
def get_budget(
    budget_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    budget = get_budget_for_user(db, budget_id, current_user.id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")

    current_spend, remaining_budget, utilization_percentage = compute_budget_metrics(db, budget)
    return BudgetResponse(
        id=budget.id,
        user_id=budget.user_id,
        category=budget.category,
        monthly_limit=budget.monthly_limit,
        created_at=budget.created_at,
        current_spend=current_spend,
        remaining_budget=remaining_budget,
        utilization_percentage=utilization_percentage,
    )


@router.put("/{budget_id}", response_model=BudgetResponse)
def update_budget(
    budget_id: int,
    payload: BudgetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    budget = get_budget_for_user(db, budget_id, current_user.id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")

    if payload.category is not None:
        new_cat = payload.category.strip().title()
        if not new_cat:
            raise HTTPException(status_code=400, detail="category cannot be empty")
        # duplicate prevention
        dup = db.query(Budget).filter(
            Budget.user_id == current_user.id,
            Budget.category == new_cat,
            Budget.id != budget_id,
        ).first()
        if dup:
            raise HTTPException(status_code=400, detail="Budget category already exists for this user")
        budget.category = new_cat

    if payload.monthly_limit is not None:
        if payload.monthly_limit <= 0:
            raise HTTPException(status_code=400, detail="monthly_limit must be > 0")
        budget.monthly_limit = float(payload.monthly_limit)

    db.add(budget)
    db.commit()
    db.refresh(budget)

    current_spend, remaining_budget, utilization_percentage = compute_budget_metrics(db, budget)
    return BudgetResponse(
        id=budget.id,
        user_id=budget.user_id,
        category=budget.category,
        monthly_limit=budget.monthly_limit,
        created_at=budget.created_at,
        current_spend=current_spend,
        remaining_budget=remaining_budget,
        utilization_percentage=utilization_percentage,
    )


@router.delete("/{budget_id}")
def delete_budget(
    budget_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    budget = get_budget_for_user(db, budget_id, current_user.id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")

    db.delete(budget)
    db.commit()

    return {"message": "Budget deleted successfully"}

@router.get("/breaches")
def budget_breaches(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    budgets = (
        db.query(Budget)
        .filter(Budget.user_id == current_user.id)
        .all()
    )

    breaches = []

    for budget in budgets:
        current_spend, _, _ = compute_budget_metrics(db, budget)

        if current_spend > budget.monthly_limit:
            breaches.append({
                "category": budget.category,
                "limit": budget.monthly_limit,
                "spent": current_spend,
                "exceeded_by": round(
                    current_spend - budget.monthly_limit,
                    2
                )
            })

    return breaches