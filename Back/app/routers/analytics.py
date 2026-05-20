from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import date, timedelta, datetime
from app.database import get_db
from app.crud.analytics import analytics_crud
from app.models import SearchStatistics, City, PropertyType, DealType, RenovationCondition
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
    queries = result.get("popular_queries", [])
    filtered = [
        q for q in queries
        if q.get("query") and q["query"].strip()
        and q["query"].strip().lower() not in ("другое", "пустой запрос", "")
    ]
    result["popular_queries"] = filtered
    result["period"] = f"{days}d"
    return result


@router.get("/search/details")
async def get_search_details(
    days: int = Query(30, ge=1, le=90),
    db: Session = Depends(get_db)
):
    """Детализация поиска: города, типы, сделки, комнаты, цены, площади, этажи, ремонт"""
    start = datetime.now() - timedelta(days=days)

    stats = db.query(SearchStatistics).filter(
        SearchStatistics.search_datetime >= start
    ).all()

    cities = {}
    property_types = {}
    deal_types = {}
    price_ranges = {"до 1 млн": 0, "1-3 млн": 0, "3-5 млн": 0, "5-10 млн": 0, "10+ млн": 0}
    rooms_count = {}
    areas = {}
    floors = {}
    renovation = {}

    for s in stats:
        filters = s.filters_json or {}

        # Город
        city_id = filters.get("city_id")
        if city_id:
            city = db.query(City).filter(City.city_id == city_id).first()
            name = city.name if city else str(city_id)
            cities[name] = cities.get(name, 0) + 1

        # Тип недвижимости
        pt_id = filters.get("property_type_id")
        if pt_id:
            pt = db.query(PropertyType).filter(PropertyType.property_type_id == pt_id).first()
            name = pt.name if pt else str(pt_id)
            property_types[name] = property_types.get(name, 0) + 1

        # Тип сделки
        dt_id = filters.get("deal_type_id")
        if dt_id:
            dt = db.query(DealType).filter(DealType.deal_type_id == dt_id).first()
            name = dt.name if dt else str(dt_id)
            deal_types[name] = deal_types.get(name, 0) + 1

        # Цена
        min_p = filters.get("min_price")
        max_p = filters.get("max_price")
        price = float(min_p or max_p or 0)
        if price:
            if price < 1000000: price_ranges["до 1 млн"] += 1
            elif price < 3000000: price_ranges["1-3 млн"] += 1
            elif price < 5000000: price_ranges["3-5 млн"] += 1
            elif price < 10000000: price_ranges["5-10 млн"] += 1
            else: price_ranges["10+ млн"] += 1

        # Комнаты
        rooms = filters.get("rooms")
        if rooms:
            rooms_count[str(rooms)] = rooms_count.get(str(rooms), 0) + 1

        # Площадь
        min_a = filters.get("min_area")
        max_a = filters.get("max_area")
        area = float(min_a or max_a or 0)
        if area:
            if area < 30: areas["до 30 м²"] = areas.get("до 30 м²", 0) + 1
            elif area < 50: areas["30-50 м²"] = areas.get("30-50 м²", 0) + 1
            elif area < 80: areas["50-80 м²"] = areas.get("50-80 м²", 0) + 1
            else: areas["80+ м²"] = areas.get("80+ м²", 0) + 1

        # Этаж
        floor = filters.get("floor")
        if floor:
            floors[str(floor)] = floors.get(str(floor), 0) + 1

        # Ремонт
        ren_id = filters.get("renovation_condition_id")
        if ren_id:
            ren = db.query(RenovationCondition).filter(RenovationCondition.renovation_condition_id == ren_id).first()
            name = ren.name if ren else str(ren_id)
            renovation[name] = renovation.get(name, 0) + 1

    return {
        "total_searches": len(stats),
        "cities": dict(sorted(cities.items(), key=lambda x: x[1], reverse=True)),
        "property_types": dict(sorted(property_types.items(), key=lambda x: x[1], reverse=True)),
        "deal_types": dict(sorted(deal_types.items(), key=lambda x: x[1], reverse=True)),
        "price_ranges": price_ranges,
        "rooms": dict(sorted(rooms_count.items(), key=lambda x: int(x[0]))),
        "areas": dict(sorted(areas.items(), key=lambda x: x[0])),
        "floors": dict(sorted(floors.items(), key=lambda x: int(x[0]))),
        "renovation": dict(sorted(renovation.items(), key=lambda x: x[1], reverse=True))
    }


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