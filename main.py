"""Основной файл приложения FastAPI"""

from contextlib import asynccontextmanager
from typing import List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

import auth
import models
import schemas
from database import engine, get_db

@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Управление жизненным циклом приложения"""
    models.Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title="Pool API", lifespan=lifespan)

@app.post("/auth/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Регистрация нового пользователя"""
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # ИСПОЛЬЗУЕМ РЕАЛЬНЫЙ ХЭШ
    hashed_pw = auth.get_password_hash(user.password)
    new_user = models.User(username=user.username, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/auth/login", response_model=schemas.Token)
def login(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Авторизация и выдача JWT токена"""
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    
    # ИСПОЛЬЗУЕМ РЕАЛЬНУЮ ПРОВЕРКУ
    if not db_user or not auth.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = auth.create_access_token(data={"sub": db_user.username, "role": "user"})
    return {"access_token": access_token, "token_type": "bearer"}

# ==== ЭНДПОИНТЫ НИЖЕ ТЕПЕРЬ ТРЕБУЮТ ТОКЕН (Depends(auth.get_current_user)) ====

@app.get("/users/", response_model=List[schemas.UserResponse])
def get_users(db: Session = Depends(get_db), _user: dict = Depends(auth.get_current_user)):
    """Получение списка всех пользователей"""
    return db.query(models.User).all()

@app.get("/users/{user_id}", response_model=schemas.UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db), _user: dict = Depends(auth.get_current_user)):
    """Получение данных пользователя по ID"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), _user: dict = Depends(auth.get_current_user)):
    """Удаление пользователя"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"detail": "User deleted"}

@app.post("/locations/", response_model=schemas.LocationResponse)
def create_location(loc: schemas.LocationCreate, db: Session = Depends(get_db), _user: dict = Depends(auth.get_current_user)):
    """Создание локации"""
    new_loc = models.Location(**loc.model_dump())
    db.add(new_loc)
    db.commit()
    db.refresh(new_loc)
    return new_loc

@app.get("/locations/", response_model=List[schemas.LocationResponse])
def get_locations(db: Session = Depends(get_db), _user: dict = Depends(auth.get_current_user)):
    """Получение списка локаций"""
    return db.query(models.Location).all()

@app.put("/locations/{loc_id}", response_model=schemas.LocationResponse)
def update_location(loc_id: int, loc: schemas.LocationCreate, db: Session = Depends(get_db), _user: dict = Depends(auth.get_current_user)):
    """Обновление локации"""
    db_loc = db.query(models.Location).filter(models.Location.id == loc_id).first()
    if not db_loc:
        raise HTTPException(status_code=404, detail="Location not found")
    for key, value in loc.model_dump().items():
        setattr(db_loc, key, value)
    db.commit()
    db.refresh(db_loc)
    return db_loc

@app.delete("/locations/{loc_id}")
def delete_location(loc_id: int, db: Session = Depends(get_db), _user: dict = Depends(auth.get_current_user)):
    """Удаление локации"""
    db_loc = db.query(models.Location).filter(models.Location.id == loc_id).first()
    if not db_loc:
        raise HTTPException(status_code=404, detail="Location not found")
    db.delete(db_loc)
    db.commit()
    return {"detail": "Location deleted"}

@app.post("/sessions/", response_model=schemas.SessionResponse)
def create_session(sess: schemas.SessionCreate, db: Session = Depends(get_db), _user: dict = Depends(auth.get_current_user)):
    """Создание тренировочной сессии"""
    new_sess = models.Session(**sess.model_dump())
    db.add(new_sess)
    db.commit()
    db.refresh(new_sess)
    return new_sess

@app.get("/sessions/", response_model=List[schemas.SessionResponse])
def get_sessions(db: Session = Depends(get_db), _user: dict = Depends(auth.get_current_user)):
    """Получение списка сессий"""
    return db.query(models.Session).all()

@app.delete("/sessions/{session_id}")
def delete_session(session_id: int, db: Session = Depends(get_db), _user: dict = Depends(auth.get_current_user)):
    """Удаление сессии."""
    db_sess = db.query(models.Session).filter(models.Session.id == session_id).first()
    if not db_sess:
        raise HTTPException(status_code=404, detail="Session not found")
    db.delete(db_sess)
    db.commit()
    return {"detail": "Session deleted"}

@app.post("/bookings/", response_model=schemas.BookingResponse)
def create_booking(book: schemas.BookingCreate, db: Session = Depends(get_db), _user: dict = Depends(auth.get_current_user)):
    """Создание бронирования"""
    new_book = models.Booking(**book.model_dump())
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book

@app.get("/bookings/", response_model=List[schemas.BookingResponse])
def get_bookings(db: Session = Depends(get_db), _user: dict = Depends(auth.get_current_user)):
    """Получение списка бронирований."""
    return db.query(models.Booking).all()

@app.post("/optimize-schedule/")
def optimize_schedule(db: Session = Depends(get_db), _user: dict = Depends(auth.get_current_user)):
    """
    Алгоритм балансировки расписания.
    Назначает свободных тренеров на нераспределенные сессии.
    """
    unassigned_sessions = db.query(models.Session).filter(models.Session.trainer == None).all()
    if not unassigned_sessions:
        return {"status": "optimized", "scheduled_trainers": 0, "detail": "No unassigned sessions"}

    available_trainers = ["Иван", "Анна", "Сергей", "Елена"]
    assigned_count = 0
    
    # Распределяем тренеров по кругу
    for i, session in enumerate(unassigned_sessions):
        session.trainer = available_trainers[i % len(available_trainers)]
        assigned_count += 1
        
    db.commit()
    return {"status": "optimized", "scheduled_trainers": assigned_count}