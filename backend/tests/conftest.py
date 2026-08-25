import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os
import shutil

# Make sure we import app after setting environment variables
os.environ["DATABASE_URL"] = "sqlite://" # In-memory database for testing
os.environ["SECRET_KEY"] = "test_secret_key_1234567890_test_secret_key"
os.environ["AI_PROVIDER"] = "mock"
os.environ["AI_API_KEY"] = ""

from app.main import app
from app.database import Base, get_db
from app.utils.security import get_password_hash

# Setup in-memory SQLite database engine
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db():
    # Setup connection per test to ensure isolation
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass
            
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def auth_headers(client, db):
    # Register and login a default test user
    email = "testuser@example.com"
    password = "Password123"
    name = "Test User"
    
    # Hash password and create record
    hashed_password = get_password_hash(password)
    from app.models import User
    user = User(name=name, email=email, password_hash=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Login to get token
    response = client.post("/api/auth/login", json={"email": email, "password": password})
    token = response.json()["access_token"]
    
    return {"Authorization": f"Bearer {token}"}
