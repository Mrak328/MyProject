from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import date, timedelta
from app.database import get_db
from app.crud.analytics import analytics_crud
from app.schemas.analytics import (
    DashboardResponse,
    PopularListingResponse,
    PriceStatsResponse,
    ViewsStatsResponse,
    SearchQueriesResponse,
    ClosedDealsResponse
)

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(db: Session = Depends(get_db)):
    return analytics_crud.get_dashboard_stats(db)


@router.get("/listings/popular", response_model=List[PopularListingResponse])
async def get_popular_listings(
    period: str = Query("week", pattern="^(day|week|month)$"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    return analytics_crud.get_popular_listings(db, period, limit)


@router.get("/views", response_model=ViewsStatsResponse)
async def get_views_stats(
    period: str = Query("week", pattern="^(day|week|month)$"),
    db: Session = Depends(get_db)
):
    result = analytics_crud.get_views_stats(db, period)
    today = date.today()
    days_map = {"day": 1, "week": 7, "month": 30}
    delta = days_map.get(period, 7)
    result["date_from"] = str(today - timedelta(days=delta))
    result["date_to"] = str(today)
    for day in result.get("views_by_day", []):
        day["unique_visitors"] = day.get("unique_visitors", 0)
        day["unique_listings"] = day.get("unique_listings", 0)
    return result


@router.get("/prices", response_model=PriceStatsResponse)
async def get_price_stats(db: Session = Depends(get_db)):
    return analytics_crud.get_price_stats(db)


@router.get("/search/queries", response_model=SearchQueriesResponse)
async def get_search_queries(
    days: int = Query(30, ge=1, le=90),
    db: Session = Depends(get_db)
):
    result = analytics_crud.get_search_queries(db, days)
    result["period"] = f"{days}d"
    return result


@router.get("/deals/closed", response_model=ClosedDealsResponse)
async def get_closed_deals(
    period: str = Query("month", pattern="^(week|month|year)$"),
    db: Session = Depends(get_db)
):
    result = analytics_crud.get_closed_deals(db, period)
    today = date.today()
    days_map = {"week": 7, "month": 30, "year": 365}
    delta = days_map.get(period, 30)
    result["date_from"] = str(today - timedelta(days=delta))
    result["date_to"] = str(today)
    result["avg_price"] = result.get("avg_price", result.get("total_revenue", 0) / max(result.get("total_closed", 1), 1))
    return result