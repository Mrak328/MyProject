from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.crud.user import user_crud
from app.schemas.user import UserUpdate, UserResponse
from app.schemas.common import MessageResponse
from app.core.dependencies import get_current_user
from app.models import Users

router = APIRouter(prefix="/users", tags=["users"])


# ============================================
# ТЕКУЩИЙ ПОЛЬЗОВАТЕЛЬ
# ============================================

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: Users = Depends(get_current_user)):
    """Профиль текущего пользователя"""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_me(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Обновить свой профиль"""
    # Проверка уникальности email
    if user_update.email and user_crud.is_email_taken(db, user_update.email, exclude_user_id=current_user.user_id):
        raise HTTPException(status_code=409, detail="Email уже используется")
    return user_crud.update(db, current_user, user_update)


# ============================================
# ПОИСК ПО ТЕЛЕФОНУ
# ============================================

@router.get("/by-phone/{phone}", response_model=UserResponse)
async def get_user_by_phone(phone: str, db: Session = Depends(get_db)):
    """Найти пользователя по номеру телефона"""
    user = user_crud.get_by_phone(db, phone)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user


# ============================================
# CRUD (админ / публичный)
# ============================================

@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    return user_crud.get_multi(db, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = user_crud.get(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Обновить пользователя (только свои данные)"""
    user = user_crud.get(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    if user.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Нет доступа")

    if user_update.email and user_crud.is_email_taken(db, user_update.email, exclude_user_id=user_id):
        raise HTTPException(status_code=409, detail="Email уже используется")
    return user_crud.update(db, user, user_update)


@router.delete("/{user_id}", response_model=MessageResponse)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Удалить пользователя (только себя)"""
    if user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Нет доступа")

    user_crud.delete(db, user_id)
    return {"message": "Пользователь удалён", "success": True}