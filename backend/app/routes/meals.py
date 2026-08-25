from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User, Meal
from app.schemas import MealResponse
from app.services.image_storage import get_storage_service

router = APIRouter(prefix="/meals", tags=["Meals Log"])

@router.get("", response_model=List[MealResponse])
def get_user_meals(
    search: Optional[str] = Query(None, description="Search meals by name or description"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Meal).filter(Meal.user_id == current_user.id)
    
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Meal.meal_name.ilike(search_filter)) | 
            (Meal.description.ilike(search_filter))
        )
        
    # Sort by creation date descending (most recent first)
    meals = query.order_by(Meal.created_at.desc()).all()
    return meals


@router.get("/{meal_id}", response_model=MealResponse)
def get_meal_details(
    meal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    meal = db.query(Meal).filter(Meal.id == meal_id).first()
    
    if not meal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal record not found."
        )
        
    if meal.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this meal record."
        )
        
    return meal


@router.delete("/{meal_id}", status_code=status.HTTP_200_OK)
async def delete_meal(
    meal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    meal = db.query(Meal).filter(Meal.id == meal_id).first()
    
    if not meal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal record not found."
        )
        
    if meal.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this meal record."
        )
        
    # Delete associated image if present
    if meal.image_url:
        try:
            storage_service = get_storage_service()
            await storage_service.delete(meal.image_url)
        except Exception as e:
            # Log error but don't prevent DB deletion
            print(f"Failed to delete image: {str(e)}")
            
    # Delete from database (cascade deletes related tables)
    try:
        db.delete(meal)
        db.commit()
        return {"detail": "Meal record deleted successfully."}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete meal: {str(e)}"
        )
