from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
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
async def get_dashboard(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    return analytics_crud.get_dashboard_stats(db)

@router.get("/listings/popular", response_model=list[PopularListingResponse])
async def get_popular_listings(
    period: str = Query("week", regex="^(day|week|month)$"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    return analytics_crud.get_popular_listings(db, period, limit)

@router.get("/views", response_model=ViewsStatsResponse)
async def get_views_stats(
    period: str = Query("week", regex="^(day|week|month)$"),
    db: Session = Depends(get_db)
):
    return analytics_crud.get_views_stats(db, period)

@router.get("/prices", response_model=PriceStatsResponse)
async def get_price_stats(db: Session = Depends(get_db)):
    return analytics_crud.get_price_stats(db)

@router.get("/search/queries", response_model=SearchQueriesResponse)
async def get_search_queries(
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db)
):
    return analytics_crud.get_search_queries(db, days)

@router.get("/closed_deals", response_model=ClosedDealsResponse)
async def get_closed_deals(
    period: str = Query("month", regex="^(week|month|year)$"),
    db: Session = Depends(get_db)
):
    return analytics_crud.get_closed_deals(db, period)