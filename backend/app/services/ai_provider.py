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
        mime_type: Optional[str] = None,
        filename: Optional[str] = None
    ) -> AIAnalysisResult:
        raise NotImplementedError("analyze_meal must be implemented by subclasses")


class MockAIProvider(AIProvider):
    def _analyze_image_content(self, image_data: bytes) -> Optional[str]:
        """
        Extracts dominant color profile and visual features from image bytes using Pillow (PIL).
        Ignores white/light studio background pixels to accurately identify food.
        Returns detected food category: 'avocado', 'banana', 'orange', 'apple', 'dry_fruits', 'mixed_fruits', 'salad', 'salmon', 'egg', 'pizza', etc.
        """
        if not image_data:
            return None
        try:
            from PIL import Image, ImageFile
            import io
            ImageFile.LOAD_TRUNCATED_IMAGES = True
            img = Image.open(io.BytesIO(image_data)).convert("RGB")
            img_small = img.resize((60, 60))
            pixels = list(img_small.getdata())
            
            total_pixels = len(pixels)
            if total_pixels == 0:
                return None
                
            white_bg_count = 0
            foreground_pixels = 0
            
            brown_nut_count = 0
            green_count = 0
            red_fruit_count = 0
            salmon_pink_count = 0
            yellow_count = 0
            orange_count = 0
            dark_raisin_count = 0
            egg_yolk_count = 0

            for r, g, b in pixels:
                # White/light gray studio background (ignore for food color ratio calculation)
                if (r > 195 and g > 190 and b > 180 and abs(r - g) < 35 and abs(g - b) < 35) or (r > 235 and g > 235 and b > 235):
                    white_bg_count += 1
                    continue
                
                foreground_pixels += 1
                
                # Dark green / Lime green (avocado, green apple, kiwi, greens)
                if (g > r + 10 and g > b + 10) or (r < 120 and g > 60 and g > r) or (r > 100 and g > 130 and g > b + 20):
                    green_count += 1
                # Bright yellow (banana, mango, pineapple, egg yolk)
                elif r > 170 and g > 150 and b < 140 and (r - b) > 50:
                    yellow_count += 1
                    if r > 200 and g > 160 and b < 80:
                        egg_yolk_count += 1
                # Orange (citrus orange, papaya, carrot)
                elif r > 180 and 80 <= g <= 170 and b < 110:
                    orange_count += 1
                # Vibrant red / pink (apple, strawberry, watermelon, cherry, red grapes)
                elif r > 140 and r > g * 1.25 and r > b * 1.25:
                    red_fruit_count += 1
                # Salmon pink (cooked salmon)
                elif r > 180 and 110 <= g <= 165 and 90 <= b <= 140:
                    salmon_pink_count += 1
                # Brown/tan nut tones (almonds, cashews, walnuts, pistachios, dates)
                elif 80 < r < 190 and 50 < g < 140 and b < 100 and (r - g) > 20 and (g - b) > 10:
                    brown_nut_count += 1
                # Dark purple/black/dark brown (raisins, prunes, dark grapes, dates)
                elif r < 90 and g < 70 and b < 80:
                    dark_raisin_count += 1

            fg_total = foreground_pixels if foreground_pixels > 0 else total_pixels

            green_ratio = green_count / fg_total
            yellow_ratio = yellow_count / fg_total
            orange_ratio = orange_count / fg_total
            red_ratio = red_fruit_count / fg_total
            salmon_ratio = salmon_pink_count / fg_total
            brown_ratio = brown_nut_count / fg_total
            dark_ratio = dark_raisin_count / fg_total
            yolk_ratio = egg_yolk_count / fg_total

            # 1. Avocado / Green fruit / Salad detection
            if green_ratio > 0.18:
                if green_ratio > 0.35 or brown_ratio > 0.08:
                    return "avocado"
                return "salad"

            # 2. Almonds / Cashews / Dry Fruits detection
            if brown_ratio > 0.18 or (brown_ratio + dark_ratio) > 0.22:
                return "dry_fruits"

            # 3. Banana / Yellow fruit detection
            if yellow_ratio > 0.18:
                if yolk_ratio > 0.20 and white_bg_count > total_pixels * 0.4:
                    return "egg"
                return "banana"

            # 4. Orange / Citrus / Papaya detection
            if orange_ratio > 0.18:
                return "orange"

            # 5. Apple / Red fruit / Strawberry detection
            if red_ratio > 0.18:
                return "apple"

            # 6. Salmon detection
            if salmon_ratio > 0.15:
                return "salmon"

            # 7. Dark Raisins / Dates / Grapes
            if dark_ratio > 0.18:
                return "dry_fruits"

            # 8. Egg detection (requires yellow yolk + white background)
            if yolk_ratio > 0.15 and white_bg_count > total_pixels * 0.4:
                return "egg"

            # 9. Generic fruit / dry fruit detection if foreground matches fruit colors
            if (green_count + yellow_count + orange_count + red_fruit_count) > fg_total * 0.30:
                return "mixed_fruits"

            if (brown_nut_count + dark_raisin_count) > fg_total * 0.25:
                return "dry_fruits"

            return None
        except Exception:
            return None

    # ---------------------------------------------------------------
    # Expanded keyword → category mapping (100+ food types supported)
    # ---------------------------------------------------------------
    KEYWORD_MAP = [
        # Indian staples
        ("thali", ["thali", "south indian", "south indian meal", "south indian meals", "south meal", "south meals", "meals", "banana leaf meal", "veg meal", "full meals", "bhojanam"]),
        ("idli", ["idli", "idly", "idlis"]),
        ("dosa", ["dosa", "masala dosa", "plain dosa", "rava dosa", "set dosa"]),
        ("sambar", ["sambar", "sambhar"]),
        ("biryani", ["biryani", "biriyani", "dum biryani", "chicken biryani", "mutton biryani", "veg biryani"]),
        ("dal", ["dal", "dhal", "lentil", "lentils", "dal tadka", "dal makhani", "red dal", "yellow dal", "moong dal", "masoor"]),
        ("roti", ["roti", "chapati", "chapatti", "phulka", "flatbread"]),
        ("naan", ["naan", "garlic naan", "butter naan"]),
        ("paratha", ["paratha", "parantha", "aloo paratha", "paneer paratha"]),
        ("paneer", ["paneer", "cottage cheese", "paneer tikka", "shahi paneer", "palak paneer", "paneer butter masala"]),
        ("curd", ["curd", "dahi", "yogurt", "yoghurt", "raita"]),
        ("upma", ["upma"]),
        ("poha", ["poha", "pohe", "chivda"]),
        ("pongal", ["pongal", "khichdi", "khichri"]),
        ("rajma", ["rajma", "kidney beans", "red beans"]),
        ("chole", ["chole", "chana", "chickpea", "chickpeas", "chhole"]),
        ("samosa", ["samosa", "samosas"]),
        ("vada", ["vada", "wada", "medu vada", "aloo vada"]),
        ("puri", ["puri", "poori", "bhatura", "bhatoora"]),
        ("uttapam", ["uttapam", "utthappam"]),
        ("pulao", ["pulao", "pilaf", "fried rice", "jeera rice"]),
        ("halwa", ["halwa", "halva", "sooji halwa", "gajar ka halwa"]),
        ("ladoo", ["ladoo", "laddu", "besan ladoo"]),
        ("jalebi", ["jalebi"]),
        ("gulab_jamun", ["gulab jamun", "gulabjamun"]),
        ("kheer", ["kheer", "rice pudding", "payasam", "payasa"]),
        # Proteins
        ("salad", ["chicken", "grilled chicken", "chicken breast", "salad", "greens", "kale", "spinach", "caesar salad", "greek salad"]),
        ("salmon", ["salmon", "fish", "seafood", "tuna", "cod", "tilapia", "prawn", "shrimp", "crab", "lobster", "mackerel", "sardine"]),
        ("egg", ["egg", "eggs", "boiled egg", "poached egg", "omelet", "omelette", "scrambled egg", "fried egg", "half fry", "anda"]),
        # Grains & Carbs
        ("rice", ["rice", "white rice", "brown rice", "steamed rice", "basmati"]),
        ("oats", ["oats", "oatmeal", "porridge", "overnight oats", "muesli", "granola"]),
        ("bread", ["bread", "whole wheat bread", "white bread", "toast", "sandwich", "wrap"]),
        ("pasta", ["pasta", "spaghetti", "penne", "macaroni", "noodles", "fettuccine", "linguine", "ramen", "udon"]),
        ("burger", ["burger", "hamburger", "cheeseburger", "veggie burger"]),
        ("pizza", ["pizza", "pepperoni pizza", "margherita pizza", "cheese pizza"]),
        ("sandwich", ["sandwich", "sub", "club sandwich", "grilled sandwich"]),
        # Dairy
        ("milk", ["milk", "glass of milk", "whole milk", "skim milk", "almond milk"]),
        ("cheese", ["cheese", "cheddar", "mozzarella", "parmesan", "feta"]),
        ("butter", ["butter", "makhan"]),
        # Fruits
        ("avocado", ["avocado", "avacado", "abocado", "guacamole", "guac"]),
        ("banana", ["banana", "bananas", "plantain", "kela"]),
        ("orange", ["orange", "oranges", "citrus", "tangerine", "clementine", "mandarin", "mosambi"]),
        ("apple", ["apple", "apples", "seb", "strawberry", "strawberries", "blueberry", "blueberries", "cherry", "cherries", "berry", "berries", "raspberry"]),
        ("mango", ["mango", "mangoes", "aam", "alphonso", "kesar mango"]),
        ("grapes", ["grape", "grapes", "angoor"]),
        ("watermelon", ["watermelon", "tarbooz", "melon", "cantaloupe", "honeydew"]),
        ("pineapple", ["pineapple", "ananas"]),
        ("papaya", ["papaya", "pawpaw", "papita"]),
        ("pomegranate", ["pomegranate", "anar"]),
        ("kiwi", ["kiwi", "kiwifruit"]),
        # Nuts & dry fruits (placed before mixed_fruits so 'dry fruit' takes precedence over 'fruit')
        ("dry_fruits", ["dry fruit", "dryfruit", "dryfruits", "dry-fruit", "dry fruits", "almond", "almonds", "badam", "cashew", "cashews", "kaju", "walnut", "walnuts", "akhrot", "pistachio", "pistachios", "pista", "raisin", "raisins", "kishmish", "date", "dates", "khajoor", "fig", "figs", "anjeer", "nut", "nuts", "mixed nuts", "trail mix"]),
        ("mixed_fruits", ["fruit", "fruits", "fruit salad", "fruit bowl", "mixed fruit", "fresh fruits"]),
        # Vegetables
        ("broccoli", ["broccoli"]),
        ("carrot", ["carrot", "carrots", "gajar"]),
        ("potato", ["potato", "potatoes", "aloo", "french fries", "fries", "mashed potato", "baked potato"]),
        ("corn", ["corn", "sweetcorn", "maize", "bhutta"]),
        # Soups & Beverages
        ("soup", ["soup", "tomato soup", "vegetable soup", "chicken soup", "dal soup", "broth"]),
        ("smoothie", ["smoothie", "juice", "protein shake", "milkshake", "lassi", "buttermilk"]),
        # Fast food & sweets
        ("chocolate", ["chocolate", "dark chocolate", "cocoa", "brownie", "chocolate cake"]),
        ("icecream", ["ice cream", "icecream", "ice-cream", "kulfi", "gelato"]),
        ("cookie", ["cookie", "cookies", "biscuit", "biscuits"]),
        ("cake", ["cake", "cupcake", "muffin", "pastry"]),
    ]

    async def analyze_meal(
        self, 
        description: Optional[str] = None, 
        image_data: Optional[bytes] = None, 
        mime_type: Optional[str] = None,
        filename: Optional[str] = None
    ) -> AIAnalysisResult:
        query_str = f"{description or ''} {filename or ''}".lower()

        # 1. Check description text & filename against the expanded keyword map
        visual_category = None
        for category, keywords in self.KEYWORD_MAP:
            if any(kw in query_str for kw in keywords):
                visual_category = category
                break

        # 2. Pixel color analysis: Run whenever an image is uploaded
        if not visual_category and image_data:
            visual_category = self._analyze_image_content(image_data)

        # Build food profile based on visual_category
        # ---- Indian Foods ----
        if visual_category == "thali":
            meal_name = "Traditional South Indian Meals (Thali)"
            foods = [
                AIFoodItem(name="Steamed Ponni Rice", estimated_quantity="1 large bowl (250g)", calories=325, protein=6.5, carbohydrates=71.0, fat=0.9),
                AIFoodItem(name="South Indian Sambar", estimated_quantity="1 cup (150ml)", calories=115, protein=4.8, carbohydrates=17.0, fat=3.2),
                AIFoodItem(name="Pepper Rasam", estimated_quantity="1 cup (150ml)", calories=45, protein=1.2, carbohydrates=8.0, fat=1.1),
                AIFoodItem(name="Vegetable Poriyal / Kootu", estimated_quantity="1 cup (120g)", calories=95, protein=3.2, carbohydrates=14.0, fat=3.1),
                AIFoodItem(name="Fresh Curd / Yogurt", estimated_quantity="1/2 cup (100g)", calories=60, protein=3.5, carbohydrates=4.5, fat=3.0),
                AIFoodItem(name="Appalam / Papad", estimated_quantity="1 piece", calories=45, protein=1.5, carbohydrates=6.0, fat=1.8),
            ]
            nutrition = AINutritionTotals(calories=685, protein=20.7, carbohydrates=120.5, fat=13.1, fiber=8.5, sugar=6.0, sodium=620.0)
            micronutrients = AIMicronutrients(iron=3.8, calcium=165.0, magnesium=85.0, potassium=620.0, vitamin_a=140.0, vitamin_c=22.0, vitamin_d=0.2, vitamin_b12=0.5)
            health_score = 86
            summary = "A wholesome, balanced traditional South Indian thali featuring steamed rice, vegetable sambar, digestive rasam, nutrient-packed poriyal, and cooling curd. Rich in complex carbs, dietary fiber, and plant proteins."
            insights = [
                "Pepper rasam aids digestion and provides immunity-boosting antioxidants.",
                "Lentil sambar and vegetable poriyal provide a rich source of plant protein and dietary fiber.",
                "Probiotic curd supports healthy gut flora after a hearty meal."
            ]

        elif visual_category == "idli":
            meal_name = "Steamed Idli with Sambar"
            foods = [
                AIFoodItem(name="Steamed Rice Idli", estimated_quantity="3 pieces (150g)", calories=117, protein=3.9, carbohydrates=24.0, fat=0.5),
                AIFoodItem(name="Sambar", estimated_quantity="1 cup (200ml)", calories=80, protein=4.5, carbohydrates=12.0, fat=2.5),
            ]
            nutrition = AINutritionTotals(calories=197, protein=8.4, carbohydrates=36.0, fat=3.0, fiber=4.2, sugar=4.0, sodium=310.0)
            micronutrients = AIMicronutrients(iron=2.1, calcium=60.0, magnesium=35.0, potassium=380.0, vitamin_a=110.0, vitamin_c=12.0, vitamin_d=0.0, vitamin_b12=0.0)
            health_score = 88
            summary = "A classic South Indian breakfast — light, fermented rice-lentil cakes with protein-rich sambar. Excellent for digestion and low in fat."
            insights = [
                "Fermented idli batter boosts gut-friendly probiotics and improves nutrient absorption.",
                "Sambar provides a good dose of plant protein, iron, and vegetables.",
                "Low in fat and calories — ideal for weight management."
            ]

        elif visual_category == "dosa":
            meal_name = "Crispy Masala Dosa"
            foods = [
                AIFoodItem(name="Dosa (Rice & Lentil Crepe)", estimated_quantity="1 large (120g)", calories=168, protein=4.5, carbohydrates=32.0, fat=3.5),
                AIFoodItem(name="Aloo Masala Filling", estimated_quantity="80g", calories=95, protein=2.0, carbohydrates=17.0, fat=3.0),
                AIFoodItem(name="Coconut Chutney", estimated_quantity="2 tbsp", calories=55, protein=0.8, carbohydrates=3.0, fat=5.0),
            ]
            nutrition = AINutritionTotals(calories=318, protein=7.3, carbohydrates=52.0, fat=11.5, fiber=3.8, sugar=3.5, sodium=450.0)
            micronutrients = AIMicronutrients(iron=1.8, calcium=55.0, magnesium=40.0, potassium=420.0, vitamin_a=95.0, vitamin_c=10.0, vitamin_d=0.0, vitamin_b12=0.0)
            health_score = 80
            summary = "A beloved South Indian crepe made from fermented rice-lentil batter, typically filled with spiced potato and served with chutney."
            insights = [
                "Fermented batter increases B-vitamin content and aids digestion.",
                "Moderate calorie meal — good for an active breakfast.",
                "Adding sambar alongside boosts protein and iron content."
            ]

        elif visual_category == "sambar":
            meal_name = "South Indian Sambar"
            foods = [
                AIFoodItem(name="Toor Dal Sambar", estimated_quantity="1 bowl (250ml)", calories=130, protein=7.0, carbohydrates=18.0, fat=3.5),
            ]
            nutrition = AINutritionTotals(calories=130, protein=7.0, carbohydrates=18.0, fat=3.5, fiber=5.5, sugar=4.0, sodium=380.0)
            micronutrients = AIMicronutrients(iron=2.5, calcium=48.0, magnesium=38.0, potassium=420.0, vitamin_a=180.0, vitamin_c=15.0, vitamin_d=0.0, vitamin_b12=0.0)
            health_score = 90
            summary = "A tangy, tamarind-based lentil and vegetable soup, rich in plant protein, iron, and dietary fiber."
            insights = [
                "High plant-protein from toor dal supports muscle maintenance.",
                "Tamarind and tomatoes provide a Vitamin C boost for iron absorption.",
                "Vegetables in sambar add dietary fiber and micronutrients."
            ]

        elif visual_category == "biryani":
            meal_name = "Chicken Dum Biryani"
            foods = [
                AIFoodItem(name="Basmati Rice", estimated_quantity="1.5 cups cooked (240g)", calories=320, protein=6.0, carbohydrates=70.0, fat=0.6),
                AIFoodItem(name="Marinated Chicken", estimated_quantity="150g", calories=240, protein=28.0, carbohydrates=3.0, fat=12.0),
                AIFoodItem(name="Fried Onions, Spices & Ghee", estimated_quantity="30g", calories=110, protein=1.0, carbohydrates=5.0, fat=10.0),
            ]
            nutrition = AINutritionTotals(calories=670, protein=35.0, carbohydrates=78.0, fat=22.6, fiber=2.5, sugar=4.0, sodium=680.0)
            micronutrients = AIMicronutrients(iron=3.2, calcium=75.0, magnesium=55.0, potassium=520.0, vitamin_a=120.0, vitamin_c=5.0, vitamin_d=0.3, vitamin_b12=0.8)
            health_score = 70
            summary = "A festive South Asian rice dish layered with marinated chicken, aromatic spices, and saffron-infused basmati rice."
            insights = [
                "High protein from chicken makes this a satisfying complete meal.",
                "Calorie-dense — best enjoyed as a main meal with a side of raita.",
                "Spices like turmeric and cumin offer anti-inflammatory antioxidants."
            ]

        elif visual_category == "dal":
            meal_name = "Dal Tadka (Tempered Lentils)"
            foods = [
                AIFoodItem(name="Cooked Yellow Dal (Toor/Moong)", estimated_quantity="1 cup (200g)", calories=198, protein=13.5, carbohydrates=30.0, fat=4.5),
            ]
            nutrition = AINutritionTotals(calories=198, protein=13.5, carbohydrates=30.0, fat=4.5, fiber=8.0, sugar=3.0, sodium=320.0)
            micronutrients = AIMicronutrients(iron=3.3, calcium=60.0, magnesium=70.0, potassium=590.0, vitamin_a=80.0, vitamin_c=3.0, vitamin_d=0.0, vitamin_b12=0.0)
            health_score = 92
            summary = "A protein-rich Indian lentil dish tempered with cumin, garlic, and spices — a nutritional staple across India."
            insights = [
                "Excellent plant protein and iron source, ideal for vegetarians.",
                "High dietary fiber supports gut health and blood sugar control.",
                "Low glycemic index — provides sustained, slow-release energy."
            ]

        elif visual_category == "roti":
            meal_name = "Whole Wheat Roti / Chapati"
            foods = [
                AIFoodItem(name="Whole Wheat Chapati", estimated_quantity="2 rotis (60g)", calories=150, protein=5.4, carbohydrates=30.0, fat=2.0),
            ]
            nutrition = AINutritionTotals(calories=150, protein=5.4, carbohydrates=30.0, fat=2.0, fiber=4.0, sugar=1.0, sodium=180.0)
            micronutrients = AIMicronutrients(iron=1.8, calcium=30.0, magnesium=45.0, potassium=170.0, vitamin_a=0.0, vitamin_c=0.0, vitamin_d=0.0, vitamin_b12=0.0)
            health_score = 85
            summary = "A whole-grain Indian flatbread — low fat, moderate protein, and a good source of complex carbohydrates and dietary fiber."
            insights = [
                "Whole wheat provides complex carbs for sustained energy release.",
                "Good source of dietary fiber supporting digestive regularity.",
                "Pair with dal or sabzi for a nutritionally complete meal."
            ]

        elif visual_category == "naan":
            meal_name = "Butter Naan"
            foods = [
                AIFoodItem(name="Butter Naan (Tandoor Baked)", estimated_quantity="1 piece (90g)", calories=262, protein=7.5, carbohydrates=44.0, fat=6.5),
            ]
            nutrition = AINutritionTotals(calories=262, protein=7.5, carbohydrates=44.0, fat=6.5, fiber=1.5, sugar=3.0, sodium=480.0)
            micronutrients = AIMicronutrients(iron=1.5, calcium=50.0, magnesium=25.0, potassium=130.0, vitamin_a=50.0, vitamin_c=0.0, vitamin_d=0.0, vitamin_b12=0.1)
            health_score = 68
            summary = "A soft, leavened Indian flatbread baked in a tandoor and finished with butter — higher in calories than roti due to maida and butter."
            insights = [
                "Higher calorie density than whole wheat roti — moderate your portions.",
                "Pairs well with protein-rich curries to balance the macros.",
                "Opt for whole wheat naan for a fiber boost."
            ]

        elif visual_category == "paratha":
            meal_name = "Aloo Paratha with Curd"
            foods = [
                AIFoodItem(name="Aloo Stuffed Paratha", estimated_quantity="2 pieces (200g)", calories=380, protein=8.5, carbohydrates=54.0, fat=14.5),
                AIFoodItem(name="Plain Curd / Yogurt", estimated_quantity="100g", calories=61, protein=3.5, carbohydrates=4.7, fat=3.3),
            ]
            nutrition = AINutritionTotals(calories=441, protein=12.0, carbohydrates=58.7, fat=17.8, fiber=4.5, sugar=5.0, sodium=520.0)
            micronutrients = AIMicronutrients(iron=2.0, calcium=130.0, magnesium=50.0, potassium=450.0, vitamin_a=80.0, vitamin_c=10.0, vitamin_d=0.1, vitamin_b12=0.3)
            health_score = 74
            summary = "A hearty Indian stuffed flatbread with spiced potato filling, paired with cooling yogurt — popular breakfast across North India."
            insights = [
                "Curd adds probiotics and calcium while cooling the meal down.",
                "Moderate in calories — suitable as a filling breakfast.",
                "Reduce ghee for a lighter calorie version."
            ]

        elif visual_category == "paneer":
            meal_name = "Paneer Butter Masala"
            foods = [
                AIFoodItem(name="Paneer (Indian Cottage Cheese)", estimated_quantity="150g", calories=265, protein=18.0, carbohydrates=3.0, fat=20.0),
                AIFoodItem(name="Tomato Butter Gravy", estimated_quantity="150ml", calories=135, protein=2.5, carbohydrates=10.0, fat=9.5),
            ]
            nutrition = AINutritionTotals(calories=400, protein=20.5, carbohydrates=13.0, fat=29.5, fiber=2.0, sugar=6.0, sodium=540.0)
            micronutrients = AIMicronutrients(iron=1.5, calcium=340.0, magnesium=45.0, potassium=250.0, vitamin_a=180.0, vitamin_c=8.0, vitamin_d=0.2, vitamin_b12=0.5)
            health_score = 75
            summary = "A rich, creamy Indian dish of fresh cottage cheese in a spiced tomato-butter sauce — high in protein and calcium."
            insights = [
                "Paneer is one of the best vegetarian protein sources with all essential amino acids.",
                "Rich in calcium for bone health.",
                "High in saturated fat — moderate portion size recommended."
            ]

        elif visual_category == "curd":
            meal_name = "Plain Curd / Yogurt Bowl"
            foods = [
                AIFoodItem(name="Full-Fat Dahi (Curd)", estimated_quantity="200g", calories=122, protein=7.0, carbohydrates=9.4, fat=6.0),
            ]
            nutrition = AINutritionTotals(calories=122, protein=7.0, carbohydrates=9.4, fat=6.0, fiber=0.0, sugar=9.0, sodium=90.0)
            micronutrients = AIMicronutrients(iron=0.1, calcium=240.0, magnesium=19.0, potassium=300.0, vitamin_a=95.0, vitamin_c=1.0, vitamin_d=0.1, vitamin_b12=0.9)
            health_score = 89
            summary = "A probiotic-rich fermented dairy product providing calcium, protein, and gut-friendly live cultures."
            insights = [
                "Probiotics support gut microbiome balance and immune function.",
                "Excellent calcium source for bone density and strength.",
                "Cooling and soothing — great with spicy Indian meals as raita."
            ]

        elif visual_category == "upma":
            meal_name = "Rava Upma (Semolina Porridge)"
            foods = [
                AIFoodItem(name="Semolina Upma with Vegetables", estimated_quantity="1 bowl (200g)", calories=230, protein=6.5, carbohydrates=40.0, fat=6.0),
            ]
            nutrition = AINutritionTotals(calories=230, protein=6.5, carbohydrates=40.0, fat=6.0, fiber=3.5, sugar=2.5, sodium=380.0)
            micronutrients = AIMicronutrients(iron=1.9, calcium=35.0, magnesium=30.0, potassium=260.0, vitamin_a=90.0, vitamin_c=8.0, vitamin_d=0.0, vitamin_b12=0.0)
            health_score = 82
            summary = "A quick South Indian breakfast made from roasted semolina, tempered spices, and mixed vegetables."
            insights = [
                "Good source of iron and B-vitamins from semolina.",
                "Vegetables boost fiber and micronutrient content.",
                "Low in fat and easy to digest — great for light morning meals."
            ]

        elif visual_category == "poha":
            meal_name = "Kanda Poha (Flattened Rice)"
            foods = [
                AIFoodItem(name="Flattened Rice with Onion & Peanuts", estimated_quantity="1 plate (200g)", calories=244, protein=6.0, carbohydrates=45.0, fat=5.5),
            ]
            nutrition = AINutritionTotals(calories=244, protein=6.0, carbohydrates=45.0, fat=5.5, fiber=3.0, sugar=3.0, sodium=290.0)
            micronutrients = AIMicronutrients(iron=2.8, calcium=25.0, magnesium=35.0, potassium=220.0, vitamin_a=60.0, vitamin_c=10.0, vitamin_d=0.0, vitamin_b12=0.0)
            health_score = 84
            summary = "A light, iron-rich Indian breakfast of flattened rice with onions, turmeric, peanuts, and curry leaves."
            insights = [
                "Flattened rice is an excellent source of easily absorbed iron.",
                "Peanuts add protein and healthy monounsaturated fats.",
                "Low calorie, easy to digest, and quick to prepare."
            ]

        elif visual_category == "pongal":
            meal_name = "Ven Pongal / Khichdi"
            foods = [
                AIFoodItem(name="Rice & Moong Dal Pongal", estimated_quantity="1 bowl (250g)", calories=295, protein=10.5, carbohydrates=52.0, fat=6.5),
            ]
            nutrition = AINutritionTotals(calories=295, protein=10.5, carbohydrates=52.0, fat=6.5, fiber=4.5, sugar=2.0, sodium=320.0)
            micronutrients = AIMicronutrients(iron=2.0, calcium=45.0, magnesium=55.0, potassium=340.0, vitamin_a=70.0, vitamin_c=5.0, vitamin_d=0.0, vitamin_b12=0.0)
            health_score = 87
            summary = "A comforting one-pot meal of rice and green gram — nutritious, easy to digest, and gentle on the stomach."
            insights = [
                "Perfect comfort food — high in complex carbs for sustained energy.",
                "Moong dal adds plant protein and essential amino acids.",
                "Ideal for recovery meals or upset stomachs."
            ]

        elif visual_category == "rajma":
            meal_name = "Rajma Masala (Kidney Bean Curry)"
            foods = [
                AIFoodItem(name="Cooked Rajma in Tomato Gravy", estimated_quantity="1 cup (250g)", calories=215, protein=13.0, carbohydrates=34.0, fat=4.5),
            ]
            nutrition = AINutritionTotals(calories=215, protein=13.0, carbohydrates=34.0, fat=4.5, fiber=9.5, sugar=4.0, sodium=430.0)
            micronutrients = AIMicronutrients(iron=4.5, calcium=75.0, magnesium=65.0, potassium=600.0, vitamin_a=95.0, vitamin_c=8.0, vitamin_d=0.0, vitamin_b12=0.0)
            health_score = 91
            summary = "A protein and fiber powerhouse curry of kidney beans simmered in spiced tomato gravy — a North Indian classic."
            insights = [
                "Outstanding plant protein and iron — excellent for vegetarians.",
                "Very high dietary fiber content supports heart health and blood sugar.",
                "Pairs perfectly with steamed rice for a complete amino acid profile."
            ]

        elif visual_category == "chole":
            meal_name = "Chole (Spiced Chickpea Curry)"
            foods = [
                AIFoodItem(name="Chickpea Masala Curry", estimated_quantity="1 cup (250g)", calories=220, protein=11.0, carbohydrates=36.0, fat=5.0),
            ]
            nutrition = AINutritionTotals(calories=220, protein=11.0, carbohydrates=36.0, fat=5.0, fiber=10.5, sugar=5.0, sodium=460.0)
            micronutrients = AIMicronutrients(iron=3.8, calcium=80.0, magnesium=60.0, potassium=520.0, vitamin_a=85.0, vitamin_c=6.0, vitamin_d=0.0, vitamin_b12=0.0)
            health_score = 90
            summary = "Hearty spiced chickpea curry bursting with plant protein, iron, and gut-healthy dietary fiber."
            insights = [
                "Chickpeas are among the best plant-based protein sources.",
                "Rich in soluble fiber which lowers LDL cholesterol.",
                "Add lemon juice before serving to boost iron absorption."
            ]

        elif visual_category == "samosa":
            meal_name = "Aloo Samosa (Fried Pastry)"
            foods = [
                AIFoodItem(name="Samosa with Potato Filling", estimated_quantity="2 pieces (120g)", calories=310, protein=5.5, carbohydrates=38.0, fat=15.5),
            ]
            nutrition = AINutritionTotals(calories=310, protein=5.5, carbohydrates=38.0, fat=15.5, fiber=2.5, sugar=2.0, sodium=480.0)
            micronutrients = AIMicronutrients(iron=1.5, calcium=25.0, magnesium=22.0, potassium=280.0, vitamin_a=45.0, vitamin_c=8.0, vitamin_d=0.0, vitamin_b12=0.0)
            health_score = 52
            summary = "A popular Indian fried pastry filled with spiced potatoes and peas — delicious but high in fat and calories."
            insights = [
                "Deep-fried — high in calories and saturated fat.",
                "Enjoy as an occasional snack rather than a regular meal.",
                "Baked samosa versions reduce fat content by 40%."
            ]

        elif visual_category == "vada":
            meal_name = "Medu Vada (Lentil Fritters)"
            foods = [
                AIFoodItem(name="Urad Dal Medu Vada", estimated_quantity="2 pieces (80g)", calories=195, protein=7.5, carbohydrates=25.0, fat=8.0),
            ]
            nutrition = AINutritionTotals(calories=195, protein=7.5, carbohydrates=25.0, fat=8.0, fiber=3.5, sugar=1.5, sodium=320.0)
            micronutrients = AIMicronutrients(iron=2.2, calcium=50.0, magnesium=40.0, potassium=280.0, vitamin_a=40.0, vitamin_c=2.0, vitamin_d=0.0, vitamin_b12=0.0)
            health_score = 68
            summary = "Crispy deep-fried urad dal donuts — protein-rich but fried, best enjoyed as an occasional South Indian breakfast."
            insights = [
                "Urad dal provides good plant protein and essential B vitamins.",
                "Fermented batter aids digestion and nutrient absorption.",
                "Frying increases calorie density — eat in moderation."
            ]

        elif visual_category == "puri":
            meal_name = "Puri / Bhatura (Deep-Fried Bread)"
            foods = [
                AIFoodItem(name="Deep-Fried Wheat Puri", estimated_quantity="3 pieces (90g)", calories=320, protein=6.5, carbohydrates=40.0, fat=15.0),
            ]
            nutrition = AINutritionTotals(calories=320, protein=6.5, carbohydrates=40.0, fat=15.0, fiber=2.0, sugar=1.5, sodium=290.0)
            micronutrients = AIMicronutrients(iron=1.7, calcium=30.0, magnesium=25.0, potassium=160.0, vitamin_a=0.0, vitamin_c=0.0, vitamin_d=0.0, vitamin_b12=0.0)
            health_score = 55
            summary = "Deep-fried Indian bread — high in calories and fat; best enjoyed on special occasions with aloo sabzi or chole."
            insights = [
                "High fat content from deep frying — moderate your portions.",
                "Pair with protein-rich chole for a more balanced meal.",
                "Baked alternatives are significantly healthier."
            ]

        elif visual_category == "uttapam":
            meal_name = "Vegetable Uttapam"
            foods = [
                AIFoodItem(name="Thick Rice Lentil Pancake with Veggies", estimated_quantity="2 pieces (200g)", calories=245, protein=8.0, carbohydrates=42.0, fat=5.5),
            ]
            nutrition = AINutritionTotals(calories=245, protein=8.0, carbohydrates=42.0, fat=5.5, fiber=4.0, sugar=3.5, sodium=340.0)
            micronutrients = AIMicronutrients(iron=2.0, calcium=50.0, magnesium=38.0, potassium=310.0, vitamin_a=120.0, vitamin_c=14.0, vitamin_d=0.0, vitamin_b12=0.0)
            health_score = 85
            summary = "A thick South Indian savory pancake topped with onions, tomatoes, and capsicum — nutritious and filling."
            insights = [
                "Fermented batter provides probiotics for digestive health.",
                "Vegetable toppings add Vitamin C, fiber, and antioxidants.",
                "Lower in fat than dosa — a great healthy breakfast option."
            ]

        elif visual_category == "pulao":
            meal_name = "Vegetable Pulao / Fried Rice"
            foods = [
                AIFoodItem(name="Basmati Rice Pulao with Vegetables", estimated_quantity="1.5 cups (280g)", calories=340, protein=7.5, carbohydrates=64.0, fat=7.0),
            ]
            nutrition = AINutritionTotals(calories=340, protein=7.5, carbohydrates=64.0, fat=7.0, fiber=3.5, sugar=3.0, sodium=390.0)
            micronutrients = AIMicronutrients(iron=1.8, calcium=40.0, magnesium=38.0, potassium=310.0, vitamin_a=150.0, vitamin_c=10.0, vitamin_d=0.0, vitamin_b12=0.0)
            health_score = 78
            summary = "A mildly spiced one-pot basmati rice dish with mixed vegetables — fragrant, satisfying, and moderate in calories."
            insights = [
                "Basmati rice has a lower glycemic index than regular white rice.",
                "Adding more vegetables increases fiber and micronutrient content.",
                "Pair with raita or dal for additional protein."
            ]

        elif visual_category == "halwa":
            meal_name = "Sooji Halwa (Semolina Sweet)"
            foods = [
                AIFoodItem(name="Roasted Semolina Halwa with Ghee & Sugar", estimated_quantity="1 cup (150g)", calories=415, protein=5.0, carbohydrates=60.0, fat=16.5),
            ]
            nutrition = AINutritionTotals(calories=415, protein=5.0, carbohydrates=60.0, fat=16.5, fiber=1.5, sugar=38.0, sodium=80.0)
            micronutrients = AIMicronutrients(iron=1.5, calcium=30.0, magnesium=20.0, potassium=110.0, vitamin_a=65.0, vitamin_c=0.0, vitamin_d=0.0, vitamin_b12=0.1)
            health_score = 42
            summary = "A traditional Indian sweet made from semolina, ghee, and sugar — calorie-dense and high in sugar."
            insights = [
                "High in simple sugars — consume in moderation.",
                "Ghee adds saturated fat — limit portion size.",
                "Best reserved for special occasions or festivals."
            ]

        elif visual_category == "ladoo":
            meal_name = "Besan Ladoo (Chickpea Flour Sweet)"
            foods = [
                AIFoodItem(name="Besan Ladoo", estimated_quantity="2 pieces (60g)", calories=255, protein=5.5, carbohydrates=32.0, fat=12.0),
            ]
            nutrition = AINutritionTotals(calories=255, protein=5.5, carbohydrates=32.0, fat=12.0, fiber=2.0, sugar=26.0, sodium=50.0)
            micronutrients = AIMicronutrients(iron=1.2, calcium=25.0, magnesium=22.0, potassium=170.0, vitamin_a=40.0, vitamin_c=0.0, vitamin_d=0.0, vitamin_b12=0.0)
            health_score = 48
            summary = "Traditional Indian sweets made from roasted chickpea flour and ghee — high in sugar and fat."
            insights = [
                "Besan (chickpea flour) provides protein and iron compared to refined flour sweets.",
                "High in simple sugars — best as occasional festive treats.",
                "Portion control is key due to high calorie density."
            ]

        elif visual_category == "jalebi":
            meal_name = "Jalebi (Deep-Fried Sweet)"
            foods = [
                AIFoodItem(name="Crispy Sugar-Soaked Jalebi", estimated_quantity="3 pieces (80g)", calories=290, protein=2.0, carbohydrates=56.0, fat=7.5),
            ]
            nutrition = AINutritionTotals(calories=290, protein=2.0, carbohydrates=56.0, fat=7.5, fiber=0.5, sugar=50.0, sodium=40.0)
            micronutrients = AIMicronutrients(iron=0.5, calcium=15.0, magnesium=5.0, potassium=60.0, vitamin_a=10.0, vitamin_c=0.0, vitamin_d=0.0, vitamin_b12=0.0)
            health_score = 28
            summary = "A spiral deep-fried sweet soaked in sugar syrup — extremely high in sugar and refined carbohydrates."
            insights = [
                "Very high sugar content — a diabetic-unfriendly indulgence.",
                "Minimal nutritional value beyond quick energy calories.",
                "Enjoy very rarely and in small quantities."
            ]

        elif visual_category == "gulab_jamun":
            meal_name = "Gulab Jamun (Milk Solid Sweet)"
            foods = [
                AIFoodItem(name="Sugar Syrup Soaked Gulab Jamun", estimated_quantity="2 pieces (80g)", calories=295, protein=4.5, carbohydrates=48.0, fat=9.5),
            ]
            nutrition = AINutritionTotals(calories=295, protein=4.5, carbohydrates=48.0, fat=9.5, fiber=0.2, sugar=42.0, sodium=60.0)
            micronutrients = AIMicronutrients(iron=0.4, calcium=90.0, magnesium=8.0, potassium=120.0, vitamin_a=50.0, vitamin_c=0.0, vitamin_d=0.0, vitamin_b12=0.2)
            health_score = 30
            summary = "A classic Indian festive dessert of milk solids fried and soaked in rose-flavored sugar syrup — very high in sugar."
            insights = [
                "High in simple sugars and saturated fat — festive treat only.",
                "Provides some calcium from milk solids.",
                "Limit to 1 piece for diabetics or those watching weight."
            ]

        elif visual_category == "kheer":
            meal_name = "Rice Kheer / Payasam"
            foods = [
                AIFoodItem(name="Sweet Rice Milk Pudding", estimated_quantity="1 cup (200ml)", calories=210, protein=5.5, carbohydrates=36.0, fat=5.5),
            ]
            nutrition = AINutritionTotals(calories=210, protein=5.5, carbohydrates=36.0, fat=5.5, fiber=0.5, sugar=28.0, sodium=80.0)
            micronutrients = AIMicronutrients(iron=0.5, calcium=165.0, magnesium=18.0, potassium=220.0, vitamin_a=95.0, vitamin_c=1.0, vitamin_d=0.1, vitamin_b12=0.5)
            health_score = 55
            summary = "A creamy Indian milk-based rice pudding flavored with cardamom and saffron — moderate in protein but high in sugar."
            insights = [
                "Good source of calcium and Vitamin B12 from milk.",
                "High in added sugar — consume as an occasional dessert.",
                "Reduce sugar and use low-fat milk for a healthier version."
            ]

        # ---- Global Grains & Carbs ----
        elif visual_category == "oats":
            meal_name = "Oatmeal / Overnight Oats Bowl"
            foods = [
                AIFoodItem(name="Rolled Oats (cooked)", estimated_quantity="1 cup (234g)", calories=166, protein=5.9, carbohydrates=28.1, fat=3.6),
            ]
            nutrition = AINutritionTotals(calories=166, protein=5.9, carbohydrates=28.1, fat=3.6, fiber=4.0, sugar=0.6, sodium=9.0)
            micronutrients = AIMicronutrients(iron=2.1, calcium=21.0, magnesium=63.0, potassium=164.0, vitamin_a=0.0, vitamin_c=0.0, vitamin_d=0.0, vitamin_b12=0.0)
            health_score = 93
            summary = "A whole-grain breakfast staple rich in beta-glucan fiber, iron, and magnesium — excellent for heart health and sustained energy."
            insights = [
                "Beta-glucan fiber lowers LDL cholesterol and supports heart health.",
                "Low glycemic index — keeps you full and energy-stable for hours.",
                "Add berries and nuts to boost antioxidants and healthy fats."
            ]

        elif visual_category == "bread":
            meal_name = "Whole Wheat Bread / Toast"
            foods = [
                AIFoodItem(name="Whole Wheat Bread Slices", estimated_quantity="2 slices (56g)", calories=138, protein=5.6, carbohydrates=26.4, fat=1.8),
            ]
            nutrition = AINutritionTotals(calories=138, protein=5.6, carbohydrates=26.4, fat=1.8, fiber=3.8, sugar=3.5, sodium=240.0)
            micronutrients = AIMicronutrients(iron=1.8, calcium=40.0, magnesium=28.0, potassium=130.0, vitamin_a=0.0, vitamin_c=0.0, vitamin_d=0.0, vitamin_b12=0.0)
            health_score = 78
            summary = "A convenient whole-grain staple providing complex carbohydrates, dietary fiber, and B-vitamins."
            insights = [
                "Whole wheat offers more fiber and micronutrients than white bread.",
                "Top with peanut butter or eggs to add protein.",
                "Check sodium content — some commercial breads are high in salt."
            ]

        elif visual_category == "pasta":
            meal_name = "Pasta / Noodles"
            foods = [
                AIFoodItem(name="Cooked Pasta (Regular)", estimated_quantity="1.5 cups (220g)", calories=330, protein=11.5, carbohydrates=65.0, fat=1.8),
            ]
            nutrition = AINutritionTotals(calories=330, protein=11.5, carbohydrates=65.0, fat=1.8, fiber=2.5, sugar=3.5, sodium=10.0)
            micronutrients = AIMicronutrients(iron=2.0, calcium=25.0, magnesium=32.0, potassium=183.0, vitamin_a=0.0, vitamin_c=0.0, vitamin_d=0.0, vitamin_b12=0.0)
            health_score = 72
            summary = "A carbohydrate-dense staple — nutritional value greatly depends on sauce and protein added."
            insights = [
                "Choose whole wheat pasta for doubled fiber content.",
                "Add lean protein (chicken, legumes) and vegetables for a balanced meal.",
                "Tomato-based sauces are healthier than cream-based alternatives."
            ]

        elif visual_category == "sandwich":
            meal_name = "Whole Wheat Sandwich"
            foods = [
                AIFoodItem(name="Whole Wheat Sandwich with Veggies", estimated_quantity="1 sandwich (200g)", calories=310, protein=15.0, carbohydrates=38.0, fat=10.0),
            ]
            nutrition = AINutritionTotals(calories=310, protein=15.0, carbohydrates=38.0, fat=10.0, fiber=4.5, sugar=5.0, sodium=520.0)
            micronutrients = AIMicronutrients(iron=2.5, calcium=80.0, magnesium=35.0, potassium=320.0, vitamin_a=120.0, vitamin_c=12.0, vitamin_d=0.1, vitamin_b12=0.4)
            health_score = 79
            summary = "A balanced grab-and-go meal — whole wheat bread with protein and fresh vegetables."
            insights = [
                "Good balance of protein, carbs, and fat for a quick meal.",
                "Load up on vegetable fillings to increase fiber and micronutrients.",
                "Watch sodium levels in processed deli meats and sauces."
            ]

        # ---- Dairy ----
        elif visual_category == "milk":
            meal_name = "Glass of Whole Milk"
            foods = [
                AIFoodItem(name="Full-Fat Cow's Milk", estimated_quantity="1 glass (240ml)", calories=149, protein=8.0, carbohydrates=12.0, fat=8.0),
            ]
            nutrition = AINutritionTotals(calories=149, protein=8.0, carbohydrates=12.0, fat=8.0, fiber=0.0, sugar=12.0, sodium=98.0)
            micronutrients = AIMicronutrients(iron=0.1, calcium=276.0, magnesium=24.0, potassium=322.0, vitamin_a=112.0, vitamin_c=0.0, vitamin_d=3.2, vitamin_b12=1.1)
            health_score = 85
            summary = "A complete nutrition source providing high-quality protein, calcium, Vitamin D, and B12 for bone and muscle health."
            insights = [
                "Outstanding calcium and Vitamin D for bone density.",
                "Complete protein with all essential amino acids.",
                "Choose low-fat options to reduce saturated fat intake."
            ]

        elif visual_category == "cheese":
            meal_name = "Cheese (Cheddar / Mozzarella)"
            foods = [
                AIFoodItem(name="Cheddar Cheese", estimated_quantity="30g (1 slice)", calories=113, protein=7.0, carbohydrates=0.4, fat=9.3),
            ]
            nutrition = AINutritionTotals(calories=113, protein=7.0, carbohydrates=0.4, fat=9.3, fiber=0.0, sugar=0.1, sodium=174.0)
            micronutrients = AIMicronutrients(iron=0.2, calcium=202.0, magnesium=7.0, potassium=28.0, vitamin_a=75.0, vitamin_c=0.0, vitamin_d=0.2, vitamin_b12=0.2)
            health_score = 70
            summary = "A calcium-rich dairy product with high protein — but also high in saturated fat and sodium."
            insights = [
                "Excellent calcium and phosphorus for bone health.",
                "High in saturated fat — moderate to 1-2 servings per day.",
                "Good source of Vitamin A and B12."
            ]

        elif visual_category == "butter":
            meal_name = "Butter / Makhan"
            foods = [
                AIFoodItem(name="Salted Butter", estimated_quantity="1 tablespoon (14g)", calories=102, protein=0.1, carbohydrates=0.0, fat=11.5),
            ]
            nutrition = AINutritionTotals(calories=102, protein=0.1, carbohydrates=0.0, fat=11.5, fiber=0.0, sugar=0.0, sodium=91.0)
            micronutrients = AIMicronutrients(iron=0.0, calcium=3.0, magnesium=0.3, potassium=3.0, vitamin_a=97.0, vitamin_c=0.0, vitamin_d=0.1, vitamin_b12=0.0)
            health_score = 45
            summary = "Pure dairy fat used in cooking — rich in Vitamin A but high in saturated fat."
            insights = [
                "Use sparingly — high in saturated fat and calories.",
                "Contains Vitamin A important for eye and immune health.",
                "Replace with olive oil or avocado for healthier fat options."
            ]

        # ---- Vegetables ----
        elif visual_category == "broccoli":
            meal_name = "Fresh Steamed Broccoli"
            foods = [
                AIFoodItem(name="Steamed Broccoli Florets", estimated_quantity="1 cup (156g)", calories=55, protein=3.7, carbohydrates=11.2, fat=0.6),
            ]
            nutrition = AINutritionTotals(calories=55, protein=3.7, carbohydrates=11.2, fat=0.6, fiber=5.1, sugar=2.2, sodium=64.0)
            micronutrients = AIMicronutrients(iron=1.0, calcium=62.0, magnesium=33.0, potassium=457.0, vitamin_a=567.0, vitamin_c=101.0, vitamin_d=0.0, vitamin_b12=0.0)
            health_score = 98
            summary = "A nutritional powerhouse vegetable delivering exceptional Vitamin C, Vitamin K, and cancer-fighting sulforaphane."
            insights = [
                "Provides 100%+ daily Vitamin C in a single cup serving.",
                "Rich in sulforaphane — a potent anti-cancer phytonutrient.",
                "High fiber and near-zero fat — ideal for any diet."
            ]

        elif visual_category == "carrot":
            meal_name = "Fresh Carrots / Gajar"
            foods = [
                AIFoodItem(name="Raw Carrots", estimated_quantity="2 medium (122g)", calories=50, protein=1.1, carbohydrates=11.7, fat=0.3),
            ]
            nutrition = AINutritionTotals(calories=50, protein=1.1, carbohydrates=11.7, fat=0.3, fiber=3.4, sugar=5.8, sodium=84.0)
            micronutrients = AIMicronutrients(iron=0.4, calcium=42.0, magnesium=14.0, potassium=410.0, vitamin_a=1019.0, vitamin_c=7.6, vitamin_d=0.0, vitamin_b12=0.0)
            health_score = 97
            summary = "A beta-carotene powerhouse vegetable providing exceptional Vitamin A for eye health and immune function."
            insights = [
                "Outstanding Vitamin A — one carrot meets your entire daily requirement.",
                "Natural antioxidants protect against oxidative cell damage.",
                "Low calorie, high fiber snack — great for weight management."
            ]

        elif visual_category == "potato":
            meal_name = "Boiled Potato / French Fries"
            foods = [
                AIFoodItem(name="Boiled Potato", estimated_quantity="1 medium (150g)", calories=128, protein=3.0, carbohydrates=29.0, fat=0.2),
            ]
            nutrition = AINutritionTotals(calories=128, protein=3.0, carbohydrates=29.0, fat=0.2, fiber=2.4, sugar=1.3, sodium=10.0)
            micronutrients = AIMicronutrients(iron=0.8, calcium=12.0, magnesium=27.0, potassium=535.0, vitamin_a=2.0, vitamin_c=16.6, vitamin_d=0.0, vitamin_b12=0.0)
            health_score = 76
            summary = "A nutrient-dense starchy vegetable — excellent source of potassium and Vitamin C when eaten with skin."
            insights = [
                "High potassium — more than a banana per serving.",
                "Boiling/baking retains nutrients far better than frying.",
                "Eat the skin for maximum fiber and micronutrient benefit."
            ]

        elif visual_category == "corn":
            meal_name = "Sweet Corn / Bhutta"
            foods = [
                AIFoodItem(name="Sweet Corn Kernels", estimated_quantity="1 cup (154g)", calories=132, protein=4.9, carbohydrates=29.0, fat=1.8),
            ]
            nutrition = AINutritionTotals(calories=132, protein=4.9, carbohydrates=29.0, fat=1.8, fiber=3.6, sugar=4.5, sodium=23.0)
            micronutrients = AIMicronutrients(iron=0.9, calcium=3.0, magnesium=33.0, potassium=325.0, vitamin_a=187.0, vitamin_c=9.7, vitamin_d=0.0, vitamin_b12=0.0)
            health_score = 83
            summary = "A naturally sweet grain-vegetable rich in fiber, antioxidants (lutein, zeaxanthin), and slow-digesting carbohydrates."
            insights = [
                "Lutein and zeaxanthin support eye health and reduce macular degeneration risk.",
                "Good source of B vitamins including folate.",
                "Naturally sweet — a healthier alternative to refined sugar snacks."
            ]

        # ---- Soups & Beverages ----
        elif visual_category == "soup":
            meal_name = "Vegetable / Chicken Soup"
            foods = [
                AIFoodItem(name="Hearty Vegetable Soup", estimated_quantity="1 bowl (300ml)", calories=90, protein=4.5, carbohydrates=15.0, fat=2.0),
            ]
            nutrition = AINutritionTotals(calories=90, protein=4.5, carbohydrates=15.0, fat=2.0, fiber=4.0, sugar=5.0, sodium=580.0)
            micronutrients = AIMicronutrients(iron=1.8, calcium=45.0, magnesium=28.0, potassium=440.0, vitamin_a=280.0, vitamin_c=20.0, vitamin_d=0.0, vitamin_b12=0.0)
            health_score = 88
            summary = "A warming, low-calorie meal that's hydrating and rich in vegetables, minerals, and fiber."
            insights = [
                "High hydration and low calorie — great for weight management.",
                "Vegetables provide a wide spectrum of vitamins and antioxidants.",
                "Watch sodium in canned/restaurant soups — make homemade to control salt."
            ]

        elif visual_category == "smoothie":
            meal_name = "Fruit Smoothie / Protein Shake"
            foods = [
                AIFoodItem(name="Blended Fruit Smoothie", estimated_quantity="1 glass (350ml)", calories=220, protein=8.0, carbohydrates=38.0, fat=4.5),
            ]
            nutrition = AINutritionTotals(calories=220, protein=8.0, carbohydrates=38.0, fat=4.5, fiber=4.0, sugar=24.0, sodium=80.0)
            micronutrients = AIMicronutrients(iron=0.8, calcium=150.0, magnesium=35.0, potassium=450.0, vitamin_a=120.0, vitamin_c=30.0, vitamin_d=0.5, vitamin_b12=0.5)
            health_score = 82
            summary = "A blended drink combining fruits, dairy/plant milk — convenient, nutrient-dense, and easy to customize."
            insights = [
                "Add protein powder or Greek yogurt to boost protein content.",
                "Natural sugars can be high — avoid adding extra sugar.",
                "A great post-workout recovery drink with the right ingredients."
            ]

        # ---- Sweets & Snacks ----
        elif visual_category == "chocolate":
            meal_name = "Dark Chocolate"
            foods = [
                AIFoodItem(name="Dark Chocolate (70%+ Cocoa)", estimated_quantity="1 bar (40g)", calories=216, protein=2.8, carbohydrates=18.0, fat=15.6),
            ]
            nutrition = AINutritionTotals(calories=216, protein=2.8, carbohydrates=18.0, fat=15.6, fiber=3.1, sugar=10.0, sodium=8.0)
            micronutrients = AIMicronutrients(iron=3.4, calcium=20.0, magnesium=64.0, potassium=203.0, vitamin_a=5.0, vitamin_c=0.0, vitamin_d=0.0, vitamin_b12=0.0)
            health_score = 72
            summary = "Dark chocolate at 70%+ cocoa is rich in antioxidant flavonoids, iron, and magnesium — a guilt-lighter indulgence."
            insights = [
                "Flavonoids in dark chocolate improve blood flow and heart health.",
                "Good source of iron and magnesium.",
                "Choose 70%+ cocoa and limit to 1-2 squares per day."
            ]

        elif visual_category == "icecream":
            meal_name = "Vanilla Ice Cream / Kulfi"
            foods = [
                AIFoodItem(name="Vanilla Ice Cream", estimated_quantity="1 scoop (100g)", calories=207, protein=3.5, carbohydrates=24.0, fat=11.0),
            ]
            nutrition = AINutritionTotals(calories=207, protein=3.5, carbohydrates=24.0, fat=11.0, fiber=0.5, sugar=21.0, sodium=80.0)
            micronutrients = AIMicronutrients(iron=0.1, calcium=128.0, magnesium=14.0, potassium=164.0, vitamin_a=110.0, vitamin_c=0.5, vitamin_d=0.3, vitamin_b12=0.4)
            health_score = 40
            summary = "A sweet frozen dairy dessert — high in sugar and saturated fat; best enjoyed as an occasional treat."
            insights = [
                "High in added sugars and saturated fat — portion control is crucial.",
                "Provides calcium from dairy base.",
                "Try frozen yogurt or banana nice cream for a lighter alternative."
            ]

        elif visual_category == "cookie":
            meal_name = "Cookies / Biscuits"
            foods = [
                AIFoodItem(name="Sweet Biscuits/Cookies", estimated_quantity="3 pieces (45g)", calories=200, protein=2.5, carbohydrates=28.0, fat=9.0),
            ]
            nutrition = AINutritionTotals(calories=200, protein=2.5, carbohydrates=28.0, fat=9.0, fiber=0.8, sugar=14.0, sodium=140.0)
            micronutrients = AIMicronutrients(iron=0.8, calcium=15.0, magnesium=8.0, potassium=60.0, vitamin_a=20.0, vitamin_c=0.0, vitamin_d=0.0, vitamin_b12=0.0)
            health_score = 38
            summary = "Processed sweet snacks with refined flour, sugar, and fat — low in nutritional value."
            insights = [
                "High in refined carbs and added sugars — minimal nutritional benefit.",
                "Pair with protein (nuts, milk) to reduce glycemic spike.",
                "Choose oat-based or whole-grain cookies for a slightly healthier option."
            ]

        elif visual_category == "cake":
            meal_name = "Cake / Cupcake"
            foods = [
                AIFoodItem(name="Chocolate/Vanilla Cake Slice", estimated_quantity="1 slice (100g)", calories=355, protein=5.0, carbohydrates=50.0, fat=16.0),
            ]
            nutrition = AINutritionTotals(calories=355, protein=5.0, carbohydrates=50.0, fat=16.0, fiber=1.2, sugar=35.0, sodium=280.0)
            micronutrients = AIMicronutrients(iron=1.0, calcium=50.0, magnesium=12.0, potassium=90.0, vitamin_a=60.0, vitamin_c=0.0, vitamin_d=0.0, vitamin_b12=0.1)
            health_score = 32
            summary = "A sweet baked dessert high in refined sugar and fat — a celebration treat best enjoyed occasionally."
            insights = [
                "Very high in simple sugars and saturated fat.",
                "Minimal nutritional value — purely a celebratory indulgence.",
                "Consider fruit-based desserts or smaller portions."
            ]

        # ---- Fruits (additional) ----
        elif visual_category == "papaya":
            meal_name = "Fresh Ripe Papaya"
            foods = [
                AIFoodItem(name="Fresh Papaya Chunks", estimated_quantity="1 cup (145g)", calories=62, protein=0.7, carbohydrates=15.7, fat=0.4),
            ]
            nutrition = AINutritionTotals(calories=62, protein=0.7, carbohydrates=15.7, fat=0.4, fiber=2.5, sugar=11.3, sodium=11.0)
            micronutrients = AIMicronutrients(iron=0.3, calcium=29.0, magnesium=14.0, potassium=264.0, vitamin_a=68.0, vitamin_c=88.3, vitamin_d=0.0, vitamin_b12=0.0)
            health_score = 96
            summary = "A tropical enzyme-rich fruit loaded with Vitamin C, Vitamin A, and papain — excellent for digestion."
            insights = [
                "Papain enzyme aids protein digestion and reduces bloating.",
                "Excellent Vitamin C source — one cup covers daily requirements.",
                "Low calorie and high in Vitamin A for eye and skin health."
            ]

        elif visual_category == "pomegranate":
            meal_name = "Fresh Pomegranate Seeds (Anar)"
            foods = [
                AIFoodItem(name="Pomegranate Arils", estimated_quantity="1 cup (174g)", calories=144, protein=2.9, carbohydrates=32.7, fat=2.1),
            ]
            nutrition = AINutritionTotals(calories=144, protein=2.9, carbohydrates=32.7, fat=2.1, fiber=7.0, sugar=23.8, sodium=3.0)
            micronutrients = AIMicronutrients(iron=0.5, calcium=28.0, magnesium=34.0, potassium=411.0, vitamin_a=14.0, vitamin_c=28.8, vitamin_d=0.0, vitamin_b12=0.0)
            health_score = 97
            summary = "A ruby-red superfood bursting with punicalagin antioxidants, fiber, and anti-inflammatory compounds."
            insights = [
                "Punicalagin and anthocyanin antioxidants protect heart and cellular health.",
                "High fiber content supports digestive and cardiovascular health.",
                "Known to reduce blood pressure and lower LDL cholesterol levels."
            ]

        elif visual_category == "kiwi":
            meal_name = "Fresh Green Kiwifruit"
            foods = [
                AIFoodItem(name="Fresh Kiwi Fruit", estimated_quantity="2 medium (148g)", calories=90, protein=1.8, carbohydrates=21.6, fat=0.8),
            ]
            nutrition = AINutritionTotals(calories=90, protein=1.8, carbohydrates=21.6, fat=0.8, fiber=4.4, sugar=13.4, sodium=4.0)
            micronutrients = AIMicronutrients(iron=0.6, calcium=52.0, magnesium=27.0, potassium=448.0, vitamin_a=154.0, vitamin_c=137.2, vitamin_d=0.0, vitamin_b12=0.0)
            health_score = 97
            summary = "A Vitamin C superstar — two kiwis provide nearly twice your daily Vitamin C requirement in just 90 calories."
            insights = [
                "Highest Vitamin C density of any common fruit per calorie.",
                "Improves sleep quality — studies show kiwi aids serotonin production.",
                "Rich in Vitamin K for blood clotting and bone metabolism."
            ]

        elif visual_category == "avocado":
            meal_name = "Fresh Hass Avocado Slices"
            foods = [
                AIFoodItem(name="Fresh Hass Avocado", estimated_quantity="1 medium (150g)", calories=240, protein=3.0, carbohydrates=12.0, fat=22.0),
            ]
            nutrition = AINutritionTotals(calories=240, protein=3.0, carbohydrates=12.0, fat=22.0, fiber=10.0, sugar=1.0, sodium=10.0)
            micronutrients = AIMicronutrients(iron=1.0, calcium=18.0, magnesium=43.0, potassium=708.0, vitamin_a=146.0, vitamin_c=15.0, vitamin_d=0.0, vitamin_b12=0.0)
            health_score = 94
            summary = "A nutrient-dense superfood rich in heart-healthy monounsaturated fats, potassium, and dietary fiber."
            insights = [
                "Packed with healthy monounsaturated fats that support cardiovascular wellness.",
                "High dietary fiber content aids digestive health and promotes long-lasting fullness.",
                "Rich in potassium—containing more potassium per serving than a banana."
            ]

        elif visual_category == "banana":
            meal_name = "Fresh Ripe Yellow Banana"
            foods = [
                AIFoodItem(name="Ripe Yellow Banana", estimated_quantity="1 medium (118g)", calories=105, protein=1.3, carbohydrates=27.0, fat=0.3),
            ]
            nutrition = AINutritionTotals(calories=105, protein=1.3, carbohydrates=27.0, fat=0.3, fiber=3.1, sugar=14.4, sodium=1.0)
            micronutrients = AIMicronutrients(iron=0.3, calcium=6.0, magnesium=32.0, potassium=422.0, vitamin_a=76.0, vitamin_c=10.3, vitamin_d=0.0, vitamin_b12=0.0)
            health_score = 91
            summary = "A quick, natural energy source packed with potassium, Vitamin B6, and wholesome dietary fiber."
            insights = [
                "High in digestible carbohydrates for instant pre- or post-workout energy.",
                "Rich potassium content helps regulate blood pressure and muscular electrolyte balance.",
                "Naturally low in fat and sodium-free."
            ]

        elif visual_category == "orange":
            meal_name = "Fresh Citrus Orange Slices"
            foods = [
                AIFoodItem(name="Fresh Valencia Orange", estimated_quantity="1 large (184g)", calories=86, protein=1.7, carbohydrates=21.6, fat=0.2),
            ]
            nutrition = AINutritionTotals(calories=86, protein=1.7, carbohydrates=21.6, fat=0.2, fiber=4.4, sugar=17.2, sodium=0.0)
            micronutrients = AIMicronutrients(iron=0.2, calcium=74.0, magnesium=18.0, potassium=333.0, vitamin_a=295.0, vitamin_c=97.9, vitamin_d=0.0, vitamin_b12=0.0)
            health_score = 96
            summary = "An immunity-boosting citrus fruit packed with over 100% daily Vitamin C and hydration."
            insights = [
                "Provides exceptional Vitamin C support for immune defenses and collagen synthesis.",
                "Contains dietary pectin fiber supporting gastrointestinal health.",
                "High water content promotes optimal cellular hydration."
            ]

        elif visual_category == "apple":
            meal_name = "Fresh Red Apple & Fruit Slice"
            foods = [
                AIFoodItem(name="Fresh Honeycrisp Apple", estimated_quantity="1 large (200g)", calories=104, protein=0.5, carbohydrates=27.6, fat=0.3),
                AIFoodItem(name="Fresh Blueberries", estimated_quantity="50 g", calories=29, protein=0.4, carbohydrates=7.2, fat=0.2)
            ]
            nutrition = AINutritionTotals(calories=133, protein=0.9, carbohydrates=34.8, fat=0.5, fiber=5.4, sugar=25.2, sodium=2.0)
            micronutrients = AIMicronutrients(iron=0.3, calcium=16.0, magnesium=14.0, potassium=230.0, vitamin_a=108.0, vitamin_c=14.5, vitamin_d=0.0, vitamin_b12=0.0)
            health_score = 96
            summary = "A refreshing, low-fat snack loaded with dietary fiber, natural fruit sugars, and vitamin C."
            insights = [
                "High dietary pectin fiber aids in digestion and gut health.",
                "Natural sugars provide quick, clean energy before workouts.",
                "Zero cholesterol and virtually fat-free snack option."
            ]

        elif visual_category == "mango":
            meal_name = "Fresh Sweet Alphonso Mango"
            foods = [
                AIFoodItem(name="Fresh Ripe Mango Slices", estimated_quantity="1 cup (165g)", calories=99, protein=1.4, carbohydrates=24.7, fat=0.6),
            ]
            nutrition = AINutritionTotals(calories=99, protein=1.4, carbohydrates=24.7, fat=0.6, fiber=2.6, sugar=22.5, sodium=2.0)
            micronutrients = AIMicronutrients(iron=0.3, calcium=18.0, magnesium=16.0, potassium=277.0, vitamin_a=180.0, vitamin_c=60.0, vitamin_d=0.0, vitamin_b12=0.0)
            health_score = 93
            summary = "The king of fruits, rich in Vitamin A, Vitamin C, antioxidants, and tropical sweetness."
            insights = [
                "Abundant in Beta-Carotene and Vitamin A supporting optimal eye health.",
                "High Vitamin C content strengthens natural immune defenses.",
                "Contains digestive enzymes like amylases that break down complex carbohydrates."
            ]

        elif visual_category == "grapes":
            meal_name = "Fresh Seedless Red & Green Grapes"
            foods = [
                AIFoodItem(name="Seedless Grapes", estimated_quantity="1 cup (151g)", calories=104, protein=1.1, carbohydrates=27.3, fat=0.2),
            ]
            nutrition = AINutritionTotals(calories=104, protein=1.1, carbohydrates=27.3, fat=0.2, fiber=1.4, sugar=23.4, sodium=3.0)
            micronutrients = AIMicronutrients(iron=0.5, calcium=15.0, magnesium=11.0, potassium=288.0, vitamin_a=100.0, vitamin_c=4.8, vitamin_d=0.0, vitamin_b12=0.0)
            health_score = 90
            summary = "A hydrating fruit rich in resveratrol polyphenols and cellular antioxidants."
            insights = [
                "Contains resveratrol, a potent antioxidant supporting cardiovascular health.",
                "High water content promotes natural metabolic hydration.",
                "Convenient low-fat natural snack."
            ]

        elif visual_category == "watermelon":
            meal_name = "Fresh Chilled Watermelon Cubes"
            foods = [
                AIFoodItem(name="Watermelon Cubes", estimated_quantity="2 cups (280g)", calories=85, protein=1.7, carbohydrates=21.0, fat=0.4),
            ]
            nutrition = AINutritionTotals(calories=85, protein=1.7, carbohydrates=21.0, fat=0.4, fiber=1.1, sugar=17.4, sodium=2.0)
            micronutrients = AIMicronutrients(iron=0.7, calcium=20.0, magnesium=28.0, potassium=320.0, vitamin_a=160.0, vitamin_c=23.0, vitamin_d=0.0, vitamin_b12=0.0)
            health_score = 95
            summary = "An ultra-hydrating fruit featuring 92% water, lycopene antioxidants, and L-citrulline."
            insights = [
                "Lycopene content protects against cellular oxidative stress.",
                "L-citrulline amino acid helps reduce post-workout muscle soreness.",
                "Extremely low calorie density allows generous portion sizes."
            ]

        elif visual_category == "pineapple":
            meal_name = "Fresh Golden Pineapple Chunks"
            foods = [
                AIFoodItem(name="Pineapple Chunks", estimated_quantity="1 cup (165g)", calories=82, protein=0.9, carbohydrates=21.6, fat=0.2),
            ]
            nutrition = AINutritionTotals(calories=82, protein=0.9, carbohydrates=21.6, fat=0.2, fiber=2.3, sugar=16.3, sodium=2.0)
            micronutrients = AIMicronutrients(iron=0.5, calcium=21.0, magnesium=20.0, potassium=180.0, vitamin_a=96.0, vitamin_c=78.9, vitamin_d=0.0, vitamin_b12=0.0)
            health_score = 94
            summary = "A tropical powerhouse containing bromelain digestive enzymes and vibrant Vitamin C."
            insights = [
                "Rich in bromelain, a natural proteolytic enzyme aiding protein digestion.",
                "Provides over 80% of daily recommended Vitamin C per serving.",
                "Supports anti-inflammatory metabolic pathways."
            ]

        elif visual_category == "dry_fruits":
            meal_name = "Assorted Premium Dry Fruits & Nuts Mix"
            foods = [
                AIFoodItem(name="Raw Almonds & Cashews", estimated_quantity="30 g", calories=172, protein=5.8, carbohydrates=7.5, fat=14.2),
                AIFoodItem(name="Walnut Kernels & Pistachios", estimated_quantity="20 g", calories=128, protein=3.2, carbohydrates=3.8, fat=12.1),
                AIFoodItem(name="Dried Raisins & Seedless Dates", estimated_quantity="25 g", calories=75, protein=0.8, carbohydrates=19.2, fat=0.1)
            ]
            nutrition = AINutritionTotals(calories=375, protein=9.8, carbohydrates=30.5, fat=26.4, fiber=5.2, sugar=17.5, sodium=8.0)
            micronutrients = AIMicronutrients(iron=2.8, calcium=95.0, magnesium=115.0, potassium=520.0, vitamin_a=45.0, vitamin_c=1.2, vitamin_d=0.0, vitamin_b12=0.0)
            health_score = 95
            summary = "A nutrient-dense superfood mix of almonds, cashews, walnuts, raisins, and dates packed with healthy fats, iron, and fiber."
            insights = [
                "Provides essential Omega-3 & Omega-6 fatty acids supporting brain and heart vitality.",
                "High plant-based protein and fiber deliver sustained, long-lasting energy.",
                "Loaded with magnesium, potassium, and plant antioxidants."
            ]

        elif visual_category == "mixed_fruits":
            meal_name = "Fresh Seasonal Fruit Medley Bowl"
            foods = [
                AIFoodItem(name="Sliced Apples & Bananas", estimated_quantity="1 cup (140g)", calories=105, protein=1.1, carbohydrates=26.5, fat=0.3),
                AIFoodItem(name="Fresh Berries & Orange Segments", estimated_quantity="1 cup (120g)", calories=55, protein=0.9, carbohydrates=13.2, fat=0.2)
            ]
            nutrition = AINutritionTotals(calories=160, protein=2.0, carbohydrates=39.7, fat=0.5, fiber=5.8, sugar=28.5, sodium=3.0)
            micronutrients = AIMicronutrients(iron=0.6, calcium=35.0, magnesium=28.0, potassium=410.0, vitamin_a=210.0, vitamin_c=85.0, vitamin_d=0.0, vitamin_b12=0.0)
            health_score = 97
            summary = "A colorful, vibrant fruit platter brimming with bioflavonoids, dietary fiber, and natural hydration."
            insights = [
                "Diverse array of antioxidants protecting cellular DNA from oxidative damage.",
                "Rich in dietary fiber promoting gut microbiota diversity.",
                "Naturally sweet and 100% fat-free snack."
            ]

        elif visual_category == "egg":
            meal_name = "Whole Organic Boiled Eggs"
            foods = [
                AIFoodItem(name="Hard Boiled Eggs", estimated_quantity="2 large (100g)", calories=155, protein=12.6, carbohydrates=1.1, fat=10.6),
            ]
            nutrition = AINutritionTotals(calories=155, protein=12.6, carbohydrates=1.1, fat=10.6, fiber=0.0, sugar=0.6, sodium=124.0)
            micronutrients = AIMicronutrients(iron=1.2, calcium=50.0, magnesium=12.0, potassium=126.0, vitamin_a=160.0, vitamin_c=0.0, vitamin_d=2.0, vitamin_b12=1.1)
            health_score = 92
            summary = "A highly digestible, complete protein source rich in essential choline, lutein, and B-vitamins."
            insights = [
                "Complete protein with an optimal amino acid score for muscle maintenance.",
                "Rich source of choline, vital for brain health and cognitive performance.",
                "Contains zero sugar and minimal carbohydrates."
            ]

        elif visual_category == "almonds":
            meal_name = "Raw Whole Almonds & Mixed Nuts"
            foods = [
                AIFoodItem(name="Raw Whole Almonds", estimated_quantity="50 g (approx. 35 nuts)", calories=289, protein=10.6, carbohydrates=10.8, fat=24.9),
            ]
            nutrition = AINutritionTotals(calories=289, protein=10.6, carbohydrates=10.8, fat=24.9, fiber=6.2, sugar=2.1, sodium=1.0)
            micronutrients = AIMicronutrients(iron=1.9, calcium=135.0, magnesium=134.0, potassium=365.0, vitamin_a=0.0, vitamin_c=0.0, vitamin_d=0.0, vitamin_b12=0.0)
            health_score = 95
            summary = "A superfood snack packed with healthy monounsaturated fats, dietary fiber, magnesium, and Vitamin E."
            insights = [
                "High in monounsaturated fats that support heart health and cholesterol balance.",
                "Rich in Vitamin E, a potent antioxidant supporting skin and cellular health.",
                "High fiber and protein content promote long-lasting satiety between meals."
            ]

        elif visual_category == "salad":
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
                "Low in simple sugars, making it great for blood sugar control."
            ]

        elif visual_category == "salmon":
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
                "Quinoa provides a complete plant protein profile and complex carbohydrates."
            ]

        elif visual_category == "pizza":
            meal_name = "Pepperoni Pizza Slice"
            foods = [
                AIFoodItem(name="Pepperoni Pizza (Thin Crust)", estimated_quantity="2 slices (approx. 180g)", calories=580, protein=24.0, carbohydrates=64.0, fat=26.0),
            ]
            nutrition = AINutritionTotals(calories=580, protein=24.0, carbohydrates=64.0, fat=26.0, fiber=2.5, sugar=6.0, sodium=1150.0)
            micronutrients = AIMicronutrients(iron=2.1, calcium=310.0, magnesium=35.0, potassium=240.0, vitamin_a=95.0, vitamin_c=2.0, vitamin_d=0.5, vitamin_b12=1.4)
            health_score = 45
            summary = "A calorie-dense meal with high sodium and saturated fat content, but a decent serving of calcium and protein."
            insights = [
                "High sodium level (approx. 50% of daily recommended limit).",
                "Good protein and calcium source from cheese."
            ]

        # ---- Unknown / Non-food fallback ----
        else:
            if image_data:
                # Image uploaded but color analysis could not confidently identify food.
                # Treat as unrecognized rather than guessing a random fruit.
                meal_name = "Non-Food / Unrecognized Image 📸"
                foods = [
                    AIFoodItem(name="Not a food item", estimated_quantity="N/A", calories=0, protein=0.0, carbohydrates=0.0, fat=0.0),
                ]
                nutrition = AINutritionTotals(calories=0, protein=0.0, carbohydrates=0.0, fat=0.0, fiber=0.0, sugar=0.0, sodium=0.0)
                micronutrients = AIMicronutrients(iron=0.0, calcium=0.0, magnesium=0.0, potassium=0.0, vitamin_a=0.0, vitamin_c=0.0, vitamin_d=0.0, vitamin_b12=0.0)
                health_score = 0
                summary = "The uploaded image could not be identified as a food item. No nutritional data is available. Please type the food name in the description box, or configure a Gemini API key in backend/.env for real AI-powered food photo recognition."
                insights = [
                    "💡 Type the food name in the description box (e.g. 'banana', 'idli', 'biryani') for accurate results.",
                    "💡 For real photo recognition of any food worldwide, add your Gemini API key: backend/.env → AI_API_KEY=your_key",
                    "⚠️ No nutrition data was recorded — this image was not recognized as food."
                ]
            else:
                food_label = (description or filename or "Unknown Food").strip().title()
                meal_name = f"{food_label} (Not in Database)"
                foods = [AIFoodItem(name=food_label, estimated_quantity="N/A", calories=0, protein=0.0, carbohydrates=0.0, fat=0.0)]
                nutrition = AINutritionTotals(calories=0, protein=0.0, carbohydrates=0.0, fat=0.0, fiber=0.0, sugar=0.0, sodium=0.0)
                micronutrients = AIMicronutrients(iron=0.0, calcium=0.0, magnesium=0.0, potassium=0.0, vitamin_a=0.0, vitamin_c=0.0, vitamin_d=0.0, vitamin_b12=0.0)
                health_score = 0
                summary = f"'{food_label}' was not found in the local food database. No nutritional data is available. Configure a Gemini API key for accurate results on any food worldwide."
                insights = [
                    f"💡 '{food_label}' is not in the offline food library. Try common names like 'idli', 'banana', 'chicken'.",
                    "💡 Add AI_API_KEY=your_gemini_key in backend/.env for real-time analysis of any food.",
                    "⚠️ No nutrition data was recorded for this entry."
                ]

        if image_data and not meal_name.endswith("📸"):
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
            
        # Configure Gemini with Windows SSL trust and REST transport
        api_key = settings.AI_API_KEY
        if api_key and "YOUR_GEMINI" not in api_key:
            try:
                import truststore
                truststore.inject_into_ssl()
            except Exception:
                pass

            try:
                genai.configure(api_key=api_key, transport="rest")
            except Exception:
                genai.configure(api_key=api_key)

            self.model = None
            for model_name in ["gemini-3.5-flash", "gemini-3.6-flash", "gemini-3.8-flash", "gemini-flash-latest", "gemini-3.1-flash-lite"]:
                try:
                    self.model = genai.GenerativeModel(model_name)
                    break
                except Exception:
                    continue
        else:
            self.model = None

    async def analyze_meal(
        self, 
        description: Optional[str] = None, 
        image_data: Optional[bytes] = None, 
        mime_type: Optional[str] = None,
        filename: Optional[str] = None
    ) -> AIAnalysisResult:
        if not settings.AI_API_KEY or not self.model or "YOUR_GEMINI" in settings.AI_API_KEY:
            # Fallback to mock provider automatically if API key is not configured
            mock = MockAIProvider()
            return await mock.analyze_meal(description, image_data, mime_type, filename=filename)
            
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
            
        models_to_try = ["gemini-3.5-flash", "gemini-3.6-flash", "gemini-3.1-flash-lite", "gemini-3.5-flash-lite", "gemini-3.8-flash"]
        last_error = None
        for m_name in models_to_try:
            try:
                active_model = genai.GenerativeModel(m_name)
                response = active_model.generate_content(contents)
                response_text = response.text
                json_data = self._extract_json(response_text)
                return AIAnalysisResult(**json_data)
            except Exception as e:
                last_error = e
                continue

        # Fallback to Mock provider if all AI models fail or are rate-limited
        print(f"Gemini API failure: {str(last_error)}. Falling back to MockAIProvider.")
        mock = MockAIProvider()
        fallback_result = await mock.analyze_meal(description, image_data, mime_type, filename=filename)
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
    if settings.AI_API_KEY and "YOUR_GEMINI" not in settings.AI_API_KEY and settings.AI_PROVIDER.lower() == "gemini":
        return GeminiAIProvider()
    return MockAIProvider()

