from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime

# --- Token Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[str] = None


# --- User Schemas ---
class UserBase(BaseModel):
    email: EmailStr
    name: str

class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserGoalUpdate(BaseModel):
    name: Optional[str] = None
    calorie_goal: Optional[int] = Field(None, ge=500, le=10000)
    protein_goal: Optional[float] = Field(None, ge=0)
    carbs_goal: Optional[float] = Field(None, ge=0)
    fat_goal: Optional[float] = Field(None, ge=0)
    fiber_goal: Optional[float] = Field(None, ge=0)

class UserResponse(UserBase):
    id: int
    calorie_goal: int
    protein_goal: float
    carbs_goal: float
    fat_goal: float
    fiber_goal: float
    created_at: datetime

    class Config:
        from_attributes = True


# --- Food Schemas ---
class FoodBase(BaseModel):
    name: str
    estimated_quantity: str
    calories: int
    protein: float
    carbohydrates: float
    fat: float

class FoodCreate(FoodBase):
    pass

class FoodResponse(FoodBase):
    id: int
    meal_id: int

    class Config:
        from_attributes = True


# --- Nutrition Schemas ---
class NutritionBase(BaseModel):
    calories: int
    protein: float
    carbohydrates: float
    fat: float
    fiber: float
    sugar: float
    sodium: float

class NutritionCreate(NutritionBase):
    pass

class NutritionResponse(NutritionBase):
    id: int
    meal_id: int

    class Config:
        from_attributes = True


# --- Micronutrient Schemas ---
class MicronutrientBase(BaseModel):
    iron: float
    calcium: float
    magnesium: float
    potassium: float
    vitamin_a: float
    vitamin_c: float
    vitamin_d: float
    vitamin_b12: float

class MicronutrientCreate(MicronutrientBase):
    pass

class MicronutrientResponse(MicronutrientBase):
    id: int
    meal_id: int

    class Config:
        from_attributes = True


# --- MealInsight Schemas ---
class MealInsightBase(BaseModel):
    health_score: int
    summary: str
    recommendations: List[str]

class MealInsightCreate(MealInsightBase):
    pass

class MealInsightResponse(MealInsightBase):
    id: int
    meal_id: int

    class Config:
        from_attributes = True


# --- Meal Schemas ---
class MealBase(BaseModel):
    meal_name: str
    description: Optional[str] = None
    image_url: Optional[str] = None

class MealCreate(BaseModel):
    meal_name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    nutrition: NutritionCreate
    micronutrients: MicronutrientCreate
    foods: List[FoodCreate]
    insight: MealInsightCreate

class MealResponse(MealBase):
    id: int
    user_id: int
    analyzed_at: datetime
    created_at: datetime
    nutrition: Optional[NutritionResponse] = None
    micronutrients: Optional[MicronutrientResponse] = None
    foods: List[FoodResponse] = []
    insight: Optional[MealInsightResponse] = None

    class Config:
        from_attributes = True


# --- AI Nutrition Raw Analysis Schema ---
# This is the exact schema returned by the AI provider
class AIFoodItem(BaseModel):
    name: str = Field(description="Name of the food item")
    estimated_quantity: str = Field(description="Serving size or weight, e.g. '150 g', '1 medium banana'")
    calories: int = Field(description="Calories in this food portion")
    protein: float = Field(description="Protein in grams")
    carbohydrates: float = Field(description="Carbohydrates in grams")
    fat: float = Field(description="Fat in grams")

class AINutritionTotals(BaseModel):
    calories: int
    protein: float
    carbohydrates: float
    fat: float
    fiber: float
    sugar: float
    sodium: float

class AIMicronutrients(BaseModel):
    iron: float = Field(description="Iron in mg")
    calcium: float = Field(description="Calcium in mg")
    magnesium: float = Field(description="Magnesium in mg")
    potassium: float = Field(description="Potassium in mg")
    vitamin_a: float = Field(description="Vitamin A in mcg RAE")
    vitamin_c: float = Field(description="Vitamin C in mg")
    vitamin_d: float = Field(description="Vitamin D in mcg")
    vitamin_b12: float = Field(description="Vitamin B12 in mcg")

class AIAnalysisResult(BaseModel):
    meal_name: str
    foods: List[AIFoodItem]
    nutrition: AINutritionTotals
    micronutrients: AIMicronutrients
    health_score: int = Field(description="Healthiness rating from 0 to 100")
    summary: str = Field(description="Brief health profile paragraph")
    insights: List[str] = Field(description="Bullet points of nutritional feedback")


# --- Dashboard Summary Schemas ---
class DailyNutritionSummary(BaseModel):
    calories: int
    protein: float
    carbohydrates: float
    fat: float
    fiber: float
    calorie_goal: int
    protein_goal: float
    carbs_goal: float
    fat_goal: float
    fiber_goal: float

class DashboardSummaryResponse(BaseModel):
    today: DailyNutritionSummary
    meals_count: int
    average_health_score: float
    meals: List[MealResponse]


# --- Water Log Schemas ---
class WaterLogCreate(BaseModel):
    amount_ml: int = Field(..., ge=1, le=10000, description="Amount of water logged in milliliters")

class WaterLogResponse(BaseModel):
    id: int
    user_id: int
    amount_ml: int
    logged_at: datetime

    class Config:
        from_attributes = True

class WaterSummaryResponse(BaseModel):
    total_ml: int
    goal_ml: int
    logs: List[WaterLogResponse]
