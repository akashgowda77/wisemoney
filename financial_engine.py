from sqlalchemy import func

from models import (
    Transaction,
    Wallet,
    Goal,
    Budget,
    Expense
)


class FinancialEngine:
    """
    Central financial scoring engine.

    Used by:
    - Dashboard
    - Advisor
    - Insights
    - Reports

    Score Range: 0 - 100
    """

    @staticmethod
    def calculate(db, current_user):

        # -------------------------
        # Income
        # -------------------------

        total_income = (
            db.query(func.sum(Transaction.amount))
            .filter(
                Transaction.user_id == current_user.id,
                Transaction.transaction_type == "income"
            )
            .scalar()
            or 0
        )

        # -------------------------
        # Expense
        # -------------------------

        total_expense = (
            db.query(func.sum(Transaction.amount))
            .filter(
                Transaction.user_id == current_user.id,
                Transaction.transaction_type == "expense"
            )
            .scalar()
            or 0
        )

        # -------------------------
        # Wallet Balance
        # -------------------------

        wallet_balance = (
            db.query(func.sum(Wallet.balance))
            .filter(
                Wallet.user_id == current_user.id
            )
            .scalar()
            or 0
        )

        # -------------------------
        # Savings Ratio (35 Points)
        # -------------------------

        savings_ratio = 0

        if total_income > 0:
            savings_ratio = (
                (total_income - total_expense)
                / total_income
            ) * 100

        savings_score = min(
            35,
            max(
                0,
                (savings_ratio / 100) * 35
            )
        )

        # -------------------------
        # Goal Progress (25 Points)
        # -------------------------

        goals = (
            db.query(Goal)
            .filter(
                Goal.user_id == current_user.id
            )
            .all()
        )

        goal_score = 0
        average_goal_progress = 0

        if goals:

            progress_values = []

            for goal in goals:

                if goal.target_amount > 0:
                    progress = min(
                        100,
                        (goal.current_savings / goal.target_amount) * 100
                    )
                else:
                    progress = 0

                progress_values.append(progress)

            average_goal_progress = (
                sum(progress_values)
                / len(progress_values)
            )

            goal_score = (
                average_goal_progress / 100
            ) * 25

        # -------------------------
        # Budget Discipline (20 Points)
        # -------------------------

        budgets = (
            db.query(Budget)
            .filter(
                Budget.user_id == current_user.id
            )
            .all()
        )

        budget_score = 20

        for budget in budgets:

            spent = (
                db.query(func.sum(Expense.amount))
                .filter(
                    Expense.user_id == current_user.id,
                    Expense.category == budget.category
                )
                .scalar()
                or 0
            )

            utilization = 0

            if budget.monthly_limit > 0:
                utilization = (
                    spent
                    / budget.monthly_limit
                ) * 100

            if utilization > 100:
                budget_score -= 5

        budget_score = max(
            0,
            budget_score
        )

        # -------------------------
        # Emergency Fund (15 Points)
        # -------------------------

        recommended_fund = total_expense * 6

        emergency_completion = 0

        if recommended_fund > 0:
            emergency_completion = min(
                100,
                (
                    wallet_balance
                    / recommended_fund
                ) * 100
            )

        emergency_score = (
            emergency_completion
            / 100
        ) * 15

        # -------------------------
        # Expense Control (5 Points)
        # -------------------------

        expense_ratio = 100

        if total_income > 0:
            expense_ratio = (
                total_expense
                / total_income
            ) * 100

        expense_control_score = max(
            0,
            (
                (100 - expense_ratio)
                / 100
            ) * 5
        )

        # -------------------------
        # Final Score
        # -------------------------

        financial_score = round(
            savings_score
            + goal_score
            + budget_score
            + emergency_score
            + expense_control_score
        )

        financial_score = min(
            100,
            max(0, financial_score)
        )

        # -------------------------
        # Grade
        # -------------------------

        if financial_score >= 90:
            grade = "A+"

        elif financial_score >= 80:
            grade = "A"

        elif financial_score >= 70:
            grade = "B"

        elif financial_score >= 60:
            grade = "C"

        elif financial_score >= 50:
            grade = "D"

        else:
            grade = "F"

        # -------------------------
        # FINANCIAL HEALTH SCORE 
        # -------------------------

        if financial_score >= 90:
            health_status = "Excellent"
        elif financial_score >= 75:
            health_status = "Healthy"
        elif financial_score >= 60:
            health_status = "Needs Improvement"
        else:
            health_status = "Critical"

        

        # -------------------------
        # Recommendations
        # -------------------------

        recommendations = []

        if savings_ratio < 20:
            recommendations.append(
                "Increase monthly savings rate."
            )

        if emergency_completion < 50:
            recommendations.append(
                "Build a stronger emergency fund."
            )

        if average_goal_progress < 50:
            recommendations.append(
                "Increase goal contributions."
            )

        if budget_score < 15:
            recommendations.append(
                "Review budget categories with overspending."
            )

        return {
            "financial_score": financial_score,
            "grade": grade,
            "health_status": health_status,

            "income": total_income,
            "expense": total_expense,
            "wallet_balance": wallet_balance,

            "savings_ratio": round(savings_ratio, 2),

            "goal_progress": round(
                average_goal_progress,
                2
            ),

            "recommended_emergency_fund": round(
                recommended_fund,
                2
            ),

            "emergency_fund_completion": round(
                emergency_completion,
                2
            ),

            "score_breakdown": {
                "savings_score": round(savings_score, 2),
                "goal_score": round(goal_score, 2),
                "budget_score": round(budget_score, 2),
                "emergency_score": round(emergency_score, 2),
                "expense_control_score": round(
                    expense_control_score,
                    2
                )
            },

            "recommendations": recommendations
        }

       