import os
import json
import re
import random
from typing import Optional, List, Dict, Any
from app.config import settings
from app.schemas import AIAnalysisResult, AIFoodItem, AINutritionTotals, AIMicronutrients
import google.generativeai as genai

class AIProvider:
    async def analyze_meal(
        self, 
        description: Optional[str] = None, 
        image_data: Optional[bytes] = None, 
        mime_type: Optional[str] = None
    ) -> AIAnalysisResult:
        raise NotImplementedError("analyze_meal must be implemented by subclasses")


class MockAIProvider(AIProvider):
    async def analyze_meal(
        self, 
        description: Optional[str] = None, 
        image_data: Optional[bytes] = None, 
        mime_type: Optional[str] = None
    ) -> AIAnalysisResult:
        desc = (description or "").lower()
        
        # Determine mock profile based on keywords
        if "chicken" in desc:
            meal_name = "Grilled Chicken Salad Bowl"
            foods = [
                AIFoodItem(name="Grilled Chicken Breast", estimated_quantity="150 g", calories=250, protein=46.0, carbohydrates=0.0, fat=6.0),
                AIFoodItem(name="Mixed Greens & Spinach", estimated_quantity="2 cups", calories=30, protein=2.0, carbohydrates=5.0, fat=0.2),
                AIFoodItem(name="Avocado slices", estimated_quantity="50 g", calories=80, protein=1.0, carbohydrates=4.2, fat=7.3),
                AIFoodItem(name="Olive Oil Vinaigrette", estimated_quantity="1 tbsp", calories=119, protein=0.0, carbohydrates=0.1, fat=13.5),
            ]
            nutrition = AINutritionTotals(calories=479, protein=49.0, carbohydrates=9.3, fat=27.0, fiber=5.2, sugar=1.5, sodium=420.0)
            micronutrients = AIMicronutrients(iron=3.2, calcium=85.0, magnesium=75.0, potassium=680.0, vitamin_a=320.0, vitamin_c=25.0, vitamin_d=0.0, vitamin_b12=0.6)
            health_score = 92
            summary = "A highly nutritious, protein-rich meal with good quality monounsaturated fats from avocado and key micronutrients."
            insights = [
                "Excellent source of lean protein for muscle repair and satiety.",
                "Healthy fats from avocado help absorb fat-soluble vitamins.",
                "Low in simple sugars, making it great for blood sugar control.",
                "Consider pairing with a whole grain like quinoa for additional fiber and complex carbs."
            ]
        elif "pizza" in desc:
            meal_name = "Pepperoni Pizza Slice"
            foods = [
                AIFoodItem(name="Pepperoni Pizza (Thin Crust)", estimated_quantity="2 slices (approx. 180g)", calories=580, protein=24.0, carbohydrates=64.0, fat=26.0),
                AIFoodItem(name="Extra Cheese Mozzarella", estimated_quantity="30 g", calories=90, protein=7.0, carbohydrates=1.0, fat=6.5)
            ]
            nutrition = AINutritionTotals(calories=670, protein=31.0, carbohydrates=65.0, fat=32.5, fiber=2.5, sugar=6.0, sodium=1150.0)
            micronutrients = AIMicronutrients(iron=2.1, calcium=310.0, magnesium=35.0, potassium=240.0, vitamin_a=95.0, vitamin_c=2.0, vitamin_d=0.5, vitamin_b12=1.4)
            health_score = 45
            summary = "A calorie-dense meal with high sodium and saturated fat content, but a decent serving of calcium and protein."
            insights = [
                "High sodium level (approx. 50% of the recommended daily limit). Drink plenty of water.",
                "Good protein and calcium source from mozzarella cheese.",
                "Lacks fiber and vegetable-based micronutrients.",
                "Pair with a fresh green side salad to boost vitamins and fiber, and moderate portion size."
            ]
        elif "egg" in desc or "breakfast" in desc or "toast" in desc:
            meal_name = "Classic Egg & Avocado Toast"
            foods = [
                AIFoodItem(name="Sourdough Bread Toast", estimated_quantity="2 slices (70g)", calories=185, protein=7.0, carbohydrates=36.0, fat=1.2),
                AIFoodItem(name="Poached Eggs", estimated_quantity="2 large", calories=143, protein=12.6, carbohydrates=0.7, fat=9.5),
                AIFoodItem(name="Mashed Avocado", estimated_quantity="60 g", calories=96, protein=1.2, carbohydrates=5.0, fat=8.8)
            ]
            nutrition = AINutritionTotals(calories=424, protein=20.8, carbohydrates=41.7, fat=19.5, fiber=6.0, sugar=2.2, sodium=380.0)
            micronutrients = AIMicronutrients(iron=2.8, calcium=62.0, magnesium=58.0, potassium=490.0, vitamin_a=180.0, vitamin_c=8.0, vitamin_d=2.0, vitamin_b12=1.2)
            health_score = 88
            summary = "A balanced breakfast featuring quality protein, healthy fats, and complex carbohydrates from sourdough."
            insights = [
                "Excellent source of choline and high-quality protein from eggs.",
                "Healthy fats and fiber from avocado promote long-lasting satiety.",
                "Sourdough toast provides slow-release carbohydrates.",
                "Add a side of grilled tomatoes or spinach to enhance Vitamin C intake."
            ]
        else:
            # Default balanced meal
            meal_name = "Seared Salmon with Quinoa & Asparagus"
            foods = [
                AIFoodItem(name="Pan-seared Salmon Fillet", estimated_quantity="150 g", calories=310, protein=34.0, carbohydrates=0.0, fat=18.0),
                AIFoodItem(name="Cooked Quinoa", estimated_quantity="1 cup (185g)", calories=222, protein=8.1, carbohydrates=39.0, fat=3.6),
                AIFoodItem(name="Steamed Asparagus spears", estimated_quantity="6 medium", calories=25, protein=2.2, carbohydrates=4.8, fat=0.2)
            ]
            nutrition = AINutritionTotals(calories=557, protein=44.3, carbohydrates=43.8, fat=21.8, fiber=7.5, sugar=1.8, sodium=280.0)
            micronutrients = AIMicronutrients(iron=4.5, calcium=92.0, magnesium=118.0, potassium=950.0, vitamin_a=240.0, vitamin_c=12.0, vitamin_d=10.5, vitamin_b12=4.8)
            health_score = 95
            summary = "An outstanding, nutrient-dense meal rich in heart-healthy Omega-3 fatty acids, plant-based fiber, and magnesium."
            insights = [
                "Rich in Omega-3 fatty acids, excellent for cardiovascular health.",
                "Quinoa provides a complete plant protein profile and complex carbohydrates.",
                "Low sodium and sugar profile makes this an exceptionally clean meal.",
                "Asparagus adds prebiotics that support digestive gut health."
            ]
        
        # If an image was uploaded, append "(Analyzed from Image)" to make it clear image was handled
        if image_data:
            meal_name += " 📸"
            
        return AIAnalysisResult(
            meal_name=meal_name,
            foods=foods,
            nutrition=nutrition,
            micronutrients=micronutrients,
            health_score=health_score,
            summary=summary,
            insights=insights
        )


