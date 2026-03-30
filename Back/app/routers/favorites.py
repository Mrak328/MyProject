from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.crud.favorite import favorite_crud
from app.crud.listing import listing_crud
from app.crud.photo import photo_crud
from app.schemas.favorite import FavoriteCreate, FavoriteResponse
from app.schemas.listing import ListingResponse
from app.schemas.common import MessageResponse

router = APIRouter(prefix="/favorites", tags=["favorites"])


@router.get("/user/{user_id}", response_model=List[ListingResponse])
async def get_user_favorites(user_id: int, db: Session = Depends(get_db)):
    favorites = favorite_crud.get_by_user(db, user_id)

    listings = []
    for fav in favorites:
        listing = listing_crud.get(db, fav.listing_id)
        if listing:
            # Получаем фото для объявления
            photos = photo_crud.get_by_listing(db, listing.listing_id)
            # Преобразуем в словарь с правильными полями
            listing_dict = {
                "listing_id": listing.listing_id,
                "title": listing.title,
                "description": listing.description,
                "price": listing.price,
                "address": listing.address,
                "total_area": listing.total_area,
                "property_type_id": listing.property_type_id,
                "deal_type_id": listing.deal_type_id,
                "user_id": listing.user_id,
                "listing_status_id": listing.listing_status_id,
                "views": listing.views,
                "moderated": listing.moderated,
                "publication_date": listing.publication_date,
                "contact_phone": listing.contact_phone,
                "contact_person": listing.contact_person,
                "photos": [p.file_url for p in photos]  # ← только URL
            }
            listings.append(listing_dict)

    return listings


@router.post("/", response_model=FavoriteResponse)
async def add_favorite(favorite: FavoriteCreate, db: Session = Depends(get_db)):
    existing = favorite_crud.get_by_user_and_listing(
        db, favorite.user_id, favorite.listing_id
    )
    if existing:
        raise HTTPException(status_code=400, detail="Already in favorites")

    return favorite_crud.create(db, favorite)


@router.delete("/{user_id}/{listing_id}", response_model=MessageResponse)
async def remove_favorite(
        user_id: int,
        listing_id: int,
        db: Session = Depends(get_db)
):
    deleted = favorite_crud.delete_by_user_and_listing(db, user_id, listing_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Favorite not found")
    return MessageResponse(message="Removed from favorites")