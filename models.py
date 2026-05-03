"""Модели базы данных SQLAlchemy"""
# pylint: disable=too-few-public-methods

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from database import Base

class User(Base):
    """Модель пользователя"""
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class Location(Base):
    """Модель локации (дорожек бассейна)"""
    __tablename__ = "locations"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    capacity = Column(Integer)

class Session(Base):
    """Модель тренировочной сессии"""
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id"))
    program_name = Column(String)
    trainer = Column(String, nullable=True)
    start_time = Column(DateTime, default=datetime.utcnow)

class Booking(Base):
    """Модель бронирования сессии"""
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    session_id = Column(Integer, ForeignKey("sessions.id"))
    pass_type = Column(String)