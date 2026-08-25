from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, time
from typing import List

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User, WaterLog
from app.schemas import WaterLogCreate, WaterLogResponse, WaterSummaryResponse

router = APIRouter(prefix="/water", tags=["Water Tracker"])

DEFAULT_WATER_GOAL = 2000  # 2 Liters (2000 ml)

@router.post("", response_model=WaterLogResponse, status_code=status.HTTP_201_CREATED)
def log_water(
    payload: WaterLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        water_log = WaterLog(
            user_id=current_user.id,
            amount_ml=payload.amount_ml
        )
        db.add(water_log)
        db.commit()
        db.refresh(water_log)
        return water_log
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to log water: {str(e)}"
        )


@router.get("/today", response_model=WaterSummaryResponse)
def get_water_today(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    now = datetime.utcnow()
    today_start = datetime.combine(now.date(), time.min)
    today_end = datetime.combine(now.date(), time.max)

    logs_today = db.query(WaterLog).filter(
        WaterLog.user_id == current_user.id,
        WaterLog.logged_at >= today_start,
        WaterLog.logged_at <= today_end
    ).order_by(WaterLog.logged_at.desc()).all()

    total_ml = sum(log.amount_ml for log in logs_today)

    return WaterSummaryResponse(
        total_ml=total_ml,
        goal_ml=DEFAULT_WATER_GOAL,
        logs=logs_today
    )


@router.delete("/{log_id}", status_code=status.HTTP_200_OK)
def delete_water_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    water_log = db.query(WaterLog).filter(WaterLog.id == log_id).first()

    if not water_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Water log entry not found."
        )

    if water_log.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this entry."
        )

    try:
        db.delete(water_log)
        db.commit()
        return {"detail": "Water log entry deleted successfully."}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete entry: {str(e)}"
        )
