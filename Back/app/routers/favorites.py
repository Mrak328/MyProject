from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.crud.favorite import favorite_crud
from app.crud.listing import listing_crud
from app.core.dependencies import get_current_user
from app.models import Users

router = APIRouter(prefix="/favorites", tags=["favorites"])


@router.post("/{listing_id}")
def add_favorite(
        listing_id: int,
        db: Session = Depends(get_db),
        current_user: Users = Depends(get_current_user)
):
    listing = listing_crud.get(db, listing_id)
    if not listing:
        raise HTTPException(404, "Объявление не найдено")

    favorite_crud.add_favorite(db, current_user.user_id, listing_id)
    return {"message": "Добавлено в избранное"}


@router.delete("/{listing_id}")
def remove_favorite(
        listing_id: int,
        db: Session = Depends(get_db),
        current_user: Users = Depends(get_current_user)
):
    favorite_crud.remove_favorite(db, current_user.user_id, listing_id)
    return {"message": "Удалено из избранного"}


@router.get("/")
def get_favorites(
        db: Session = Depends(get_db),
        current_user: Users = Depends(get_current_user)
):
    favorites = favorite_crud.get_user_favorites(db, current_user.user_id)
    listings = []
    for fav in favorites:
        listing = listing_crud.get(db, fav.listing_id)
        if listing:
            listings.append(listing)
    return listings


@router.get("/check/{listing_id}")
def check_favorite(
        listing_id: int,
        db: Session = Depends(get_db),
        current_user: Users = Depends(get_current_user)
):
    return {"is_favorite": favorite_crud.is_favorite(db, current_user.user_id, listing_id)}