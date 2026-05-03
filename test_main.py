import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool # ВАЖНО

from main import app, get_db 
from database import Base 
import models 

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool, 
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    print(f"\nОбнаруженные таблицы: {Base.metadata.tables.keys()}")
    
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_register_user():
    response = client.post("/auth/register", json={"username": "newuser", "password": "testpass"})
    assert response.status_code == 200
    assert response.json()["username"] == "newuser"

def test_register_existing_user():
    client.post("/auth/register", json={"username": "duplicate", "password": "password"})
    response = client.post("/auth/register", json={"username": "duplicate", "password": "password"})
    assert response.status_code == 400

def test_login_user():
    client.post("/auth/register", json={"username": "loginuser", "password": "correct_password"})
    
    response = client.post("/auth/login", json={"username": "loginuser", "password": "correct_password"})
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_get_users():
    client.post("/auth/register", json={"username": "listuser", "password": "password"})
    
    response = client.get("/users/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0

def test_create_and_get_location():
    response = client.post("/locations/", json={"name": "Main Pool", "capacity": 50})
    assert response.status_code == 200
    loc_id = response.json()["id"]
    
    res_get = client.get("/locations/")
    assert res_get.status_code == 200
    assert any(loc["id"] == loc_id for loc in res_get.json())

def test_delete_nonexistent_location():
    response = client.delete("/locations/9999")
    assert response.status_code == 404

def test_optimize_schedule():
    response = client.post("/optimize-schedule/")
    assert response.status_code == 200
    assert response.json()["status"] == "optimized"