from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import date

class DashboardResponse(BaseModel):
    total_listings: int
    active_today: int
    views_today: int
    new_listings_today: int

class PopularListingResponse(BaseModel):
    listing_id: int
    title: str
    price: float
    address: str
    views: int
    photo: Optional[str] = None

class PriceStatsResponse(BaseModel):
    total_active: int
    avg_price: float
    avg_price_per_m2: float
    min_price: float
    max_price: float
    price_ranges: Dict[str, int]
    by_type: List[dict]

class ViewsStatsResponse(BaseModel):
    period: str
    total_views: int
    unique_listings: int
    unique_visitors: int
    views_by_day: List[dict]

class SearchQueriesResponse(BaseModel):
    total_searches: int
    popular_queries: List[dict]

class ClosedDealsResponse(BaseModel):
    period: str
    total_closed: int
    total_revenue: float
    avg_days_to_sell: float
    by_type: List[dict]