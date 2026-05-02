"""
Схемы Pydantic для валидации данных и ответов API.
"""
# pylint: disable=too-few-public-methods, invalid-name

from datetime import datetime
from typing import Optional
from enum import Enum

from pydantic import BaseModel, Field

class ProgramEnum(str, Enum):
    """Перечисление программ бассейна."""
    free = "Свободное плавание"
    kids = "Детская группа"
    sport = "Спортивная группа"
    aqua = "Аквааэробика"

class PassTypeEnum(str, Enum):
    """Перечисление типов абонементов."""
    single = "Разовый"
    monthly = "Абонемент на месяц"

class UserCreate(BaseModel):
    """Схема создания пользователя."""
    username: str = Field(..., min_length=2, max_length=100)
    age: int = Field(..., ge=1, le=100)

class UserResponse(UserCreate):
    """Схема ответа с данными пользователя."""
    id: int

    class Config:
        """Настройки Pydantic."""
        from_attributes = True

class LocationCreate(BaseModel):
    """Схема создания локации."""
    name: str = Field(..., description="Например: Дорожка 1")

class LocationResponse(LocationCreate):
    """Схема ответа с данными локации."""
    id: int
    capacity: int

    class Config:
        """Настройки Pydantic."""
        from_attributes = True

class SessionCreate(BaseModel):
    """Схема создания сеанса."""
    location_id: int
    program_name: ProgramEnum
    trainer: Optional[str] = None
    start_time: datetime

class SessionResponse(BaseModel):
    """Схема ответа с данными сеанса."""
    id: int
    location_id: int
    program_name: str
    trainer: Optional[str]
    start_time: datetime
    end_time: datetime
    price_single: float
    price_monthly: float
    current_participants: int
    max_participants: int

    class Config:
        """Настройки Pydantic."""
        from_attributes = True

class BookingCreate(BaseModel):
    """Схема создания бронирования."""
    user_id: int
    session_id: int
    pass_type: PassTypeEnum

class BookingResponse(BaseModel):
    """Схема ответа с данными бронирования."""
    id: int
    user_id: int
    session_id: int
    pass_type: str

    class Config:
        """Настройки Pydantic."""
        from_attributes = True