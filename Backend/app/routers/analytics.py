from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional
from datetime import date, timedelta, datetime
from app.database import get_db
from app import models

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/dashboard")
async def get_dashboard(
        days: int = Query(30, ge=1, le=365),
        db: Session = Depends(get_db)
):
    """Главная статистика сайта"""
    today = date.today()

    total_listings = db.query(models.Listing).count()

    active_today = db.query(models.Listing).filter(
        models.Listing.listing_status_id == 1,
        func.date(models.Listing.publication_date) == today
    ).count()

    views_today = db.query(models.ListingViewStatistics).filter(
        models.ListingViewStatistics.view_date == today
    ).count()

    new_listings_today = db.query(models.Listing).filter(
        func.date(models.Listing.publication_date) == today
    ).count()

    return {
        "total_listings": total_listings,
        "active_today": active_today,
        "views_today": views_today,
        "new_listings_today": new_listings_today
    }


@router.get("/listings/popular")
async def get_popular_listings(
        period: str = Query("week", regex="^(day|week|month)$"),
        limit: int = Query(10, ge=1, le=50),
        db: Session = Depends(get_db)
):
    """Самые просматриваемые объявления за период"""
    today = date.today()

    if period == "day":
        start_date = today - timedelta(days=1)
    elif period == "week":
        start_date = today - timedelta(days=7)
    else:  # month
        start_date = today - timedelta(days=30)

    listings = db.query(
        models.Listing,
        func.count(models.ListingViewStatistics.record_id).label('view_count')
    ).outerjoin(
        models.ListingViewStatistics,
        models.Listing.listing_id == models.ListingViewStatistics.listing_id
    ).filter(
        models.Listing.listing_status_id == 1,
        models.ListingViewStatistics.view_date >= start_date
    ).group_by(
        models.Listing.listing_id
    ).order_by(
        desc('view_count')
    ).limit(limit).all()

    result = []
    for listing, view_count in listings:
        photo = db.query(models.Photo).filter(
            models.Photo.listing_id == listing.listing_id
        ).first()

        result.append({
            "listing_id": listing.listing_id,
            "title": listing.title,
            "price": float(listing.price) if listing.price else 0,
            "address": listing.address,
            "views": view_count,
            "photo": photo.file_url if photo else None
        })

    return result


@router.get("/views")
async def get_views_statistics(
        period: str = Query("week", regex="^(day|week|month)$"),
        db: Session = Depends(get_db)
):
    """Статистика просмотров за период"""
    today = date.today()

    if period == "day":
        start_date = today - timedelta(days=1)
    elif period == "week":
        start_date = today - timedelta(days=7)
    else:  # month
        start_date = today - timedelta(days=30)

    total_views = db.query(models.ListingViewStatistics).filter(
        models.ListingViewStatistics.view_date >= start_date
    ).count()

    unique_listings = db.query(models.ListingViewStatistics.listing_id).distinct().filter(
        models.ListingViewStatistics.view_date >= start_date
    ).count()

    unique_visitors = db.query(models.ListingViewStatistics.user_id).distinct().filter(
        models.ListingViewStatistics.view_date >= start_date,
        models.ListingViewStatistics.user_id.isnot(None)
    ).count()

    views_by_day = db.query(
        func.date(models.ListingViewStatistics.view_date).label('date'),
        func.count(models.ListingViewStatistics.record_id).label('count')
    ).filter(
        models.ListingViewStatistics.view_date >= start_date
    ).group_by(
        func.date(models.ListingViewStatistics.view_date)
    ).order_by(
        'date'
    ).all()

    return {
        "period": period,
        "total_views": total_views,
        "unique_listings": unique_listings,
        "unique_visitors": unique_visitors,
        "views_by_day": [{"date": str(d.date), "count": d.count} for d in views_by_day]
    }


@router.get("/search/queries")
async def get_search_analytics(
        days: int = Query(7, ge=1, le=90),
        db: Session = Depends(get_db)
):
    """Аналитика поисковых запросов"""
    start_date = datetime.now() - timedelta(days=days)

    popular = db.query(
        models.SearchStatistics.search_query,
        func.count(models.SearchStatistics.record_id).label('count')
    ).filter(
        models.SearchStatistics.search_datetime >= start_date,
        models.SearchStatistics.search_query.isnot(None)
    ).group_by(
        models.SearchStatistics.search_query
    ).order_by(
        desc('count')
    ).limit(20).all()

    total_searches = db.query(models.SearchStatistics).filter(
        models.SearchStatistics.search_datetime >= start_date
    ).count()

    return {
        "total_searches": total_searches,
        "popular_queries": [
            {"query": q[0] or "пустой запрос", "count": q[1]}
            for q in popular
        ]
    }


