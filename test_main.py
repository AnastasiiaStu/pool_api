import pytest
from fastapi.testclient import TestClient
from main import app
from auth import create_access_token

client = TestClient(app)

# Фикстура для получения токена админа
@pytest.fixture
def admin_token():
    return create_access_token(data={"sub": "admin", "role": "admin"})

def test_optimization_algorithm(admin_token):
    """Проверка бизнес-алгоритма: нагрузка должна распределяться равномерно"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = {
        "demands": [
            {"program": "Детская группа", "count": 5}, # Тренера: Иван, Марина
            {"program": "Аквааэробика", "count": 1}    # Тренера: Александра, Екатерина
        ]
    }
    
    response = client.post("/optimize-schedule/", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    
    # 5 детских групп должны распределиться как 3 на одного и 2 на другого
    workloads = data["final_workload_hours"]
    assert workloads["Иван"] + workloads["Марина"] == 5
    assert abs(workloads["Иван"] - workloads["Марина"]) <= 1 # Проверка баланса
    
    # Аквааэробика: 1 час должен уйти любому из двух
    assert workloads["Александра"] + workloads["Екатерина"] == 1

def test_unauthorized_access():
    """Тест защиты эндпоинта (без токена должен быть 401)"""[cite: 4]
    response = client.post("/optimize-schedule/", json={"demands": []})
    assert response.status_code == 401