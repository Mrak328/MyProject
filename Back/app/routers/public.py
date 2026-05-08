from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from app.database import get_db
from app.models import Listing, PropertyType, DealType, City, Region
from app.schemas.analytics import PriceStatsResponse
from app.crud.analytics import analytics_crud

router = APIRouter(prefix="/public", tags=["public"])


@router.get("/market-overview")
async def get_market_overview(db: Session = Depends(get_db)):
    """Обзор рынка: общая статистика"""
    total_listings = db.query(Listing).filter(
        Listing.listing_status_id == 1,
        Listing.moderated == True
    ).count()

    avg_price = db.query(func.avg(Listing.price)).filter(
        Listing.listing_status_id == 1,
        Listing.moderated == True,
        Listing.price.isnot(None)
    ).scalar()

    avg_area = db.query(func.avg(Listing.total_area)).filter(
        Listing.listing_status_id == 1,
        Listing.moderated == True,
        Listing.total_area.isnot(None)
    ).scalar()

    new_today = db.query(Listing).filter(
        func.date(Listing.publication_date) == func.current_date()
    ).count()

    return {
        "total_listings": total_listings,
        "avg_price": round(float(avg_price), 2) if avg_price else 0,
        "avg_price_per_m2": round(float(avg_price) / float(avg_area), 2) if avg_price and avg_area else 0,
        "avg_area": round(float(avg_area), 2) if avg_area else 0,
        "new_today": new_today
    }


@router.get("/property-types")
async def get_property_types(db: Session = Depends(get_db)):
    """Список типов недвижимости с количеством объявлений"""
    types = (
        db.query(
            PropertyType.property_type_id,
            PropertyType.name,
            func.count(Listing.listing_id).label('count')
        )
        .outerjoin(Listing, Listing.property_type_id == PropertyType.property_type_id)
        .group_by(PropertyType.property_type_id, PropertyType.name)
        .order_by(PropertyType.property_type_id)
        .all()
    )
    return [
        {"property_type_id": t.property_type_id, "name": t.name, "count": t.count}
        for t in types
    ]


@router.get("/deal-types")
async def get_deal_types(db: Session = Depends(get_db)):
    """Список типов сделок"""
    types = db.query(DealType).all()
    return [{"deal_type_id": t.deal_type_id, "name": t.name} for t in types]


@router.get("/cities")
async def get_cities(
    region_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Список городов (опционально по региону)"""
    query = db.query(City)
    if region_id:
        query = query.filter(City.region_id == region_id)
    cities = query.order_by(City.name).all()
    return [{"city_id": c.city_id, "name": c.name, "region_id": c.region_id} for c in cities]


@router.get("/regions")
async def get_regions(
    country_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Список регионов (опционально по стране)"""
    query = db.query(Region)
    if country_id:
        query = query.filter(Region.country_id == country_id)
    regions = query.order_by(Region.name).all()
    return [{"region_id": r.region_id, "name": r.name, "country_id": r.country_id} for r in regions]


@router.get("/prices", response_model=PriceStatsResponse)
async def get_price_stats(db: Session = Depends(get_db)):
    """Ценовая статистика по активным объявлениям"""
    return analytics_crud.get_price_stats(db)


@router.get("/latest-listings")
async def get_latest_listings(
    limit: int = Query(6, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """Последние опубликованные объявления (для главной)"""
    from app.crud.photo import photo_crud

    listings = (
        db.query(Listing)
        .filter(
            Listing.listing_status_id == 1,
            Listing.moderated == True
        )
        .order_by(Listing.publication_date.desc())
        .limit(limit)
        .all()
    )

    result = []
    for l in listings:
        photos = photo_crud.get_by_listing(db, l.listing_id)
        result.append({
            "listing_id": l.listing_id,
            "title": l.title,
            "price": l.price,
            "total_area": l.total_area,
            "rooms": l.rooms,
            "floor": l.floor,
            "max_floor": l.max_floor,
            "publication_date": l.publication_date,
            "photo": photos[0].file_url if photos else None,
            "city": l.address.city.name if l.address and l.address.city else None
        })

    return result