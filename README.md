# Проект: Разработка веб-приложения на FastAPI
API для управления бассейном

Выполнила: Студеникина Анастасия

## Создание структуры проекта

```
mkdir pool_api
cd pool_api
```

## Устанавливаем зависимости
```
pip install -r requirements.txt
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