from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from app.database import get_db
from app.crud.listing import listing_crud
from app.crud.photo import photo_crud
from app.schemas.listing import ListingCreate, ListingUpdate, ListingResponse
from app.schemas.common import MessageResponse
from app.core.dependencies import get_current_user_optional
from app.models import Users, Listing

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


@router.get("/search")
async def search_listings(
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=100),
        query: Optional[str] = None,
        city: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        min_area: Optional[float] = None,
        max_area: Optional[float] = None,
        rooms: Optional[int] = None,
        floor: Optional[int] = None,
        max_floor: Optional[int] = None,
        renovation_condition_id: Optional[int] = None,
        deal_type_id: Optional[int] = None,
        property_type_id: Optional[int] = None,
        sort_by: str = "date_desc",
        db: Session = Depends(get_db)
):
    skip = (page - 1) * page_size

    query_builder = db.query(Listing).filter(
        Listing.listing_status_id == 1,
        Listing.moderated == True
    )

    if query:
        query_builder = query_builder.filter(
            or_(
                Listing.title.ilike(f"%{query}%"),
                Listing.description.ilike(f"%{query}%"),
                Listing.address.ilike(f"%{query}%")
            )
        )
    if city:
        query_builder = query_builder.filter(Listing.address.ilike(f"%{city}%"))
    if min_price:
        query_builder = query_builder.filter(Listing.price >= min_price)
    if max_price:
        query_builder = query_builder.filter(Listing.price <= max_price)
    if min_area:
        query_builder = query_builder.filter(Listing.total_area >= min_area)
    if max_area:
        query_builder = query_builder.filter(Listing.total_area <= max_area)
    if rooms:
        if rooms == 4:  # 4+ комнат
            query_builder = query_builder.filter(Listing.rooms >= 4)
        else:
            query_builder = query_builder.filter(Listing.rooms == rooms)
    if floor is not None:
        query_builder = query_builder.filter(Listing.floor == floor)
    if max_floor:
        query_builder = query_builder.filter(Listing.max_floor >= max_floor)
    if renovation_condition_id:
        query_builder = query_builder.filter(Listing.renovation_condition_id == renovation_condition_id)
    if deal_type_id:
        query_builder = query_builder.filter(Listing.deal_type_id == deal_type_id)
    if property_type_id:
        query_builder = query_builder.filter(Listing.property_type_id == property_type_id)

    # Сортировка
    if sort_by == "price_asc":
        query_builder = query_builder.order_by(Listing.price.asc())
    elif sort_by == "price_desc":
        query_builder = query_builder.order_by(Listing.price.desc())
    elif sort_by == "views_desc":
        query_builder = query_builder.order_by(Listing.views.desc())
    elif sort_by == "area_asc":
        query_builder = query_builder.order_by(Listing.total_area.asc())
    elif sort_by == "area_desc":
        query_builder = query_builder.order_by(Listing.total_area.desc())
    else:
        query_builder = query_builder.order_by(Listing.publication_date.desc())

    total = query_builder.count()
    listings = query_builder.offset(skip).limit(page_size).all()

    result = []
    for listing in listings:
        photos = photo_crud.get_by_listing(db, listing.listing_id)
        result.append({
            "listing_id": listing.listing_id,
            "title": listing.title,
            "description": listing.description,
            "price": listing.price,
            "address": listing.address,
            "total_area": listing.total_area,
            "rooms": listing.rooms,
            "floor": listing.floor,
            "max_floor": listing.max_floor,
            "renovation_condition_id": listing.renovation_condition_id,
            "property_type_id": listing.property_type_id,
            "deal_type_id": listing.deal_type_id,
            "user_id": listing.user_id,
            "listing_status_id": listing.listing_status_id,
            "views": listing.views,
            "moderated": listing.moderated,
            "publication_date": listing.publication_date,
            "photos": [p.file_url for p in photos]
        })

    return {
        "items": result,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size
    }


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
    ip_address = request.client.host if request.client else "unknown"
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

    listing_crud.register_listing_view(
        db=db,
        listing_id=listing_id,
        user_id=current_user.user_id if current_user else None,
        ip_address=ip_address,
        device=device,
        browser=browser
    )

    return {"status": "ok", "message": "View registered"}