from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from typing import Optional
from datetime import datetime
from app.database import get_db
from app.crud.user import user_crud
from app.core.config import settings
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
        # Декодируем токен напрямую, без auth_service
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        user_id = int(user_id)
    except JWTError:
        raise credentials_exception

    user = user_crud.get(db, user_id)
    if user is None:
        raise credentials_exception

    # Обновляем время последней активности
    user.last_activity = datetime.now()
    db.commit()

    return user


async def get_current_user_optional(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
) -> Optional[Users]:
    """Получить пользователя из токена (опционально)"""
    try:
        return await get_current_user(token, db)
    except HTTPException:
        return None


async def get_current_admin(
        current_user: Users = Depends(get_current_user)
) -> Users:
    """Только для администратора (role_id = 1)"""
    if current_user.role_id != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


async def get_current_moderator(
        current_user: Users = Depends(get_current_user)
) -> Users:
    """Только для модератора (role_id = 2)"""
    if current_user.role_id != 2:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Moderator access required"
        )
    return current_user