@router.get("/prices")
async def get_price_statistics(
        db: Session = Depends(get_db)
):
    """Детальная статистика цен по активным объявлениям"""
    active_listings = db.query(models.Listing).filter(
        models.Listing.listing_status_id == 1,
        models.Listing.price.isnot(None)
    ).all()

    if not active_listings:
        return {
            "total_active": 0,
            "avg_price": 0,
            "avg_price_per_m2": 0,
            "min_price": 0,
            "max_price": 0,
            "by_type": []
        }

    prices = [float(l.price) for l in active_listings if l.price]
    min_price = min(prices) if prices else 0
    max_price = max(prices) if prices else 0
    avg_price = sum(prices) / len(prices) if prices else 0

    prices_per_m2 = []
    for l in active_listings:
        if l.price and l.total_area and l.total_area > 0:
            prices_per_m2.append(float(l.price) / float(l.total_area))

    avg_price_per_m2 = sum(prices_per_m2) / len(prices_per_m2) if prices_per_m2 else 0

    property_types = db.query(models.PropertyType).all()
    by_type = []

    for pt in property_types:
        type_listings = [l for l in active_listings if l.property_type_id == pt.property_type_id]
        if type_listings:
            type_prices = [float(l.price) for l in type_listings if l.price]
            type_prices_per_m2 = []
            for l in type_listings:
                if l.price and l.total_area and l.total_area > 0:
                    type_prices_per_m2.append(float(l.price) / float(l.total_area))

            by_type.append({
                "type": pt.name,
                "count": len(type_listings),
                "avg_price": sum(type_prices) / len(type_prices) if type_prices else 0,
                "avg_price_per_m2": sum(type_prices_per_m2) / len(type_prices_per_m2) if type_prices_per_m2 else 0
            })

    return {
        "total_active": len(active_listings),
        "avg_price": round(avg_price, 2),
        "avg_price_per_m2": round(avg_price_per_m2, 2),
        "min_price": round(min_price, 2),
        "max_price": round(max_price, 2),
        "by_type": by_type
    }


@router.get("/closed_deals")
async def get_closed_deals_statistics(
        period: str = Query("month", regex="^(week|month|year)$"),
        db: Session = Depends(get_db)
):
    """Статистика по закрытым сделкам"""
    today = date.today()

    if period == "week":
        start_date = today - timedelta(days=7)
    elif period == "month":
        start_date = today - timedelta(days=30)
    else:  # year
        start_date = today - timedelta(days=365)

    closed = db.query(models.Listing).filter(
        models.Listing.listing_status_id == 3,
        models.Listing.moderation_date >= start_date
    ).all()

    if not closed:
        return {
            "period": period,
            "total_closed": 0,
            "total_revenue": 0,
            "avg_days_to_sell": 0,
            "by_type": []
        }

    prices = [float(l.price) for l in closed if l.price]
    total_revenue = sum(prices) if prices else 0

    # Среднее время продажи
    days_diff = []
    for l in closed:
        if l.publication_date and l.moderation_date:
            diff = (l.moderation_date - l.publication_date).days
            if diff >= 0:
                days_diff.append(diff)

    avg_days = sum(days_diff) / len(days_diff) if days_diff else 0

    property_types = db.query(models.PropertyType).all()
    by_type = []

    for pt in property_types:
        type_closed = [l for l in closed if l.property_type_id == pt.property_type_id]
        if type_closed:
            type_prices = [float(l.price) for l in type_closed if l.price]
            by_type.append({
                "type": pt.name,
                "count": len(type_closed),
                "total_revenue": sum(type_prices) if type_prices else 0,
                "avg_price": sum(type_prices) / len(type_prices) if type_prices else 0
            })

    return {
        "period": period,
        "total_closed": len(closed),
        "total_revenue": total_revenue,
        "avg_days_to_sell": round(avg_days, 1),
        "by_type": by_type
    }


