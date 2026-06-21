from fastapi import APIRouter, Depends
from pydantic import BaseModel

router = APIRouter()

class GoalRequest(BaseModel):
    goal_name: str
    target_amount: float
    current_savings: float
    monthly_saving_capacity: float

@router.post("/planner")
def savings_planner(goal: GoalRequest):

    remaining = goal.target_amount - goal.current_savings

    if remaining <= 0:
        return {
            "goal": goal.goal_name,
            "status": "Achieved"
        }

    months = remaining / goal.monthly_saving_capacity

    return {
        "goal": goal.goal_name,
        "target_amount": goal.target_amount,
        "current_savings": goal.current_savings,
        "remaining_amount": remaining,
        "estimated_months": round(months, 1)
    }