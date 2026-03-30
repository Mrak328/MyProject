from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError
from typing import Optional
from app.database import get_db
from app.crud.user import user_crud
from app.services.auth import auth_service
from app.schemas.auth import TokenData
from app.models import Users

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
) -> Users:
    """Получить текущего пользователя из JWT токена"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token:
        raise credentials_exception

    try:
        # Декодируем токен
        payload = auth_service.decode_token(token)
        if payload is None:
            raise credentials_exception

        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception

        user_id = int(user_id)

    except JWTError:
        raise credentials_exception

    # Получаем пользователя из БД
    user = user_crud.get(db, user_id)
    if user is None:
        raise credentials_exception

    return user


async def get_current_user_optional(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
) -> Optional[Users]:
    """Получить пользователя из токена (опционально, без ошибки)"""
    try:
        return await get_current_user(token, db)
    except HTTPException:
        return None


async def get_current_admin(
        current_user: Users = Depends(get_current_user)
) -> Users:
    """Проверка прав администратора"""
    if current_user.role_id != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user