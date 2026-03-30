from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.crud.user import user_crud
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.schemas.common import MessageResponse
from app.core.dependencies import get_current_user
from app.models import Users

router = APIRouter(prefix="/users", tags=["users"])

# ===== СПЕЦИАЛЬНЫЕ МАРШРУТЫ (ДО ПАРАМЕТРИЗОВАННЫХ) =====

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Users = Depends(get_current_user)
):
    """Получить информацию о текущем авторизованном пользователе"""
    return current_user

@router.get("/phone/{phone}", response_model=UserResponse)
async def get_user_by_phone(phone: str, db: Session = Depends(get_db)):
    user = user_crud.get_by_phone(db, phone)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# ===== ОБЫЧНЫЕ CRUD МАРШРУТЫ =====

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
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    if user_crud.get_by_phone(db, user.phone_number):
        raise HTTPException(status_code=400, detail="Phone already registered")
    if user.email and user_crud.get_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    return user_crud.create(db, user)

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db)
):
    user = user_crud.get(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user_crud.update(db, db_obj=user, obj_in=user_update)

@router.delete("/{user_id}", response_model=MessageResponse)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    user = user_crud.delete(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return MessageResponse(message="User deleted")