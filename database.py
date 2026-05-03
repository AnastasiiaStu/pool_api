"""Модуль конфигурации и подключения к базе данных"""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./pool.db")

if "sqlite" in DATABASE_URL:
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

SESSION_LOCAL = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Генератор сессий для подключения к БД"""
    db = SESSION_LOCAL()
    try:
        yield db
    finally:
        db.close()