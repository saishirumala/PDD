from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas import UserResponse, UserGoalUpdate

router = APIRouter(prefix="/profile", tags=["User Profile"])

@router.get("", response_model=UserResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("", response_model=UserResponse)
def update_profile(
    profile_data: UserGoalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if profile_data.name is not None:
        # Prevent completely blank name
        name_val = profile_data.name.strip()
        if not name_val:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Name cannot be left blank."
            )
        current_user.name = name_val

    if profile_data.calorie_goal is not None:
        current_user.calorie_goal = profile_data.calorie_goal

    if profile_data.protein_goal is not None:
        current_user.protein_goal = profile_data.protein_goal

    if profile_data.carbs_goal is not None:
        current_user.carbs_goal = profile_data.carbs_goal

    if profile_data.fat_goal is not None:
        current_user.fat_goal = profile_data.fat_goal

    if profile_data.fiber_goal is not None:
        current_user.fiber_goal = profile_data.fiber_goal

    try:
        db.add(current_user)
        db.commit()
        db.refresh(current_user)
        return current_user
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile targets: {str(e)}"
        )
