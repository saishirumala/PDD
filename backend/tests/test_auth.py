def test_register_user(client):
    response = client.post(
        "/api/auth/register",
        json={"name": "Alice Smith", "email": "alice@example.com", "password": "securepassword"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Alice Smith"
    assert data["email"] == "alice@example.com"
    assert "password_hash" not in data


def test_register_duplicate_email(client):
    # First register
    client.post(
        "/api/auth/register",
        json={"name": "Alice Smith", "email": "alice@example.com", "password": "securepassword"}
    )
    # Register duplicate
    response = client.post(
        "/api/auth/register",
        json={"name": "Alice Alternate", "email": "alice@example.com", "password": "otherpassword"}
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_login_success(client):
    # Register first
    client.post(
        "/api/auth/register",
        json={"name": "Bob Jones", "email": "bob@example.com", "password": "bobpassword"}
    )
    # Login
    response = client.post(
        "/api/auth/login",
        json={"email": "bob@example.com", "password": "bobpassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client):
    response = client.post(
        "/api/auth/login",
        json={"email": "nonexistent@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert "Incorrect email" in response.json()["detail"]


def test_read_user_me(client, auth_headers):
    response = client.get("/api/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "testuser@example.com"
    assert data["name"] == "Test User"


def test_read_user_me_unauthorized(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401
