"""Интеграционные тесты для FastAPI приложения"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base
from main import app, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool, 
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    """Переопределение зависимости БД для тестов"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    """Фикстура для создания и очистки БД перед каждым тестом"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def get_auth_headers():
    """Хелпер для получения заголовков с токеном"""
    client.post("/auth/register", json={"username": "testuser", "password": "testpass"})
    response = client.post("/auth/login", json={"username": "testuser", "password": "testpass"})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

# Тесты Auth 
def test_register_user():
    """Тест успешной регистрации"""
    response = client.post("/auth/register", json={"username": "newuser", "password": "testpass"})
    assert response.status_code == 200
    assert response.json()["username"] == "newuser"

def test_register_existing_user():
    """Тест регистрации существующего пользователя"""
    client.post("/auth/register", json={"username": "duplicate", "password": "password"})
    response = client.post("/auth/register", json={"username": "duplicate", "password": "password"})
    assert response.status_code == 400

def test_login_user():
    """Тест успешной авторизации"""
    client.post("/auth/register", json={"username": "loginuser", "password": "correct_password"})
    response = client.post("/auth/login", json={"username": "loginuser", "password": "correct_password"})
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_wrong_password():
    """Тест авторизации с неверным паролем"""
    client.post("/auth/register", json={"username": "loginuser", "password": "correct_password"})
    response = client.post("/auth/login", json={"username": "loginuser", "password": "wrong_pass"})
    assert response.status_code == 401

# Тесты Users 
def test_get_users():
    """Тест получения списка пользователей"""
    headers = get_auth_headers()
    response = client.get("/users/", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_get_user_by_id():
    """Тест получения пользователя по ID"""
    headers = get_auth_headers()
    response = client.get("/users/1", headers=headers)
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"

def test_delete_user():
    """Тест удаления пользователя"""
    headers = get_auth_headers()
    response = client.delete("/users/1", headers=headers)
    assert response.status_code == 200

# Тесты Locations 
def test_create_and_get_location():
    """Тест создания локации."""
    headers = get_auth_headers()
    response = client.post("/locations/", json={"name": "Main Pool", "capacity": 50}, headers=headers)
    assert response.status_code == 200
    
    res_get = client.get("/locations/", headers=headers)
    assert any(loc["name"] == "Main Pool" for loc in res_get.json())

def test_put_location():
    """Тест обновления локации"""
    headers = get_auth_headers()
    client.post("/locations/", json={"name": "Pool", "capacity": 10}, headers=headers)
    response = client.put("/locations/1", json={"name": "Updated Pool", "capacity": 20}, headers=headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Pool"

def test_delete_nonexistent_location():
    """Тест удаления несуществующей локации"""
    headers = get_auth_headers()
    response = client.delete("/locations/9999", headers=headers)
    assert response.status_code == 404

# Тесты Sessions & Optimization 
def test_delete_session():
    """Тест удаления сессии."""
    headers = get_auth_headers()
    client.post("/locations/", json={"name": "Main Pool", "capacity": 50}, headers=headers)
    client.post("/sessions/", json={"location_id": 1, "program_name": "Swim"}, headers=headers)
    
    response = client.delete("/sessions/1", headers=headers)
    assert response.status_code == 200

def test_optimize_schedule():
    """Тест алгоритма оптимизации расписания"""
    headers = get_auth_headers()
    # Создаем локацию и 2 сессии без тренеров
    client.post("/locations/", json={"name": "Main Pool", "capacity": 50}, headers=headers)
    client.post("/sessions/", json={"location_id": 1, "program_name": "Swim 1"}, headers=headers)
    client.post("/sessions/", json={"location_id": 1, "program_name": "Swim 2"}, headers=headers)

    response = client.post("/optimize-schedule/", headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "optimized"
    assert response.json()["scheduled_trainers"] == 2