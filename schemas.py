"""Схемы Pydantic для валидации входных и выходных данных API"""
# pylint: disable=too-few-public-methods

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

class UserCreate(BaseModel):
    """Схема создания пользователя"""
    username: str
    password: str

class UserResponse(BaseModel):
    """Схема ответа с данными пользователя"""
    id: int
    username: str
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    """Схема JWT токена"""
    access_token: str
    token_type: str

class LocationCreate(BaseModel):
    """Схема создания локации"""
    name: str
    capacity: int

class LocationResponse(LocationCreate):
    """Схема ответа с данными локации"""
    id: int
    model_config = ConfigDict(from_attributes=True)

class SessionCreate(BaseModel):
    """Схема создания сессии"""
    location_id: int
    program_name: str
    trainer: Optional[str] = None

class SessionResponse(SessionCreate):
    """Схема ответа с данными сессии"""
    id: int
    start_time: datetime
    model_config = ConfigDict(from_attributes=True)

class BookingCreate(BaseModel):
    """Схема создания бронирования"""
    user_id: int
    session_id: int
    pass_type: str

class BookingResponse(BookingCreate):
    """Схема ответа с данными бронирования"""
    id: int
    model_config = ConfigDict(from_attributes=True)