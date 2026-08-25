from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from datetime import datetime, time, timedelta
from typing import List, Dict, Any

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User, Meal
from app.schemas import DashboardSummaryResponse, DailyNutritionSummary

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/today", response_model=DashboardSummaryResponse)
def get_dashboard_today(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Calculate start and end of today in UTC
    now = datetime.utcnow()
    # Let's align with user's local day. For database, UTC is safe, but we can also use general date.
    # To be safe, we capture meals created since midnight UTC today.
    today_start = datetime.combine(now.date(), time.min)
    today_end = datetime.combine(now.date(), time.max)

    # Query all meals created today
    meals_today = db.query(Meal).filter(
        Meal.user_id == current_user.id,
        Meal.created_at >= today_start,
        Meal.created_at <= today_end
    ).all()

    # Aggregate nutrition totals
    total_calories = 0
    total_protein = 0.0
    total_carbohydrates = 0.0
    total_fat = 0.0
    total_fiber = 0.0

    scores_sum = 0
    meals_count = len(meals_today)

    for meal in meals_today:
        if meal.nutrition:
            total_calories += meal.nutrition.calories
            total_protein += meal.nutrition.protein
            total_carbohydrates += meal.nutrition.carbohydrates
            total_fat += meal.nutrition.fat
            total_fiber += meal.nutrition.fiber
        if meal.insight:
            scores_sum += meal.insight.health_score

    average_score = float(scores_sum / meals_count) if meals_count > 0 else 0.0

    summary_obj = DailyNutritionSummary(
        calories=total_calories,
        protein=round(total_protein, 1),
        carbohydrates=round(total_carbohydrates, 1),
        fat=round(total_fat, 1),
        fiber=round(total_fiber, 1),
        calorie_goal=current_user.calorie_goal,
        protein_goal=current_user.protein_goal,
        carbs_goal=current_user.carbs_goal,
        fat_goal=current_user.fat_goal,
        fiber_goal=current_user.fiber_goal
    )

    return DashboardSummaryResponse(
        today=summary_obj,
        meals_count=meals_count,
        average_health_score=round(average_score, 1),
        meals=meals_today
    )


@router.get("/summary")
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Provide weekly/monthly aggregate statistics for charts
    now = datetime.utcnow()
    seven_days_ago = now - timedelta(days=7)

    # Get meals from past 7 days
    meals_week = db.query(Meal).filter(
        Meal.user_id == current_user.id,
        Meal.created_at >= seven_days_ago
    ).order_by(Meal.created_at.asc()).all()

    # Group meals by day of week
    daily_stats: Dict[str, Dict[str, Any]] = {}
    for i in range(7):
        day = (now - timedelta(days=i)).strftime("%a") # e.g. Mon, Tue
        daily_stats[day] = {"calories": 0, "protein": 0.0, "carbs": 0.0, "fat": 0.0, "count": 0}

    for meal in meals_week:
        day_str = meal.created_at.strftime("%a")
        if day_str in daily_stats:
            daily_stats[day_str]["count"] += 1
            if meal.nutrition:
                daily_stats[day_str]["calories"] += meal.nutrition.calories
                daily_stats[day_str]["protein"] += meal.nutrition.protein
                daily_stats[day_str]["carbs"] += meal.nutrition.carbohydrates
                daily_stats[day_str]["fat"] += meal.nutrition.fat

    # Format list ordered chronologically (oldest day first)
    weekly_chart_data = []
    for i in reversed(range(7)):
        day = (now - timedelta(days=i)).strftime("%a")
        weekly_chart_data.append({
            "day": day,
            "calories": daily_stats[day]["calories"],
            "protein": round(daily_stats[day]["protein"], 1),
            "carbohydrates": round(daily_stats[day]["carbs"], 1),
            "fat": round(daily_stats[day]["fat"], 1),
            "meals_count": daily_stats[day]["count"]
        })

    # General totals
    total_meals_analyzed = db.query(Meal).filter(Meal.user_id == current_user.id).count()
    
    # Calculate average health score of all time
    all_meals = db.query(Meal).filter(Meal.user_id == current_user.id).all()
    all_time_score_sum = sum(m.insight.health_score for m in all_meals if m.insight)
    all_time_avg_score = float(all_time_score_sum / len(all_meals)) if len(all_meals) > 0 else 0.0

    return {
        "weekly_chart": weekly_chart_data,
        "total_meals": total_meals_analyzed,
        "average_health_score": round(all_time_avg_score, 1),
    }