@router.get("/prices")
async def get_price_statistics(
        db: Session = Depends(get_db)
):
    """Детальная статистика цен по активным объявлениям"""
    print("\n" + "=" * 50)
    print("НАЧАЛО РАСЧЕТА СТАТИСТИКИ ЦЕН")
    print("=" * 50)

    # Только активные объявления (status_id = 1)
    active_listings = db.query(models.Listing).filter(
        models.Listing.listing_status_id == 1,
        models.Listing.price.isnot(None)
    ).all()

    print(f"Всего активных объявлений с ценой: {len(active_listings)}")

    if not active_listings:
        print("НЕТ АКТИВНЫХ ОБЪЯВЛЕНИЙ!")
        return {
            "total_active": 0,
            "avg_price": 0,
            "median_price": 0,
            "min_price": 0,
            "max_price": 0,
            "price_per_m2": {
                "avg": 0,
                "min": 0,
                "max": 0
            },
            "price_ranges": {},
            "by_type": []
        }

    # Считаем объявления с площадью
    listings_with_area = [l for l in active_listings if l.total_area and l.total_area > 0]
    print(f"Объявлений с площадью: {len(listings_with_area)}")

    # Все цены
    prices = [float(l.price) for l in active_listings if l.price]
    print(f"Всего цен: {len(prices)}")
    if prices:
        print(f"Примеры цен: {prices[:5]}")

    # Основная статистика
    min_price = min(prices) if prices else 0
    max_price = max(prices) if prices else 0
    avg_price = sum(prices) / len(prices) if prices else 0

    print(f"Мин цена: {min_price}")
    print(f"Макс цена: {max_price}")
    print(f"Средняя цена: {avg_price}")

    # Медианная цена
    if prices:
        prices.sort()
        n = len(prices)
        if n % 2 == 0:
            median_price = (prices[n // 2 - 1] + prices[n // 2]) / 2
        else:
            median_price = prices[n // 2]
        print(f"Медианная цена: {median_price}")
    else:
        median_price = 0

    # Цена за м² - детальный расчет
    prices_per_m2 = []
    print("\n--- ДЕТАЛЬНЫЙ РАСЧЕТ ЦЕНЫ ЗА М² ---")
    for i, l in enumerate(active_listings):
        if l.price and l.total_area and l.total_area > 0:
            try:
                price = float(l.price)
                area = float(l.total_area)
                price_per_m2 = price / area
                prices_per_m2.append(price_per_m2)
                print(f"  {i + 1}. ID:{l.listing_id} Цена:{price} Площадь:{area} = {price_per_m2:.2f} ₽/м²")
            except Exception as e:
                print(f"  Ошибка расчета для ID {l.listing_id}: {e}")
        else:
            print(f"  {i + 1}. ID:{l.listing_id} - НЕТ ПЛОЩАДИ (total_area={l.total_area})")

    print(f"\nВсего рассчитано цен за м²: {len(prices_per_m2)}")

    if prices_per_m2:
        avg_price_per_m2 = sum(prices_per_m2) / len(prices_per_m2)
        min_price_per_m2 = min(prices_per_m2)
        max_price_per_m2 = max(prices_per_m2)
        print(f"Средняя цена за м²: {avg_price_per_m2}")
        print(f"Мин цена за м²: {min_price_per_m2}")
        print(f"Макс цена за м²: {max_price_per_m2}")
    else:
        avg_price_per_m2 = 0
        min_price_per_m2 = 0
        max_price_per_m2 = 0
        print("НЕТ ДАННЫХ ДЛЯ РАСЧЕТА ЦЕНЫ ЗА М²!")

    # Распределение по ценовым диапазонам
    price_ranges = {
        "до 2 млн": 0,
        "2-4 млн": 0,
        "4-6 млн": 0,
        "6-10 млн": 0,
        "10-15 млн": 0,
        "более 15 млн": 0
    }

    for price in prices:
        if price < 2000000:
            price_ranges["до 2 млн"] += 1
        elif price < 4000000:
            price_ranges["2-4 млн"] += 1
        elif price < 6000000:
            price_ranges["4-6 млн"] += 1
        elif price < 10000000:
            price_ranges["6-10 млн"] += 1
        elif price < 15000000:
            price_ranges["10-15 млн"] += 1
        else:
            price_ranges["более 15 млн"] += 1

    # Статистика по типам недвижимости
    property_types = db.query(models.PropertyType).all()
    by_type = []

    for pt in property_types:
        type_listings = [l for l in active_listings if l.property_type_id == pt.property_type_id]
        if type_listings:
            type_prices = [float(l.price) for l in type_listings if l.price]

            # Цена за м² для этого типа
            type_prices_per_m2 = []
            for l in type_listings:
                if l.price and l.total_area and l.total_area > 0:
                    try:
                        type_prices_per_m2.append(float(l.price) / float(l.total_area))
                    except:
                        pass

            by_type.append({
                "type": pt.name,
                "count": len(type_listings),
                "avg_price": sum(type_prices) / len(type_prices) if type_prices else 0,
                "min_price": min(type_prices) if type_prices else 0,
                "max_price": max(type_prices) if type_prices else 0,
                "avg_price_per_m2": sum(type_prices_per_m2) / len(type_prices_per_m2) if type_prices_per_m2 else 0,
                "total_value": sum(type_prices) if type_prices else 0
            })

    print("\n" + "=" * 50)
    print("ИТОГОВЫЙ РЕЗУЛЬТАТ:")
    print("=" * 50)
    result = {
        "total_active": len(active_listings),
        "avg_price": round(avg_price, 2),
        "median_price": round(median_price, 2),
        "min_price": round(min_price, 2),
        "max_price": round(max_price, 2),
        "price_per_m2": {
            "avg": round(avg_price_per_m2, 2),
            "min": round(min_price_per_m2, 2),
            "max": round(max_price_per_m2, 2)
        },
        "price_ranges": price_ranges,
        "by_type": by_type
    }

    print(f"total_active: {result['total_active']}")
    print(f"price_per_m2.avg: {result['price_per_m2']['avg']}")
    print("=" * 50)

    return result