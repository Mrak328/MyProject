from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from app.database import get_db
from app.crud.listing import listing_crud
from app.crud.photo import photo_crud
from app.crud.action_log import action_log_crud
from app.crud.analytics import analytics_crud
from app.schemas.listing import ListingCreate, ListingUpdate, ListingResponse
from app.schemas.common import MessageResponse, PaginatedResponse
from app.core.dependencies import get_current_user, get_current_user_optional
from app.models import Users, Listing, Address, City, SearchStatistics

router = APIRouter(prefix="/listings", tags=["listings"])


def _enrich_listing(listing, db: Session) -> dict:
    photos = photo_crud.get_by_listing(db, listing.listing_id)
    return {
        "listing_id": listing.listing_id,
        "user_id": listing.user_id,
        "title": listing.title,
        "description": listing.description,
        "price": listing.price,
        "total_area": listing.total_area,
        "rooms": listing.rooms,
        "floor": listing.floor,
        "max_floor": listing.max_floor,
        "property_type_id": listing.property_type_id,
        "deal_type_id": listing.deal_type_id,
        "renovation_condition_id": listing.renovation_condition_id,
        "market_type_id": listing.market_type_id,
        "developer_name": listing.developer_name,
        "listing_status_id": listing.listing_status_id,
        "views": listing.views,
        "moderated": listing.moderated,
        "publication_date": listing.publication_date,
        "update_date": listing.update_date,
        "contact_person": listing.contact_person,
        "contact_phone": listing.contact_phone,
        "address": analytics_crud._build_address(db, listing.address_id),
        "photos": [p.file_url for p in photos]
    }


@router.get("/", response_model=List[ListingResponse])
async def get_listings(skip: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=100), db: Session = Depends(get_db)):
    listings = listing_crud.get_active(db, skip=skip, limit=limit)
    return [_enrich_listing(l, db) for l in listings]


