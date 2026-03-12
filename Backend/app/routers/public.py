from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app import crud

router = APIRouter(prefix="/public", tags=["public"])

@router.get("/market-overview")
async def get_market_overview(
    city: str,
    property_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Обзор рынка для покупателей"""
    stats = crud.get_market_stats(db, city, property_type)
    return {
        "city": city,
        "total_offers": stats["total"],
        "avg_price_per_m2": stats["avg_price_per_m2"],
        "price_change_month": stats["price_change"],
        "popular_districts": stats["popular_districts"][:5]
    }

@router.get("/district/{district}")
async def get_district_info(
    district: str,
    city: str,
    db: Session = Depends(get_db)
):
    """Информация о районе"""
    return crud.get_district_stats(db, city, district)

@router.get("/price-trends")
async def get_price_trends(
    city: str,
    property_type: str = "apartment",
    months: int = 6,
    db: Session = Depends(get_db)
):
    """Динамика цен за период"""
    return crud.get_price_trends(db, city, property_type, months)