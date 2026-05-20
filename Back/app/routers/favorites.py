from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.crud.favorite import favorite_crud
from app.crud.listing import listing_crud
from app.crud.photo import photo_crud
from app.crud.action_log import action_log_crud
from app.crud.analytics import analytics_crud
from app.schemas.listing import ListingResponse
from app.schemas.common import MessageResponse
from app.core.dependencies import get_current_user
from app.models import Users

router = APIRouter(prefix="/favorites", tags=["favorites"])


def _enrich_favorite(listing, db: Session) -> dict:
    photos = photo_crud.get_by_listing(db, listing.listing_id)
    return {
        "listing_id": listing.listing_id, "user_id": listing.user_id, "title": listing.title,
        "description": listing.description, "price": listing.price, "total_area": listing.total_area,
        "rooms": listing.rooms, "floor": listing.floor, "max_floor": listing.max_floor,
        "property_type_id": listing.property_type_id, "deal_type_id": listing.deal_type_id,
        "renovation_condition_id": listing.renovation_condition_id, "market_type_id": listing.market_type_id,
        "listing_status_id": listing.listing_status_id, "views": listing.views, "moderated": listing.moderated,
        "publication_date": listing.publication_date, "update_date": listing.update_date,
        "contact_person": listing.contact_person, "contact_phone": listing.contact_phone,
        "address": analytics_crud._build_address(db, listing.address_id),
        "photos": [p.file_url for p in photos]
    }


@router.post("/{listing_id}", response_model=MessageResponse)
async def add_favorite(listing_id: int, db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    listing = listing_crud.get(db, listing_id)
    if not listing: raise HTTPException(status_code=404, detail="Объявление не найдено")
    favorite_crud.add(db, current_user.user_id, listing_id)
    action_log_crud.log(db, current_user.user_id, 5, listing_id=listing_id)
    return {"message": "Добавлено в избранное", "success": True}


@router.delete("/{listing_id}", response_model=MessageResponse)
async def remove_favorite(listing_id: int, db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    deleted = favorite_crud.remove(db, current_user.user_id, listing_id)
    if not deleted: raise HTTPException(status_code=404, detail="Объявление не в избранном")
    return {"message": "Удалено из избранного", "success": True}


@router.post("/{listing_id}/toggle", response_model=MessageResponse)
async def toggle_favorite(listing_id: int, db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    listing = listing_crud.get(db, listing_id)
    if not listing: raise HTTPException(status_code=404, detail="Объявление не найдено")
    result = favorite_crud.toggle(db, current_user.user_id, listing_id)
    return {"message": "Добавлено" if result["status"] == "added" else "Удалено", "success": True}


@router.get("/", response_model=List[ListingResponse])
async def get_favorites(db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    favorites = favorite_crud.get_by_user(db, current_user.user_id)
    listings = []
    for fav in favorites:
        listing = listing_crud.get(db, fav.listing_id)
        if listing: listings.append(_enrich_favorite(listing, db))
    return listings


@router.get("/check/{listing_id}")
async def check_favorite(listing_id: int, db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    return {"listing_id": listing_id, "is_favorite": favorite_crud.is_favorite(db, current_user.user_id, listing_id)}