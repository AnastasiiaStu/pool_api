"""
Модели базы данных SQLAlchemy для API бассейна.
"""
# pylint: disable=too-few-public-methods, not-callable

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from database import Base

class Location(Base):
    """Дорожки бассейна"""
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    capacity = Column(Integer, default=10)

    sessions = relationship("PoolSession", back_populates="location")

class User(Base):
    """Клиенты бассейна"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default="client")
    age = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=func.now())

    bookings = relationship("Booking", back_populates="user")

class PoolSession(Base):
    """Сеансы/Занятия на дорожке"""
    __tablename__ = "pool_sessions"

    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)

    program_name = Column(String(100), nullable=False)
    trainer = Column(String(100), nullable=True)

    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)

    price_single = Column(Float, nullable=False)
    price_monthly = Column(Float, nullable=False)

    min_age = Column(Integer, default=0)
    max_age = Column(Integer, default=999)

    max_participants = Column(Integer, default=10)
    current_participants = Column(Integer, default=0)

    location = relationship("Location", back_populates="sessions")
    bookings = relationship("Booking", back_populates="session")

class Booking(Base):
    """Бронирование (покупка абонемента/разового)"""
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("pool_sessions.id"), nullable=False)
    pass_type = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=func.now())

    user = relationship("User", back_populates="bookings")
    session = relationship("PoolSession", back_populates="bookings")

    __table_args__ = (
        UniqueConstraint('user_id', 'session_id', name='unique_user_session'),
    )