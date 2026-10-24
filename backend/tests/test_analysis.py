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
    assert data["today"]["calories"] == 580 # Matches pizza in MockAIProvider
    assert len(data["meals"]) == 1


def test_analyze_avocado_image_success(client, auth_headers):
    # Mock JPEG image bytes
    mock_jpg = b"\xFF\xD8\xFF\xE0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00\xFF\xDB\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\x09\x09\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.' \",#\x1c\x1c(7),01444\x1f'9=82<.342\xFF\xC0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xFF\xC4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\n\x0b\xFF\xDA\x00\x08\x01\x01\x00\x00?\x00\xbf\x00\xFF\xD9"
    files = {"image": ("avocado.jpg", mock_jpg, "image/jpeg")}
    response = client.post(
        "/api/analyze",
        files=files,
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert "Avocado" in data["meal_name"]
    assert data["nutrition"]["calories"] == 240


def test_analyze_banana_image_success(client, auth_headers):
    mock_jpg = b"\xFF\xD8\xFF\xE0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00\xFF\xDB\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\x09\x09\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.' \",#\x1c\x1c(7),01444\x1f'9=82<.342\xFF\xC0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xFF\xC4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\n\x0b\xFF\xDA\x00\x08\x01\x01\x00\x00?\x00\xbf\x00\xFF\xD9"
    files = {"image": ("yellow_banana.jpg", mock_jpg, "image/jpeg")}
    response = client.post(
        "/api/analyze",
        files=files,
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert "Banana" in data["meal_name"]
    assert data["nutrition"]["calories"] == 105


def test_analyze_avacado_typo_success(client, auth_headers):
    response = client.post(
        "/api/analyze",
        data={"description": "avacado"},
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert "Avocado" in data["meal_name"]
    assert data["nutrition"]["calories"] == 240


def test_analyze_dry_fruits_success(client, auth_headers):
    response = client.post(
        "/api/analyze",
        data={"description": "dry fruits"},
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert "Dry Fruits" in data["meal_name"]
    assert data["nutrition"]["calories"] > 0
    assert len(data["foods"]) >= 1


def test_analyze_fruits_image_upload(client, auth_headers):
    mock_jpg = b"\xFF\xD8\xFF\xE0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00\xFF\xDB\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\x09\x09\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.' \",#\x1c\x1c(7),01444\x1f'9=82<.342\xFF\xC0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xFF\xC4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\n\x0b\xFF\xDA\x00\x08\x01\x01\x00\x00?\x00\xbf\x00\xFF\xD9"
    files = {"image": ("mixed_fruits.jpg", mock_jpg, "image/jpeg")}
    response = client.post(
        "/api/analyze",
        data={"description": "fruit"},
        files=files,
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert "Fruit" in data["meal_name"] or "Fruit" in str(data["foods"])
    assert data["nutrition"]["calories"] > 0


