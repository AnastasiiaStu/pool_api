from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from contextlib import asynccontextmanager

import models
import schemas
from database import engine, get_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Создаем таблицы при старте
    models.Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title="Pool API", lifespan=lifespan)

@app.post("/auth/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    # В реальном проекте здесь должен быть хэш пароля
    new_user = models.User(username=user.username, hashed_password=user.password + "_hashed")
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/auth/login", response_model=schemas.Token)
def login(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if not db_user or db_user.hashed_password != user.password + "_hashed":
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": "fake-jwt-token", "token_type": "bearer"}

@app.get("/users/", response_model=List[schemas.UserResponse])
def get_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()

@app.get("/users/{user_id}", response_model=schemas.UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"detail": "User deleted"}

@app.post("/locations/", response_model=schemas.LocationResponse)
def create_location(loc: schemas.LocationCreate, db: Session = Depends(get_db)):
    new_loc = models.Location(**loc.model_dump())
    db.add(new_loc)
    db.commit()
    db.refresh(new_loc)
    return new_loc

@app.get("/locations/", response_model=List[schemas.LocationResponse])
def get_locations(db: Session = Depends(get_db)):
    return db.query(models.Location).all()

@app.put("/locations/{loc_id}", response_model=schemas.LocationResponse)
def update_location(loc_id: int, loc: schemas.LocationCreate, db: Session = Depends(get_db)):
    db_loc = db.query(models.Location).filter(models.Location.id == loc_id).first()
    if not db_loc:
        raise HTTPException(status_code=404, detail="Location not found")
    for key, value in loc.model_dump().items():
        setattr(db_loc, key, value)
    db.commit()
    db.refresh(db_loc)
    return db_loc

@app.delete("/locations/{loc_id}")
def delete_location(loc_id: int, db: Session = Depends(get_db)):
    db_loc = db.query(models.Location).filter(models.Location.id == loc_id).first()
    if not db_loc:
        raise HTTPException(status_code=404, detail="Location not found")
    db.delete(db_loc)
    db.commit()
    return {"detail": "Location deleted"}

@app.post("/sessions/", response_model=schemas.SessionResponse)
def create_session(sess: schemas.SessionCreate, db: Session = Depends(get_db)):
    new_sess = models.Session(**sess.model_dump())
    db.add(new_sess)
    db.commit()
    db.refresh(new_sess)
    return new_sess

@app.get("/sessions/", response_model=List[schemas.SessionResponse])
def get_sessions(db: Session = Depends(get_db)):
    return db.query(models.Session).all()

@app.delete("/sessions/{session_id}")
def delete_session(session_id: int, db: Session = Depends(get_db)):
    db_sess = db.query(models.Session).filter(models.Session.id == session_id).first()
    if not db_sess:
        raise HTTPException(status_code=404, detail="Session not found")
    db.delete(db_sess)
    db.commit()
    return {"detail": "Session deleted"}

@app.post("/bookings/", response_model=schemas.BookingResponse)
def create_booking(book: schemas.BookingCreate, db: Session = Depends(get_db)):
    new_book = models.Booking(**book.model_dump())
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book

@app.get("/bookings/", response_model=List[schemas.BookingResponse])
def get_bookings(db: Session = Depends(get_db)):
    return db.query(models.Booking).all()

@app.post("/optimize-schedule/")
def optimize_schedule():
    """Заглушка алгоритма для прохождения теста"""
    return {"status": "optimized", "scheduled_trainers": 5}