from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from auth import get_db, get_current_user
from models import Goal, User

router = APIRouter()

class GoalCreate(BaseModel):
    goal_name: str
    target_amount: float
    current_savings: float = 0

class GoalResponse(BaseModel):
    id: int
    goal_name: str
    target_amount: float
    current_savings: float
    user_id: int

    class Config:
        from_attributes = True

# Create Goal
@router.post("/", response_model=GoalResponse)
def create_goal(
    goal: GoalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_goal = Goal(
        goal_name=goal.goal_name,
        target_amount=goal.target_amount,
        current_savings=goal.current_savings,
        user_id=current_user.id
    )

    db.add(new_goal)
    db.commit()
    db.refresh(new_goal)

    return new_goal

# Get All Goals
@router.get("/", response_model=List[GoalResponse])
def get_goals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Goal).filter(
        Goal.user_id == current_user.id
    ).all()

# Goal Progress
@router.get("/{goal_id}")
def goal_progress(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    goal = db.query(Goal).filter(
        Goal.id == goal_id,
        Goal.user_id == current_user.id
    ).first()

    if not goal:
        raise HTTPException(
            status_code=404,
            detail="Goal not found"
        )

    progress = (
        goal.current_savings / goal.target_amount
    ) * 100

    return {
        "goal": goal.goal_name,
        "target_amount": goal.target_amount,
        "current_savings": goal.current_savings,
        "progress_percentage": round(progress, 2)
    }