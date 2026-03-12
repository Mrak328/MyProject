from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import crud, schemas

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])

@router.get("/user/{user_id}", response_model=List[schemas.SearchSubscription])
async def get_subscriptions(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Подписки пользователя на поиск"""
    return crud.get_user_subscriptions(db, user_id)

@router.post("/")
async def create_subscription(
    subscription: schemas.SubscriptionCreate,
    db: Session = Depends(get_db)
):
    """Создать подписку на новые объявления по фильтрам"""
    return crud.create_subscription(db, subscription)

@router.delete("/{subscription_id}")
async def delete_subscription(
    subscription_id: int,
    db: Session = Depends(get_db)
):
    """Удалить подписку"""
    crud.delete_subscription(db, subscription_id)
    return {"message": "Подписка удалена"}