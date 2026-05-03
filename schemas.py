from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    password: str  # Пароль теперь передается в теле запроса

class UserResponse(BaseModel):
    id: int
    username: str
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str

class LocationCreate(BaseModel):
    name: str
    capacity: int

class LocationResponse(LocationCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)

class SessionCreate(BaseModel):
    location_id: int
    program_name: str
    trainer: Optional[str] = None

class SessionResponse(SessionCreate):
    id: int
    start_time: datetime
    model_config = ConfigDict(from_attributes=True)

class BookingCreate(BaseModel):
    user_id: int
    session_id: int
    pass_type: str

class BookingResponse(BookingCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)