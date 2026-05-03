# Проект: Разработка веб-приложения на FastAPI
API для автоматизации работы бассейна, включая управление пользователями, распределение тренировочных сессий и оптимизацию расписания

Выполнила: Студеникина Анастасия

## Предметная область

- Управление ресурсами: контроль занятости и вместимости дорожек бассейна 
- Безопасность: разграничение доступа через JWT-токены
- Планирование: создание тренировочных программ и автоматическое назначение персонала

## Структура файлов

- ``main.py``- Инициализация приложения и основные эндпоинты
- ``auth.py``- Логика аутентификации и генерации токенов
- ``models.py`` и ``schemas.py``- Описание таблиц БД и схем валидации Pydantic
- ``database.py``- Настройка подключения к SQLAlchemy

## Создание структуры проекта

```
mkdir pool_api
cd pool_api
```

## Устанавливаем зависимости
```
pip install -r requirements.txt
```

## Запускаем тесты
```
pytest --cov=. test_main.py
```

## Запускаем сервер
```
uvicorn main:app --reload
```

## Создаем истоию в git

```
git init
git branch -M main
git add models.py database.py schemas.py
git commit -m "feat: init db and basic models"
git add auth.py main.py requirements.txt
git commit -m "feat: implement JWT auth and scheduling algorithm"
git add Dockerfile docker-compose.yml
git commit -m "chore: add docker compose infrastructure"
git add test_main.py pylint.txt README.md
git commit -m "test: add TestClient scenarios and docs"
```

## Запускаем контейнеры

```
docker-compose up -d --build
```

## Пушим все в git

```
git remote add origin https://github.com/AnastasiiaStu/pool_api.git
git push -u origin main
```

## Останавливаем контейнер

```
docker-compose down -v
```
