def test_analyze_description_only_success(client, auth_headers):
    response = client.post(
        "/api/analyze",
        data={"description": "I had a grilled chicken bowl with rice and avocado"},
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert "nutrition" in data
    assert "foods" in data
    assert "insight" in data
    assert data["nutrition"]["calories"] > 0
    # Verified it matched chicken keyword in MockAIProvider
    assert "Chicken" in data["meal_name"]
    assert len(data["foods"]) > 0


def test_analyze_empty_inputs_fails(client, auth_headers):
    response = client.post(
        "/api/analyze",
        data={},
        headers=auth_headers
    )
    assert response.status_code == 400
    assert "must provide either" in response.json()["detail"]


def test_analyze_invalid_image_format_fails(client, auth_headers):
    # Uploading a mock file that is text/plain
    files = {"image": ("test.txt", b"dummy content", "text/plain")}
    response = client.post(
        "/api/analyze",
        data={"description": "Salad"},
        files=files,
        headers=auth_headers
    )
    assert response.status_code == 400
    assert "Unsupported file format" in response.json()["detail"]


def test_dashboard_today_aggregation(client, auth_headers):
    # Log a meal first
    client.post(
        "/api/analyze",
        data={"description": "pizza slice"},
        headers=auth_headers
    )
    
    # Check dashboard today
    response = client.get("/api/dashboard/today", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["meals_count"] == 1
    assert data["today"]["calories"] == 670 # Matches pizza in MockAIProvider
    assert len(data["meals"]) == 1
