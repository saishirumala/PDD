from app.models import WaterLog, User
from datetime import datetime, timedelta

def test_log_water_success(client, auth_headers, db):
    # Log 250ml
    response = client.post(
        "/api/water",
        json={"amount_ml": 250},
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["amount_ml"] == 250
    assert "id" in data
    assert "logged_at" in data

    # Verify in DB
    log = db.query(WaterLog).filter(WaterLog.id == data["id"]).first()
    assert log is not None
    assert log.amount_ml == 250


def test_log_water_validation_error(client, auth_headers):
    # Log negative value
    response = client.post(
        "/api/water",
        json={"amount_ml": -10},
        headers=auth_headers
    )
    assert response.status_code == 422

    # Log too high value
    response = client.post(
        "/api/water",
        json={"amount_ml": 20000},
        headers=auth_headers
    )
    assert response.status_code == 422


def test_get_water_today_empty(client, auth_headers):
    response = client.get("/api/water/today", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total_ml"] == 0
    assert data["goal_ml"] == 2000
    assert data["logs"] == []


def test_get_water_today_with_logs(client, auth_headers, db):
    user = db.query(User).filter(User.email == "testuser@example.com").first()

    # Create logs: one today, one yesterday
    log_today = WaterLog(user_id=user.id, amount_ml=500, logged_at=datetime.utcnow())
    log_yesterday = WaterLog(user_id=user.id, amount_ml=750, logged_at=datetime.utcnow() - timedelta(days=1))

    db.add_all([log_today, log_yesterday])
    db.commit()

    # Query today's summary
    response = client.get("/api/water/today", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total_ml"] == 500  # only log_today should count
    assert len(data["logs"]) == 1
    assert data["logs"][0]["amount_ml"] == 500


def test_delete_water_log_success(client, auth_headers, db):
    user = db.query(User).filter(User.email == "testuser@example.com").first()
    log = WaterLog(user_id=user.id, amount_ml=250)
    db.add(log)
    db.commit()

    # Delete
    response = client.delete(f"/api/water/{log.id}", headers=auth_headers)
    assert response.status_code == 200
    assert "deleted successfully" in response.json()["detail"]

    # Verify not in DB
    assert db.query(WaterLog).filter(WaterLog.id == log.id).first() is None


def test_delete_water_log_not_found(client, auth_headers):
    response = client.delete("/api/water/9999", headers=auth_headers)
    assert response.status_code == 404


def test_delete_water_log_forbidden(client, auth_headers, db):
    # Register another user
    other_user = User(name="Other User", email="other@example.com", password_hash="dummyhash")
    db.add(other_user)
    db.commit()
    db.refresh(other_user)

    # Log for other user
    log = WaterLog(user_id=other_user.id, amount_ml=500)
    db.add(log)
    db.commit()

    # Try to delete using testuser's auth_headers
    response = client.delete(f"/api/water/{log.id}", headers=auth_headers)
    assert response.status_code == 403
