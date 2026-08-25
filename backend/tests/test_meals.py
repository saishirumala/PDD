from app.models import Meal, Nutrition, MealInsight, Food, Micronutrient, User

def test_get_meals_empty(client, auth_headers):
    response = client.get("/api/meals", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_create_and_get_meal_details(client, auth_headers, db):
    # Retrieve user first to associate correctly
    user = db.query(User).filter(User.email == "testuser@example.com").first()
    
    # Manually seed a meal
    meal = Meal(user_id=user.id, meal_name="Test Salmon Plate", description="Salmon and salad")
    db.add(meal)
    db.flush()
    
    nutrition = Nutrition(meal_id=meal.id, calories=400, protein=30, carbohydrates=10, fat=15, fiber=3, sugar=2, sodium=300)
    micro = Micronutrient(meal_id=meal.id, iron=1, calcium=2, magnesium=3, potassium=4, vitamin_a=5, vitamin_c=6, vitamin_d=7, vitamin_b12=8)
    insight = MealInsight(meal_id=meal.id, health_score=90, summary="Good test meal", recommendations=["Keep eating test salmon"])
    food = Food(meal_id=meal.id, name="Salmon", estimated_quantity="150g", calories=300, protein=25, carbohydrates=0, fat=12)
    
    db.add_all([nutrition, micro, insight, food])
    db.commit()

    # Query list
    response = client.get("/api/meals", headers=auth_headers)
    assert response.status_code == 200
    meals_list = response.json()
    assert len(meals_list) == 1
    assert meals_list[0]["meal_name"] == "Test Salmon Plate"

    # Query details
    detail_response = client.get(f"/api/meals/{meal.id}", headers=auth_headers)
    assert detail_response.status_code == 200
    meal_detail = detail_response.json()
    assert meal_detail["meal_name"] == "Test Salmon Plate"
    assert meal_detail["nutrition"]["calories"] == 400
    assert meal_detail["insight"]["health_score"] == 90
    assert len(meal_detail["foods"]) == 1


def test_delete_meal(client, auth_headers, db):
    user = db.query(User).filter(User.email == "testuser@example.com").first()
    
    meal = Meal(user_id=user.id, meal_name="To Delete", description="To delete description")
    db.add(meal)
    db.flush()
    nutrition = Nutrition(meal_id=meal.id, calories=200, protein=10, carbohydrates=20, fat=5, fiber=1, sugar=5, sodium=100)
    insight = MealInsight(meal_id=meal.id, health_score=50, summary="Okay meal", recommendations=[])
    db.add_all([nutrition, insight])
    db.commit()

    # Delete request
    delete_response = client.delete(f"/api/meals/{meal.id}", headers=auth_headers)
    assert delete_response.status_code == 200
    assert "deleted successfully" in delete_response.json()["detail"]

    # Verify deleted in database
    assert db.query(Meal).filter(Meal.id == meal.id).first() is None
    assert db.query(Nutrition).filter(Nutrition.meal_id == meal.id).first() is None


def test_update_profile_goals(client, auth_headers):
    # Update goals
    update_response = client.put(
        "/api/profile",
        json={
            "calorie_goal": 2500,
            "protein_goal": 180.0,
            "carbs_goal": 280.0,
            "fat_goal": 75.0,
            "fiber_goal": 35.0
        },
        headers=auth_headers
    )
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["calorie_goal"] == 2500
    assert data["protein_goal"] == 180.0
    assert data["fiber_goal"] == 35.0
