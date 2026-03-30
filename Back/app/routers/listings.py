from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.crud.listing import listing_crud
from app.crud.photo import photo_crud
from app.schemas.listing import ListingCreate, ListingUpdate, ListingResponse
from app.schemas.common import MessageResponse
from app.core.dependencies import get_current_user_optional
from app.models import Users

router = APIRouter(prefix="/listings", tags=["listings"])


@router.get("/", response_model=List[ListingResponse])
async def get_listings(
        skip: int = Query(0, ge=0),
        limit: int = Query(50, ge=1, le=100),
        city: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        db: Session = Depends(get_db)
):
    listings = listing_crud.get_active(db, skip=skip, limit=limit)

    result = []
    for listing in listings:
        photos = photo_crud.get_by_listing(db, listing.listing_id)
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
            "photos": [p.file_url for p in photos]
        }
        result.append(listing_dict)

    return result


@router.get("/active", response_model=List[ListingResponse])
async def get_active_listings(
        skip: int = Query(0, ge=0),
        limit: int = Query(50, ge=1, le=100),
        db: Session = Depends(get_db)
):
    listings = listing_crud.get_active(db, skip=skip, limit=limit)

    result = []
    for listing in listings:
        photos = photo_crud.get_by_listing(db, listing.listing_id)
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
            "photos": [p.file_url for p in photos]
        }
        result.append(listing_dict)

    return result


@router.get("/{listing_id}", response_model=ListingResponse)
async def get_listing(listing_id: int, db: Session = Depends(get_db)):
    listing = listing_crud.get(db, listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    listing_crud.increment_views(db, listing_id)

    photos = photo_crud.get_by_listing(db, listing_id)

    response_data = {
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
        "photos": [p.file_url for p in photos]
    }

    return response_data


@router.post("/", response_model=ListingResponse)
async def create_listing(listing: ListingCreate, db: Session = Depends(get_db)):
    return listing_crud.create(db, listing)


@router.put("/{listing_id}", response_model=ListingResponse)
async def update_listing(
        listing_id: int,
        listing_update: ListingUpdate,
        db: Session = Depends(get_db)
):
    listing = listing_crud.get(db, id=listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return listing_crud.update(db, db_obj=listing, obj_in=listing_update)


@router.delete("/{listing_id}", response_model=MessageResponse)
async def delete_listing(listing_id: int, db: Session = Depends(get_db)):
    listing = listing_crud.delete(db, id=listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return MessageResponse(message="Listing deleted")


@router.get("/{listing_id}/photos")
async def get_listing_photos(listing_id: int, db: Session = Depends(get_db)):
    photos = photo_crud.get_by_listing(db, listing_id)
    return [{"photo_id": p.photo_id, "url": p.file_url, "title": p.title} for p in photos]


@router.post("/{listing_id}/view")
async def register_view(
        listing_id: int,
        request: Request,
        current_user: Optional[Users] = Depends(get_current_user_optional),
        db: Session = Depends(get_db)
):
    """Зарегистрировать просмотр объявления"""
    # Получаем IP адрес
    ip_address = request.client.host if request.client else "unknown"

    # Определяем устройство и браузер из User-Agent
    user_agent = request.headers.get("user-agent", "")
    device = "Desktop"
    browser = "Unknown"

    if "Mobile" in user_agent or "Android" in user_agent:
        device = "Mobile"
    elif "Tablet" in user_agent or "iPad" in user_agent:
        device = "Tablet"

    if "Chrome" in user_agent:
        browser = "Chrome"
    elif "Firefox" in user_agent:
        browser = "Firefox"
    elif "Safari" in user_agent:
        browser = "Safari"
    elif "Edge" in user_agent:
        browser = "Edge"

    # Регистрируем просмотр
    listing_crud.register_listing_view(
        db=db,
        listing_id=listing_id,
        user_id=current_user.user_id if current_user else None,
        ip_address=ip_address,
        device=device,
        browser=browser
    )

    return {"status": "ok", "message": "View registered"}