class GeminiAIProvider(AIProvider):
    def __init__(self):
        # Read the prompt template
        prompt_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts", "nutrition_analysis.txt")
        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                self.prompt_template = f.read()
        except Exception:
            # Fallback prompt in case reading fails
            self.prompt_template = "Analyze the meal: {description}. Return JSON."
            
        # Configure Gemini
        api_key = settings.AI_API_KEY
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel("gemini-1.5-flash")
        else:
            self.model = None

    async def analyze_meal(
        self, 
        description: Optional[str] = None, 
        image_data: Optional[bytes] = None, 
        mime_type: Optional[str] = None
    ) -> AIAnalysisResult:
        if not settings.AI_API_KEY or not self.model:
            # Fallback to mock provider automatically if API key is not configured
            mock = MockAIProvider()
            return await mock.analyze_meal(description, image_data, mime_type)
            
        # Format the system/user instruction prompt
        user_prompt = self.prompt_template.replace(
            "{description}", description or "No description provided"
        ).replace(
            "{has_image}", "Yes" if image_data else "No"
        )
        
        contents = [user_prompt]
        
        if image_data:
            contents.append({
                "mime_type": mime_type or "image/jpeg",
                "data": image_data
            })
            
        try:
            # Request content generation
            response = self.model.generate_content(contents)
            response_text = response.text
            
            # Clean up the output to extract JSON
            json_data = self._extract_json(response_text)
            
            # Parse into AIAnalysisResult model
            return AIAnalysisResult(**json_data)
        except Exception as e:
            # Fallback to Mock provider if AI service fails, to guarantee working app
            print(f"Gemini API failure: {str(e)}. Falling back to MockAIProvider.")
            mock = MockAIProvider()
            fallback_result = await mock.analyze_meal(description, image_data, mime_type)
            fallback_result.summary += f" (Note: Gemini API was unavailable, loaded via fallback)."
            return fallback_result

    def _extract_json(self, text: str) -> Dict[str, Any]:
        # Strip markdown markers if present
        match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
        if match:
            json_str = match.group(1)
        else:
            # Try to grab whatever is inside curly braces
            match_brace = re.search(r'(\{.*\})', text, re.DOTALL)
            if match_brace:
                json_str = match_brace.group(1)
            else:
                json_str = text
                
        # Clean and parse
        cleaned_str = json_str.strip()
        return json.loads(cleaned_str)

# Helper function to initialize provider based on environment settings
def get_ai_provider() -> AIProvider:
    if settings.AI_API_KEY and settings.AI_PROVIDER.lower() == "gemini":
        return GeminiAIProvider()
    return MockAIProvider()
