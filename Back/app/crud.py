from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc, extract, case
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from decimal import Decimal
import app.models as models
import app.schemas as schemas

# User CRUD
def get_user(db: Session, user_id: int):
    return db.query(models.Users).filter(models.Users.user_id == user_id).first()


def get_user_by_phone(db: Session, phone: str):
    return db.query(models.Users).filter(models.Users.phone_number == phone).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.Users).filter(models.Users.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Users).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.Users(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate):
    db_user = db.query(models.Users).filter(models.Users.user_id == user_id).first()
    if db_user:
        for key, value in user_update.dict(exclude_unset=True).items():
            setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int):
    db_user = db.query(models.Users).filter(models.Users.user_id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False


# Listing CRUD
def get_listing(db: Session, listing_id: int):
    return db.query(models.Listing).filter(models.Listing.listing_id == listing_id).first()


def get_listings(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        status_id: Optional[int] = None,
        deal_type_id: Optional[int] = None,
        property_type_id: Optional[int] = None,
        min_price: Optional[Decimal] = None,
        max_price: Optional[Decimal] = None,
        user_id: Optional[int] = None
):
    query = db.query(models.Listing)

    if status_id:
        query = query.filter(models.Listing.listing_status_id == status_id)
    if deal_type_id:
        query = query.filter(models.Listing.deal_type_id == deal_type_id)
    if property_type_id:
        query = query.filter(models.Listing.property_type_id == property_type_id)
    if min_price:
        query = query.filter(models.Listing.price >= min_price)
    if max_price:
        query = query.filter(models.Listing.price <= max_price)
    if user_id:
        query = query.filter(models.Listing.user_id == user_id)

    return query.offset(skip).limit(limit).all()


def create_listing(db: Session, listing: schemas.ListingCreate):
    db_listing = models.Listing(**listing.dict())
    db.add(db_listing)
    db.commit()
    db.refresh(db_listing)
    return db_listing


def update_listing(db: Session, listing_id: int, listing_update: schemas.ListingUpdate):
    db_listing = db.query(models.Listing).filter(models.Listing.listing_id == listing_id).first()
    if db_listing:
        for key, value in listing_update.dict(exclude_unset=True).items():
            setattr(db_listing, key, value)
        db_listing.update_date = datetime.now()
        db.commit()
        db.refresh(db_listing)
    return db_listing


def delete_listing(db: Session, listing_id: int):
    db_listing = db.query(models.Listing).filter(models.Listing.listing_id == listing_id).first()
    if db_listing:
        db.delete(db_listing)
        db.commit()
        return True
    return False


# Photo CRUD
def get_photos_by_listing(db: Session, listing_id: int):
    return db.query(models.Photo).filter(models.Photo.listing_id == listing_id).all()


def create_photo(db: Session, photo: schemas.PhotoCreate):
    db_photo = models.Photo(**photo.dict())
    db.add(db_photo)
    db.commit()
    db.refresh(db_photo)
    return db_photo


# Review CRUD
def get_reviews_by_user(db: Session, user_id: int):
    return db.query(models.Review).filter(models.Review.user_id == user_id).all()


def create_review(db: Session, review: schemas.ReviewCreate):
    db_review = models.Review(**review.dict())
    db.add(db_review)
    db.commit()
    db.refresh(db_review)

    # Update user rating
    update_user_rating(db, review.user_id)

    return db_review


def update_user_rating(db: Session, user_id: int):
    """Update user's average rating based on reviews"""
    reviews = db.query(models.Review).filter(models.Review.user_id == user_id).all()
    if reviews:
        avg_rating = sum(r.rating for r in reviews) / len(reviews)
        user = get_user(db, user_id)
        if user:
            user.rating = avg_rating
            user.reviews_count = len(reviews)
            db.commit()


# Favorite CRUD
def get_favorites_by_user(db: Session, user_id: int):
    return db.query(models.Favorite).filter(models.Favorite.user_id == user_id).all()


def add_favorite(db: Session, favorite: schemas.FavoriteCreate):
    db_favorite = models.Favorite(**favorite.dict())
    db.add(db_favorite)
    db.commit()
    db.refresh(db_favorite)
    return db_favorite


def remove_favorite(db: Session, user_id: int, listing_id: int):
    db_favorite = db.query(models.Favorite).filter(
        models.Favorite.user_id == user_id,
        models.Favorite.listing_id == listing_id
    ).first()
    if db_favorite:
        db.delete(db_favorite)
        db.commit()
        return True
    return False


# Analytics CRUD
def get_sales_analytics(db: Session, start_date: date, end_date: date) -> schemas.SalesAnalytics:
    # Total listings
    total_listings = db.query(models.Listing).count()

    # Active listings (assuming status_id = 1 for active)
    active_listings = db.query(models.Listing).filter(
        models.Listing.listing_status_id == 1
    ).count()

    # Sold listings (assuming status_id = 3 for sold)
    sold_listings = db.query(models.Listing).filter(
        models.Listing.listing_status_id == 3
    ).count()

    # Total revenue from sold listings
    total_revenue = db.query(func.sum(models.Listing.price)).filter(
        models.Listing.listing_status_id == 3,
        models.Listing.moderation_date.between(start_date, end_date)
    ).scalar() or Decimal('0')

    # Average price
    avg_price = db.query(func.avg(models.Listing.price)).filter(
        models.Listing.listing_status_id == 3
    ).scalar() or 0

    # Average days on market
    avg_days = db.query(
        func.avg(
            func.extract('day', models.Listing.moderation_date - models.Listing.publication_date)
        )
    ).filter(
        models.Listing.listing_status_id == 3,
        models.Listing.moderation_date.isnot(None)
    ).scalar() or 0

    # Conversion rate (views to contacts opened)
    conversion_data = db.query(
        func.sum(models.ListingPerformance.contacts_opened).label('total_contacts'),
        func.sum(models.ListingPerformance.total_views).label('total_views')
    ).filter(
        models.ListingPerformance.calculation_date.between(start_date, end_date)
    ).first()

    conversion_rate = 0
    if conversion_data.total_views and conversion_data.total_views > 0:
        conversion_rate = (conversion_data.total_contacts / conversion_data.total_views) * 100

    return schemas.SalesAnalytics(
        total_listings=total_listings,
        active_listings=active_listings,
        sold_listings=sold_listings,
        total_revenue=total_revenue,
        average_price=float(avg_price),
        average_days_on_market=float(avg_days) if avg_days else 0,
        conversion_rate=float(conversion_rate)
    )


def get_listing_performance(db: Session, listing_id: int, days: int = 30):
    cutoff_date = date.today() - timedelta(days=days)

    performance = db.query(models.ListingPerformance).filter(
        models.ListingPerformance.listing_id == listing_id,
        models.ListingPerformance.calculation_date >= cutoff_date
    ).order_by(models.ListingPerformance.calculation_date.desc()).all()

    return performance


def get_top_performing_listings(db: Session, limit: int = 10):
    today = date.today()

    return db.query(
        models.Listing,
        models.ListingPerformance
    ).join(
        models.ListingPerformance,
        models.Listing.listing_id == models.ListingPerformance.listing_id
    ).filter(
        models.ListingPerformance.calculation_date == today
    ).order_by(
        models.ListingPerformance.ctr.desc()
    ).limit(limit).all()


def get_daily_stats(db: Session, days: int = 30):
    cutoff_date = date.today() - timedelta(days=days)

    stats = db.query(
        models.ListingViewStatistics.view_date.label('date'),
        func.count(models.ListingViewStatistics.record_id).label('views'),
        func.count(func.distinct(models.ListingViewStatistics.user_id)).label('unique_visitors'),
        func.count(func.distinct(models.Listing.listing_id)).label('listings_added')
    ).outerjoin(
        models.Listing,
        func.date(models.Listing.publication_date) == models.ListingViewStatistics.view_date
    ).filter(
        models.ListingViewStatistics.view_date >= cutoff_date
    ).group_by(
        models.ListingViewStatistics.view_date
    ).order_by(
        models.ListingViewStatistics.view_date.desc()
    ).all()

    return stats


def get_price_analytics(db: Session, property_type_id: Optional[int] = None):
    query = db.query(
        models.PropertyType.name.label('property_type'),
        func.avg(models.Listing.price).label('avg_price'),
        func.min(models.Listing.price).label('min_price'),
        func.max(models.Listing.price).label('max_price'),
        func.percentile_cont(0.5).within_group(models.Listing.price).label('median_price'),
        func.count(models.Listing.listing_id).label('listings_count')
    ).join(
        models.PropertyType,
        models.Listing.property_type_id == models.PropertyType.property_type_id
    ).filter(
        models.Listing.listing_status_id == 1  # Active listings only
    )

    if property_type_id:
        query = query.filter(models.Listing.property_type_id == property_type_id)

    return query.group_by(models.PropertyType.name).all()


def get_user_activity_analytics(db: Session, days: int = 30):
    cutoff_date = date.today() - timedelta(days=days)

    activities = db.query(
        models.Users.user_id,
        models.Users.first_name,
        func.count(models.UserActivity.activity_id).label('total_sessions'),
        func.avg(models.UserActivity.session_duration_minutes).label('avg_session_duration'),
        func.sum(models.UserActivity.searches_count).label('total_searches'),
        func.sum(models.UserActivity.views_count).label('total_views'),
        func.max(models.UserActivity.activity_date).label('last_activity')
    ).join(
        models.UserActivity,
        models.Users.user_id == models.UserActivity.user_id
    ).filter(
        models.UserActivity.activity_date >= cutoff_date
    ).group_by(
        models.Users.user_id,
        models.Users.first_name
    ).order_by(
        func.count(models.UserActivity.activity_id).desc()
    ).limit(20).all()

    return activities


def get_search_analytics(db: Session, days: int = 30):
    cutoff_date = datetime.now() - timedelta(days=days)

    # Popular search queries
    popular_queries = db.query(
        models.SearchStatistics.search_query,
        func.count(models.SearchStatistics.record_id).label('count')
    ).filter(
        models.SearchStatistics.search_datetime >= cutoff_date,  # Изменено с search_date_time
        models.SearchStatistics.search_query.isnot(None)
    ).group_by(
        models.SearchStatistics.search_query
    ).order_by(
        func.count(models.SearchStatistics.record_id).desc()
    ).limit(20).all()

    # Average results count
    avg_results = db.query(
        func.avg(models.SearchStatistics.results_count)
    ).filter(
        models.SearchStatistics.search_datetime >= cutoff_date  # Изменено с search_date_time
    ).scalar() or 0

    # Average search time
    avg_time = db.query(
        func.avg(models.SearchStatistics.execution_time_seconds)
    ).filter(
        models.SearchStatistics.search_datetime >= cutoff_date  # Изменено с search_date_time
    ).scalar() or 0

    filters_usage = {
        "price_range": "common",
        "property_type": "common",
        "area": "less common"
    }

    return schemas.SearchAnalytics(
        popular_queries=[{"query": q, "count": c} for q, c in popular_queries],
        avg_results_count=float(avg_results),
        avg_search_time=float(avg_time),
        filters_usage=filters_usage
    )


def get_dashboard_summary(db: Session) -> schemas.DashboardSummary:
    today = date.today()

    # Total users
    total_users = db.query(models.Users).count()

    # Active listings (status_id = 1)
    active_listings = db.query(models.Listing).filter(
        models.Listing.listing_status_id == 1
    ).count()

    # Today's views
    today_views = db.query(models.ListingViewStatistics).filter(
        models.ListingViewStatistics.view_date == today
    ).count()

    # Today's conversions - ИСПРАВЛЕНО
    today_conversions = db.query(models.TargetConversions).filter(
        func.date(models.TargetConversions.event_datetime) == today  # Изменено с event_date_time
    ).count()

    # Total revenue (sold listings)
    total_revenue = db.query(func.sum(models.Listing.price)).filter(
        models.Listing.listing_status_id == 3
    ).scalar() or Decimal('0')

    # Recent activities - ИСПРАВЛЕНО
    recent_activities = db.query(models.ActionLog).order_by(
        models.ActionLog.action_datetime.desc()  # Изменено с action_date_time
    ).limit(10).all()

    # Top performing listings
    top_listings = []
    top_performing = get_top_performing_listings(db, limit=5)

    for listing, performance in top_performing:
        top_listings.append(schemas.ListingPerformanceSchema(
            listing_id=listing.listing_id,
            title=listing.title,
            total_views=performance.total_views,
            unique_views=performance.unique_views,
            contacts_opened=performance.contacts_opened,
            favorites_added=performance.favorites_added,
            ctr=float(performance.ctr) if performance.ctr else 0,
            conversion_rate=float(performance.call_conversion_rate) if performance.call_conversion_rate else 0,
            calculation_date=performance.calculation_date
        ))

    return schemas.DashboardSummary(
        total_users=total_users,
        active_listings=active_listings,
        today_views=today_views,
        today_conversions=today_conversions,
        total_revenue=total_revenue,
        recent_activities=[{"action": a.action, "time": a.action_datetime} for a in recent_activities],  # Изменено
        top_performing_listings=top_listings
    )

def get_total_listings(db: Session) -> int:
    """Общее количество объявлений"""
    return db.query(models.Listing).count()


def get_active_today(db: Session) -> int:
    """Активных объявлений сегодня"""
    today = date.today()
    return db.query(models.Listing).filter(
        models.Listing.publication_date >= today
    ).count()


def get_views_today(db: Session) -> int:
    """Просмотров сегодня"""
    today = date.today()
    return db.query(models.ListingViewStatistics).filter(
        models.ListingViewStatistics.view_date == today
    ).count()


def get_contacts_today(db: Session) -> int:
    """Запросов контактов сегодня"""
    today = date.today()
    return db.query(models.TargetConversions).filter(
        func.date(models.TargetConversions.event_datetime) == today,
        models.TargetConversions.conversion_type == 'contact'
    ).count()


def get_new_listings_today(db: Session) -> int:
    """Новых объявлений сегодня"""
    today = date.today()
    return db.query(models.Listing).filter(
        func.date(models.Listing.publication_date) == today
    ).count()


def get_popular_searches(db: Session, limit: int = 10) -> List[dict]:
    """Популярные поисковые запросы"""
    results = db.query(
        models.SearchStatistics.search_query,
        func.count(models.SearchStatistics.record_id).label('count')
    ).filter(
        models.SearchStatistics.search_query.isnot(None)
    ).group_by(
        models.SearchStatistics.search_query
    ).order_by(
        desc('count')
    ).limit(limit).all()

    return [{"query": r[0], "count": r[1]} for r in results]


def get_popular_listings(db: Session, period: str = "day", limit: int = 10):
    """Самые просматриваемые объявления за период"""
    if period == "day":
        date_from = date.today() - timedelta(days=1)
    elif period == "week":
        date_from = date.today() - timedelta(days=7)
    else:  # month
        date_from = date.today() - timedelta(days=30)

    results = db.query(
        models.Listing,
        func.count(models.ListingViewStatistics.record_id).label('views')
    ).join(
        models.ListingViewStatistics,
        models.Listing.listing_id == models.ListingViewStatistics.listing_id
    ).filter(
        models.ListingViewStatistics.view_date >= date_from
    ).group_by(
        models.Listing.listing_id
    ).order_by(
        desc('views')
    ).limit(limit).all()

    return [listing for listing, _ in results]


def get_average_prices(db: Session, city: str, property_type: Optional[str] = None):
    """Средние цены по городу"""
    query = db.query(
        func.avg(models.Listing.price).label('avg_price'),
        func.avg(models.Listing.price / models.Listing.total_area).label('avg_price_per_m2'),
        func.count(models.Listing.listing_id).label('count')
    ).filter(
        models.Listing.address.ilike(f'%{city}%')
    )

    if property_type:
        query = query.filter(models.Listing.property_type_id == property_type)

    result = query.first()
    return {
        "city": city,
        "avg_price": float(result.avg_price) if result.avg_price else 0,
        "avg_price_per_m2": float(result.avg_price_per_m2) if result.avg_price_per_m2 else 0,
        "listings_count": result.count
    }


def get_popular_metros(db: Session, city: str, limit: int = 10):
    """Популярные станции метро"""
    # Упрощенная версия - в реальности нужно парсить адрес
    results = db.query(
        models.Listing.metro,
        func.count(models.Listing.listing_id).label('count')
    ).filter(
        models.Listing.address.ilike(f'%{city}%'),
        models.Listing.metro.isnot(None)
    ).group_by(
        models.Listing.metro
    ).order_by(
        desc('count')
    ).limit(limit).all()

    return [{"metro": r[0], "count": r[1]} for r in results]


def get_market_stats(db: Session, city: str, property_type: Optional[str] = None):
    """Статистика рынка"""
    query = db.query(models.Listing).filter(
        models.Listing.address.ilike(f'%{city}%')
    )

    if property_type:
        query = query.filter(models.Listing.property_type_id == property_type)

    total = query.count()

    # Средняя цена за м²
    avg_price_per_m2 = db.query(
        func.avg(models.Listing.price / models.Listing.total_area)
    ).filter(
        models.Listing.address.ilike(f'%{city}%'),
        models.Listing.total_area > 0
    ).scalar() or 0

    # Изменение цены за месяц (упрощенно)
    last_month = date.today() - timedelta(days=30)
    prev_month = last_month - timedelta(days=30)

    current_avg = db.query(func.avg(models.Listing.price)).filter(
        models.Listing.address.ilike(f'%{city}%'),
        models.Listing.publication_date >= last_month
    ).scalar() or 0

    prev_avg = db.query(func.avg(models.Listing.price)).filter(
        models.Listing.address.ilike(f'%{city}%'),
        models.Listing.publication_date.between(prev_month, last_month)
    ).scalar() or 0

    price_change = ((current_avg - prev_avg) / prev_avg * 100) if prev_avg else 0

    # Популярные районы (упрощенно - первые слова из адреса)
    districts = db.query(
        models.Listing.address,
        func.count(models.Listing.listing_id).label('count')
    ).filter(
        models.Listing.address.ilike(f'%{city}%')
    ).group_by(
        models.Listing.address
    ).order_by(
        desc('count')
    ).limit(5).all()

    popular_districts = [{"name": d[0].split(',')[1] if ',' in d[0] else d[0], "count": d[1]} for d in districts]

    return {
        "total": total,
        "avg_price_per_m2": float(avg_price_per_m2),
        "price_change": float(price_change),
        "popular_districts": popular_districts
    }


def get_district_stats(db: Session, city: str, district: str):
    """Статистика по району"""
    address_filter = f'%{city}%{district}%'

    listings = db.query(models.Listing).filter(
        models.Listing.address.ilike(address_filter)
    ).all()

    if not listings:
        return {
            "district": district,
            "total_listings": 0,
            "avg_price": 0,
            "avg_price_per_m2": 0,
            "min_price": 0,
            "max_price": 0,
            "popular_property_types": []
        }

    prices = [float(l.price) for l in listings if l.price]
    areas = [float(l.total_area) for l in listings if l.total_area]

    price_per_m2 = []
    for l in listings:
        if l.price and l.total_area and l.total_area > 0:
            price_per_m2.append(float(l.price) / float(l.total_area))

    # Типы недвижимости
    from collections import Counter
    property_types = Counter([l.property_type_id for l in listings if l.property_type_id])

    return {
        "district": district,
        "total_listings": len(listings),
        "avg_price": sum(prices) / len(prices) if prices else 0,
        "avg_price_per_m2": sum(price_per_m2) / len(price_per_m2) if price_per_m2 else 0,
        "min_price": min(prices) if prices else 0,
        "max_price": max(prices) if prices else 0,
        "popular_property_types": [
            {"type_id": tid, "count": count}
            for tid, count in property_types.most_common(3)
        ]
    }


def get_price_trends(db: Session, city: str, property_type: str, months: int = 6):
    """Динамика цен за период"""
    trends = []
    today = date.today()

    for i in range(months):
        month_end = today - timedelta(days=30 * i)
        month_start = month_end - timedelta(days=30)

        avg_price = db.query(func.avg(models.Listing.price)).filter(
            models.Listing.address.ilike(f'%{city}%'),
            models.Listing.property_type_id == property_type,
            models.Listing.publication_date.between(month_start, month_end)
        ).scalar() or 0

        count = db.query(models.Listing).filter(
            models.Listing.address.ilike(f'%{city}%'),
            models.Listing.property_type_id == property_type,
            models.Listing.publication_date.between(month_start, month_end)
        ).count()

        trends.append({
            "month": month_start.strftime("%Y-%m"),
            "avg_price": float(avg_price),
            "listings_count": count,
            "change_percent": 0  # Можно добавить расчет позже
        })

    # Расчет изменений в процентах
    for i in range(len(trends) - 1):
        if trends[i + 1]["avg_price"] > 0:
            change = ((trends[i]["avg_price"] - trends[i + 1]["avg_price"]) /
                      trends[i + 1]["avg_price"] * 100)
            trends[i]["change_percent"] = round(change, 2)

    return list(reversed(trends))


# ============= ФУНКЦИИ ДЛЯ ИЗБРАННОГО =============

def get_user_favorites(db: Session, user_id: int):
    """Получить избранные объявления пользователя"""
    favorites = db.query(models.Favorite).filter(
        models.Favorite.user_id == user_id
    ).all()

    listings = []
    for fav in favorites:
        listing = db.query(models.Listing).filter(
            models.Listing.listing_id == fav.listing_id
        ).first()
        if listing:
            listings.append(listing)

    return listings


def add_favorite(db: Session, user_id: int, listing_id: int):
    """Добавить в избранное"""
    favorite = models.Favorite(
        user_id=user_id,
        listing_id=listing_id
    )
    db.add(favorite)
    db.commit()
    db.refresh(favorite)
    return favorite


def remove_favorite(db: Session, user_id: int, listing_id: int):
    """Удалить из избранного"""
    db.query(models.Favorite).filter(
        models.Favorite.user_id == user_id,
        models.Favorite.listing_id == listing_id
    ).delete()
    db.commit()


# ============= ФУНКЦИИ ДЛЯ ПОДПИСОК =============

def get_user_subscriptions(db: Session, user_id: int):
    """Подписки пользователя"""
    return db.query(models.SearchSubscription).filter(
        models.SearchSubscription.user_id == user_id,
        models.SearchSubscription.active == True
    ).all()


def create_subscription(db: Session, subscription: schemas.SubscriptionCreate):
    """Создать подписку"""
    db_sub = models.SearchSubscription(
        user_id=subscription.user_id,
        name=subscription.name,
        filter_parameters=subscription.filters.dict(),
        email_notifications=subscription.email_notifications
    )
    db.add(db_sub)
    db.commit()
    db.refresh(db_sub)
    return db_sub


def delete_subscription(db: Session, subscription_id: int):
    """Удалить подписку"""
    db.query(models.SearchSubscription).filter(
        models.SearchSubscription.subscription_id == subscription_id
    ).delete()
    db.commit()


# ============= ФУНКЦИИ ДЛЯ ПРОСМОТРОВ =============

def increment_listing_views(db: Session, listing_id: int):
    """Увеличить счетчик просмотров объявления"""
    listing = db.query(models.Listing).filter(
        models.Listing.listing_id == listing_id
    ).first()
    if listing:
        listing.views = (listing.views or 0) + 1
        db.commit()


def register_listing_view(db: Session, listing_id: int, user_id: Optional[int] = None):
    """Зарегистрировать просмотр"""
    view = models.ListingViewStatistics(
        listing_id=listing_id,
        user_id=user_id,
        view_date=date.today(),
        view_time=datetime.now().time()
    )
    db.add(view)
    db.commit()

    # Увеличиваем счетчик
    increment_listing_views(db, listing_id)


def log_contact_request(db: Session, listing_id: int):
    """Зарегистрировать запрос контактов"""
    conversion = models.TargetConversions(
        listing_id=listing_id,
        conversion_type='contact',
        event_datetime=datetime.now(),
        successful=True
    )
    db.add(conversion)
    db.commit()


# ============= ФУНКЦИИ ДЛЯ ПОИСКА =============

def search_listings(
        db: Session,
        skip: int = 0,
        limit: int = 20,
        deal_type: Optional[str] = None,
        property_type: Optional[str] = None,
        rooms: Optional[int] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        min_area: Optional[float] = None,
        max_area: Optional[float] = None,
        city: Optional[str] = None,
        district: Optional[str] = None,
        metro: Optional[str] = None,
        sort_by: str = "date_desc"
):
    """Поиск объявлений с фильтрацией"""
    query = db.query(models.Listing).filter(
        models.Listing.moderated == True  # Только проверенные
    )

    if deal_type:
        # Нужно связать с моделью DealType
        query = query.join(models.DealType).filter(models.DealType.name.ilike(f'%{deal_type}%'))

    if property_type:
        # Нужно связать с моделью PropertyType
        query = query.join(models.PropertyType).filter(models.PropertyType.name.ilike(f'%{property_type}%'))

    if rooms:
        # Это упрощенно - в реальности нужно парсить описание
        query = query.filter(models.Listing.title.ilike(f'%{rooms} комн%'))

    if min_price:
        query = query.filter(models.Listing.price >= min_price)
    if max_price:
        query = query.filter(models.Listing.price <= max_price)

    if min_area:
        query = query.filter(models.Listing.total_area >= min_area)
    if max_area:
        query = query.filter(models.Listing.total_area <= max_area)

    if city:
        query = query.filter(models.Listing.address.ilike(f'%{city}%'))
    if district:
        query = query.filter(models.Listing.address.ilike(f'%{district}%'))
    if metro:
        query = query.filter(models.Listing.address.ilike(f'%{metro}%'))

    # Сортировка
    if sort_by == "price_asc":
        query = query.order_by(models.Listing.price.asc())
    elif sort_by == "price_desc":
        query = query.order_by(models.Listing.price.desc())
    elif sort_by == "views_desc":
        query = query.order_by(models.Listing.views.desc())
    else:  # date_desc
        query = query.order_by(models.Listing.publication_date.desc())

    return query.offset(skip).limit(limit).all()

def get_active_listings(db: Session, skip: int = 0, limit: int = 50):
    """
    Получить только активные объявления (listing_status_id = 1)
    """
    return db.query(models.Listing).filter(
models.Listing.listing_status_id == 1,  # 1 = активное
        models.Listing.moderated == True        # только проверенные
    ).order_by(
        models.Listing.publication_date.desc()  # сначала новые
    ).offset(skip).limit(limit).all()


def get_similar_listings(db: Session, listing_id: int, limit: int = 5):
    """Похожие объявления"""
    listing = db.query(models.Listing).filter(
        models.Listing.listing_id == listing_id
    ).first()

    if not listing:
        return []

    # Ищем по тому же городу и похожей цене
    price_range = 0.3  # +-30%
    min_price = listing.price * (1 - price_range)
    max_price = listing.price * (1 + price_range)

    # Извлекаем город из адреса (упрощенно)
    city = listing.address.split(',')[0] if ',' in listing.address else listing.address

    similar = db.query(models.Listing).filter(
        models.Listing.listing_id != listing_id,
        models.Listing.address.ilike(f'%{city}%'),
        models.Listing.price.between(min_price, max_price),
        models.Listing.property_type_id == listing.property_type_id
    ).order_by(
        models.Listing.publication_date.desc()
    ).limit(limit).all()

    return similar


def update_photo(db: Session, photo_id: int, photo_update: dict):
    """Обновить фото"""
    db_photo = db.query(models.Photo).filter(models.Photo.photo_id == photo_id).first()
    if db_photo:
        for key, value in photo_update.items():
            setattr(db_photo, key, value)
        db.commit()
        db.refresh(db_photo)
    return db_photo

def delete_photo(db: Session, photo_id: int):
    """Удалить фото"""
    db_photo = db.query(models.Photo).filter(models.Photo.photo_id == photo_id).first()
    if db_photo:
        db.delete(db_photo)
        db.commit()
        return True
    return False

def get_listing_with_photos(db: Session, listing_id: int):
    """Получить объявление со всеми фотографиями"""
    listing = db.query(models.Listing).filter(
        models.Listing.listing_id == listing_id,
        models.Listing.listing_status_id == 1,
        models.Listing.moderated == True
    ).first()

    if not listing:
        return None
