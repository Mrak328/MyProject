from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import crud, schemas

router = APIRouter(prefix="/favorites", tags=["favorites"])

@router.get("/user/{user_id}", response_model=List[schemas.Listing])
async def get_favorites(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Список избранных объявлений пользователя"""
    return crud.get_user_favorites(db, user_id)

@router.post("/user/{user_id}/listing/{listing_id}")
async def add_favorite(
    user_id: int,
    listing_id: int,
    db: Session = Depends(get_db)
):
    """Добавить в избранное"""
    crud.add_favorite(db, user_id, listing_id)
    return {"message": "Добавлено в избранное"}

@router.delete("/user/{user_id}/listing/{listing_id}")
async def remove_favorite(
    user_id: int,
    listing_id: int,
    db: Session = Depends(get_db)
):
    """Удалить из избранного"""
    crud.remove_favorite(db, user_id, listing_id)
    return {"message": "Удалено из избранного"}