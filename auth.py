"""Модуль для работы с аутентификацией и JWT токенами"""

from datetime import datetime, timedelta

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher

password_hash = PasswordHash((Argon2Hasher(),))

SECRET_KEY = "super-secret-key-for-pool-api"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет соответствие введенного пароля хэшу"""
    return password_hash.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Генерирует хэш пароля"""
    return password_hash.hash(password)

def create_access_token(data: dict) -> str:
    """Создает JWT токен доступа"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """Извлекает текущего пользователя из JWT токена"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None:
            raise HTTPException(status_code=401, detail="Неверный токен")
        return {"username": username, "role": role}
    except JWTError as exc:
        raise HTTPException(
            status_code=401,
            detail="Не удалось проверить учетные данные"
        ) from exc

def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """Проверяет наличие прав администратора у пользователя"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Требуется роль admin")
    return current_user