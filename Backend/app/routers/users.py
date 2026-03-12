from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import crud, schemas

router = APIRouter()

@router.get("/", response_model=List[schemas.User])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Список всех продавцов/арендодателей"""
    return crud.get_users(db, skip=skip, limit=limit)

@router.get("/{user_id}", response_model=schemas.User)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Профиль продавца: рейтинг, отзывы, контакты"""
    user = crud.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Продавец не найден")
    return user

@router.get("/{user_id}/listings", response_model=List[schemas.Listing])
async def get_user_listings(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Все объявления конкретного продавца"""
    return crud.get_listings(db, user_id=user_id)

@router.get("/{user_id}/reviews", response_model=List[schemas.Review])
async def get_user_reviews(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Отзывы о продавце"""
    return crud.get_reviews_by_user(db, user_id)

@router.post("/", response_model=schemas.User)
async def register_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    """Регистрация нового продавца/покупателя"""
    # Проверка телефона
    if crud.get_user_by_phone(db, user.phone_number):
        raise HTTPException(status_code=400, detail="Телефон уже зарегистрирован")
    return crud.create_user(db=db, user=user)

@router.post("/{user_id}/reviews", response_model=schemas.Review)
async def create_review(
    user_id: int,
    review: schemas.ReviewCreate,
    db: Session = Depends(get_db)
):
    """Оставить отзыв о продавце"""
    return crud.create_review(db, review)