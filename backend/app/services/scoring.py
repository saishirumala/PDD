def calculate_health_score(
    calories: int,
    protein: float,
    carbohydrates: float,
    fat: float,
    fiber: float,
    sugar: float,
    sodium: float
) -> int:
    """
    Calculates a transparent, rule-based nutritional health score between 10 and 100.
    
    Factors considered:
    - Protein density (positive)
    - Fiber content (positive)
    - Sugar level (negative)
    - Sodium density (negative)
    - Balance of macronutrients
    """
    # Start with a base score of 70
    score = 70
    
    # 1. Protein Bonus (target: > 15% of calories or general high intake)
    # 1g protein = 4 kcal
    protein_kcal = protein * 4
    if calories > 0:
        protein_ratio = protein_kcal / calories
        if protein_ratio >= 0.25:
            score += 12
        elif protein_ratio >= 0.15:
            score += 8
        elif protein_ratio >= 0.08:
            score += 3
    else:
        if protein > 25:
            score += 10
        elif protein > 12:
            score += 5

    # 2. Fiber Bonus (excellent indicator of vegetables/grains)
    if fiber >= 8:
        score += 12
    elif fiber >= 5:
        score += 8
    elif fiber >= 2.5:
        score += 4
        
    # 3. Sugar Penalty (excess simple sugars are detrimental)
    if sugar > 25:
        score -= 20
    elif sugar > 15:
        score -= 10
    elif sugar > 8:
        score -= 4
    elif sugar <= 3:
        score += 5 # low sugar bonus

    # 4. Sodium Penalty (excess sodium causes cardiovascular concerns)
    # Sodium is in mg. Standard target is < 2300mg/day, ideally < 1500mg.
    # Per meal, we want < 600mg.
    if sodium > 1200:
        score -= 20
    elif sodium > 800:
        score -= 12
    elif sodium > 500:
        score -= 5
    elif sodium < 200:
        score += 4 # low sodium bonus

    # 5. Saturated Fat/Calorie Density check
    # If fat is very high relative to calories (fat = 9 kcal/g)
    fat_kcal = fat * 9
    if calories > 0:
        fat_ratio = fat_kcal / calories
        if fat_ratio > 0.45: # More than 45% calories from fat
            score -= 8
        elif fat_ratio < 0.15: # Too low fat
            score -= 3
            
    # Cap score between 10 and 100
    return max(10, min(100, int(score)))