@router.get("/search", response_model=PaginatedResponse[ListingResponse])
async def search_listings(
    request: Request,
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
    deal_type_id: Optional[int] = None,
    property_type_id: Optional[int] = None,
    market_type_id: Optional[int] = None,
    renovation_condition_id: Optional[int] = None,
    sort_by: str = "date_desc",
    db: Session = Depends(get_db)
):
    skip = (page - 1) * page_size
    query_builder = db.query(Listing).filter(Listing.listing_status_id == 1, Listing.moderated == True)

    if query:
        query_builder = query_builder.filter(or_(Listing.title.ilike(f"%{query}%"), Listing.description.ilike(f"%{query}%")))
    if city:
        query_builder = query_builder.join(Address, Listing.address_id == Address.address_id).join(City, Address.city_id == City.city_id).filter(City.name.ilike(f"%{city}%"))
    if min_price is not None: query_builder = query_builder.filter(Listing.price >= min_price)
    if max_price is not None: query_builder = query_builder.filter(Listing.price <= max_price)
    if min_area is not None: query_builder = query_builder.filter(Listing.total_area >= min_area)
    if max_area is not None: query_builder = query_builder.filter(Listing.total_area <= max_area)
    if rooms is not None:
        if rooms >= 4: query_builder = query_builder.filter(Listing.rooms >= 4)
        else: query_builder = query_builder.filter(Listing.rooms == rooms)
    if floor is not None: query_builder = query_builder.filter(Listing.floor == floor)
    if deal_type_id is not None: query_builder = query_builder.filter(Listing.deal_type_id == deal_type_id)
    if property_type_id is not None: query_builder = query_builder.filter(Listing.property_type_id == property_type_id)
    if market_type_id is not None: query_builder = query_builder.filter(Listing.market_type_id == market_type_id)
    if renovation_condition_id is not None: query_builder = query_builder.filter(Listing.renovation_condition_id == renovation_condition_id)

    sort_map = {"price_asc": Listing.price.asc(), "price_desc": Listing.price.desc(), "views_desc": Listing.views.desc(), "area_asc": Listing.total_area.asc(), "area_desc": Listing.total_area.desc(), "date_desc": Listing.publication_date.desc(), "date_asc": Listing.publication_date.asc()}
    query_builder = query_builder.order_by(sort_map.get(sort_by, Listing.publication_date.desc()))

    total = query_builder.count()
    listings = query_builder.offset(skip).limit(page_size).all()

    # Сохранить запрос в search_statistics
    search_query_text = query or city or ""
    filters = {}
    for k, v in request.query_params.items():
        if v and k not in ('page', 'page_size'):
            filters[k] = v

    try:
        stat = SearchStatistics(
            user_id=None,
            search_query=search_query_text,
            filters_json=filters,
            results_count=total
        )
        db.add(stat)
        db.commit()
    except Exception:
        pass

    return {"items": [_enrich_listing(l, db) for l in listings], "total": total, "page": page, "size": page_size, "pages": (total + page_size - 1) // page_size if total > 0 else 0}


@router.get("/{listing_id}", response_model=ListingResponse)
async def get_listing(listing_id: int, db: Session = Depends(get_db)):
    listing = listing_crud.get(db, listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Объявление не найдено")
    listing_crud.increment_views(db, listing_id)
    return _enrich_listing(listing, db)


@router.get("/{listing_id}/photos")
async def get_listing_photos(listing_id: int, db: Session = Depends(get_db)):
    photos = photo_crud.get_by_listing(db, listing_id)
    return [{"photo_id": p.photo_id, "file_url": p.file_url, "title": p.title} for p in photos]


@router.post("/{listing_id}/view")
async def register_view(listing_id: int, request: Request, current_user: Optional[Users] = Depends(get_current_user_optional), db: Session = Depends(get_db)):
    listing_crud.register_view(db, listing_id=listing_id, user_id=current_user.user_id if current_user else None, ip_address=request.client.host if request.client else None)
    action_log_crud.log(db, current_user.user_id if current_user else None, 1, listing_id=listing_id, ip_address=request.client.host, user_agent=request.headers.get("user-agent"))
    return {"status": "ok"}


@router.post("/", response_model=ListingResponse, status_code=201)
async def create_listing(listing_data: ListingCreate, request: Request, db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    new_listing = listing_crud.create(db, listing_data, current_user.user_id)
    action_log_crud.log(db, current_user.user_id, 2, listing_id=new_listing.listing_id, ip_address=request.client.host, user_agent=request.headers.get("user-agent"))
    return _enrich_listing(new_listing, db)


@router.put("/{listing_id}", response_model=ListingResponse)
async def update_listing(listing_id: int, listing_update: ListingUpdate, request: Request, db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    listing = listing_crud.get(db, listing_id)
    if not listing: raise HTTPException(status_code=404, detail="Объявление не найдено")
    if listing.user_id != current_user.user_id: raise HTTPException(status_code=403, detail="Нет доступа")
    updated = listing_crud.update(db, listing, listing_update)
    action_log_crud.log(db, current_user.user_id, 3, listing_id=listing_id, ip_address=request.client.host, user_agent=request.headers.get("user-agent"))
    return _enrich_listing(updated, db)


@router.delete("/{listing_id}", response_model=MessageResponse)
async def delete_listing(listing_id: int, request: Request, db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    listing = listing_crud.get(db, listing_id)
    if not listing: raise HTTPException(status_code=404, detail="Объявление не найдено")
    if listing.user_id != current_user.user_id: raise HTTPException(status_code=403, detail="Нет доступа")
    action_log_crud.log(db, current_user.user_id, 4, listing_id=listing_id, ip_address=request.client.host, user_agent=request.headers.get("user-agent"))
    listing_crud.delete_obj(db, listing)
    return {"message": "Объявление удалено", "success": True}


@router.get("/my/list", response_model=List[ListingResponse])
async def get_my_listings(db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    listings = listing_crud.get_by_user(db, current_user.user_id)
    return [_enrich_listing(l, db) for l in listings]