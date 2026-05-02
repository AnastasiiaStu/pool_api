"""
Основной модуль API бассейна. Содержит эндпоинты и бизнес-логику.
"""
from datetime import timedelta
from typing import List

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from database import engine, get_db, Base
from models import Location, User, PoolSession, Booking
from schemas import (
    UserCreate, UserResponse, LocationCreate, LocationResponse,
    SessionCreate, SessionResponse, BookingCreate, BookingResponse
)
from auth import (
    get_password_hash, verify_password, create_access_token, require_admin
)

app = FastAPI(title="Pool Booking API", description="API для бассейна")

PROGRAM_RULES = {
    "Свободное плавание": {
        "trainers": [None, ""], "price_single": 500,
        "price_monthly": 5000, "min_age": 6, "max_age": 999
    },
    "Детская группа": {
        "trainers": ["Иван", "Марина"], "price_single": 300,
        "price_monthly": 3000, "min_age": 3, "max_age": 14
    },
    "Спортивная группа": {
        "trainers": ["Илья", "Ольга"], "price_single": 1000,
        "price_monthly": 10000, "min_age": 12, "max_age": 25
    },
    "Аквааэробика": {
        "trainers": ["Александра", "Екатерина"], "price_single": 700,
        "price_monthly": 7000, "min_age": 12, "max_age": 999
    },
}

class DemandItem(BaseModel):
    """Схема для запроса потребности в тренировках."""
    program: str
    count: int

class OptimizationRequest(BaseModel):
    """Схема запроса на оптимизацию расписания."""
    demands: List[DemandItem]

@app.on_event("startup")
async def startup():
    """Инициализация базы данных при запуске."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.post("/auth/register")
async def register(user: UserCreate, password: str, db: AsyncSession = Depends(get_db)):
    """Регистрация нового пользователя."""
    hashed_pw = get_password_hash(password)
    db_user = User(**user.model_dump(), password_hash=hashed_pw)
    db.add(db_user)
    await db.commit()
    return {"message": "Пользователь зарегистрирован"}

@app.post("/auth/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Аутентификация пользователя и выдача токена."""
    stmt = select(User).where(User.username == form_data.username)
    user = (await db.execute(stmt)).scalar_one_or_none()
    
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Неверное имя или пароль")

    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/", response_model=UserResponse)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """Создание пользователя администратором (базовый метод)."""
    db_user = User(**user.model_dump(), password_hash="placeholder")
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

@app.post("/locations/", response_model=LocationResponse)
async def create_location(location: LocationCreate, db: AsyncSession = Depends(get_db)):
    """Создание дорожки (локации)."""
    db_location = Location(name=location.name, capacity=10)
    db.add(db_location)
    await db.commit()
    await db.refresh(db_location)
    return db_location

@app.post("/sessions/", response_model=SessionResponse)
async def create_session(
    session: SessionCreate,
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_admin)  # pylint: disable=unused-argument
):
    """Создание сеанса. Доступно только администраторам."""
    if session.start_time.hour < 9 or session.start_time.hour >= 20:
        raise HTTPException(status_code=400, detail="Бассейн работает с 09:00 до 20:00.")
    if session.start_time.minute != 0:
        raise HTTPException(status_code=400, detail="Сеансы начинаются в начале часа.")

    end_time = session.start_time + timedelta(hours=1)
    prog_name = session.program_name.value
    rules = PROGRAM_RULES[prog_name]

    if session.trainer not in rules["trainers"]:
        raise HTTPException(
            status_code=400,
            detail=f"Недопустимый тренер. Допустимые: {rules['trainers']}"
        )

    stmt = select(Location).where(Location.id == session.location_id)
    loc_result = await db.execute(stmt)
    if not loc_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Локация не найдена")

    db_session = PoolSession(
        location_id=session.location_id,
        program_name=prog_name,
        trainer=session.trainer,
        start_time=session.start_time,
        end_time=end_time,
        price_single=rules["price_single"],
        price_monthly=rules["price_monthly"],
        min_age=rules["min_age"],
        max_age=rules["max_age"],
        max_participants=10
    )
    db.add(db_session)
    await db.commit()
    await db.refresh(db_session)
    return db_session

@app.post("/bookings/", response_model=BookingResponse)
async def create_booking(booking: BookingCreate, db: AsyncSession = Depends(get_db)):
    """Бронирование сеанса клиентом."""
    user_stmt = select(User).where(User.id == booking.user_id)
    user = (await db.execute(user_stmt)).scalar_one_or_none()
    if not user:
        raise HTTPException(404, "Пользователь не найден")

    session_stmt = select(PoolSession).where(PoolSession.id == booking.session_id)
    session = (await db.execute(session_stmt)).scalar_one_or_none()
    if not session:
        raise HTTPException(404, "Сеанс не найден")

    if user.age < session.min_age or user.age > session.max_age:
        raise HTTPException(400, "Возраст не подходит для программы.")

    if session.current_participants >= session.max_participants:
        raise HTTPException(400, "На дорожке нет свободных мест.")

    stmt = select(Booking).where(
        Booking.user_id == user.id, Booking.session_id == session.id
    )
    existing = await db.execute(stmt)
    if existing.scalar_one_or_none():
        raise HTTPException(400, "Вы уже записаны на этот сеанс.")

    db_booking = Booking(
        user_id=user.id,
        session_id=session.id,
        pass_type=booking.pass_type.value
    )
    db.add(db_booking)
    session.current_participants += 1

    await db.commit()
    await db.refresh(db_booking)
    return db_booking

@app.post("/optimize-schedule/")
async def optimize_trainer_schedule(
    request: OptimizationRequest,
    _admin: dict = Depends(require_admin)  # pylint: disable=unused-argument
):
    """Оптимальное назначение тренеров (алгоритм балансировки нагрузки)."""
    workload = {
        t: 0 for trainers in PROGRAM_RULES.values()
        for t in trainers["trainers"] if t
    }
    schedule_result = []

    for demand in request.demands:
        program = demand.program
        if program not in PROGRAM_RULES:
            raise HTTPException(status_code=400, detail=f"Неизвестная программа: {program}")

        allowed_trainers = PROGRAM_RULES[program]["trainers"]

        if not allowed_trainers or allowed_trainers == [None, ""]:
            for _ in range(demand.count):
                schedule_result.append({"program": program, "trainer": None})
            continue

        for _ in range(demand.count):
            best_trainer = min(allowed_trainers, key=lambda t: workload[t])
            workload[best_trainer] += 1
            schedule_result.append({"program": program, "trainer": best_trainer})

    return {
        "status": "Оптимизация завершена успешно",
        "assigned_schedule": schedule_result,
        "final_workload_hours": workload
    }