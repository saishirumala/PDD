from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from typing import Optional
import logging

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User, Meal, Nutrition, Micronutrient, Food, MealInsight
from app.schemas import MealResponse
from app.services.ai_provider import get_ai_provider
from app.services.image_storage import get_storage_service
from app.services.scoring import calculate_health_score

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/analyze", tags=["Meal Analysis"])

@router.post("", response_model=MealResponse, status_code=status.HTTP_201_CREATED)
async def analyze_meal_endpoint(
    description: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 1. Input validation: Must have at least description or image
    if not description and not image:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must provide either a meal description text or upload a food photograph."
        )

    image_url = None
    image_data = None
    mime_type = None

    # 2. Image upload handling & validation
    if image:
        storage_service = get_storage_service()
        
        # Read file contents to validate size
        file_bytes = await image.read()
        file_size = len(file_bytes)
        
        is_valid, err_msg = storage_service.validate_image(
            filename=image.filename,
            file_size=file_size,
            content_type=image.content_type
        )
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=err_msg
            )
            
        # Store for AI provider use
        image_data = file_bytes
        mime_type = image.content_type
        
        # Save image locally
        try:
            image_url = await storage_service.save(
                file_data=file_bytes,
                filename=image.filename,
                mime_type=image.content_type
            )
        except Exception as e:
            logger.error(f"Image storage failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save uploaded image."
            )

    # 3. Call AI provider
    try:
        ai_provider = get_ai_provider()
        ai_result = await ai_provider.analyze_meal(
            description=description,
            image_data=image_data,
            mime_type=mime_type
        )
    except Exception as e:
        logger.error(f"AI Provider analysis failed: {str(e)}")
        # If image was saved, try cleaning it up
        if image_url:
            await get_storage_service().delete(image_url)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI service analysis failed: {str(e)}"
        )

    # 4. Refine Health Score using our transparent scoring algorithm
    calculated_score = calculate_health_score(
        calories=ai_result.nutrition.calories,
        protein=ai_result.nutrition.protein,
        carbohydrates=ai_result.nutrition.carbohydrates,
        fat=ai_result.nutrition.fat,
        fiber=ai_result.nutrition.fiber,
        sugar=ai_result.nutrition.sugar,
        sodium=ai_result.nutrition.sodium
    )
    # Blend AI score and calculated score or rely on calculated score to enforce rules
    final_health_score = int((ai_result.health_score + calculated_score) / 2)

    # 5. Persist to PostgreSQL database
    try:
        # Create Meal row
        db_meal = Meal(
            user_id=current_user.id,
            meal_name=ai_result.meal_name,
            description=description,
            image_url=image_url
        )
        db.add(db_meal)
        db.flush() # Populate db_meal.id

        # Create Nutrition row
        db_nutrition = Nutrition(
            meal_id=db_meal.id,
            calories=ai_result.nutrition.calories,
            protein=ai_result.nutrition.protein,
            carbohydrates=ai_result.nutrition.carbohydrates,
            fat=ai_result.nutrition.fat,
            fiber=ai_result.nutrition.fiber,
            sugar=ai_result.nutrition.sugar,
            sodium=ai_result.nutrition.sodium
        )
        db.add(db_nutrition)

        # Create Micronutrients row
        db_micro = Micronutrient(
            meal_id=db_meal.id,
            iron=ai_result.micronutrients.iron,
            calcium=ai_result.micronutrients.calcium,
            magnesium=ai_result.micronutrients.magnesium,
            potassium=ai_result.micronutrients.potassium,
            vitamin_a=ai_result.micronutrients.vitamin_a,
            vitamin_c=ai_result.micronutrients.vitamin_c,
            vitamin_d=ai_result.micronutrients.vitamin_d,
            vitamin_b12=ai_result.micronutrients.vitamin_b12
        )
        db.add(db_micro)

        # Create Food items
        for food in ai_result.foods:
            db_food = Food(
                meal_id=db_meal.id,
                name=food.name,
                estimated_quantity=food.estimated_quantity,
                calories=food.calories,
                protein=food.protein,
                carbohydrates=food.carbohydrates,
                fat=food.fat
            )
            db.add(db_food)

        # Create Meal Insights row
        db_insight = MealInsight(
            meal_id=db_meal.id,
            health_score=final_health_score,
            summary=ai_result.summary,
            recommendations=ai_result.insights
        )
        db.add(db_insight)

        db.commit()
        db.refresh(db_meal)
        return db_meal

    except Exception as e:
        db.rollback()
        logger.error(f"Database transaction failed: {str(e)}")
        # Clean up image from disk on failure
        if image_url:
            await get_storage_service().delete(image_url)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to persist meal analysis to database: {str(e)}"
        )
