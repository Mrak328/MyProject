from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import date, timedelta
from typing import List, Dict, Any
from app.models import Listing, Photo, ListingViewStatistics, SearchStatistics, PropertyType


class CRUDAnalytics:
    def get_dashboard_stats(self, db: Session) -> Dict[str, Any]:
        today = date.today()

        total_listings = db.query(Listing).count()

        # Используем publication_date вместо created_at
        active_today = db.query(Listing).filter(
            Listing.listing_status_id == 1,
            func.date(Listing.publication_date) == today
        ).count()

        views_today = db.query(ListingViewStatistics).filter(
            ListingViewStatistics.view_date == today
        ).count()

        new_today = db.query(Listing).filter(
            func.date(Listing.publication_date) == today
        ).count()

        return {
            "total_listings": total_listings,
            "active_today": active_today,
            "views_today": views_today,
            "new_listings_today": new_today
        }

    def get_popular_listings(
            self,
            db: Session,
            period: str = "week",
            limit: int = 10
    ) -> List[Dict]:
        today = date.today()

        if period == "day":
            start = today - timedelta(days=1)
        elif period == "week":
            start = today - timedelta(days=7)
        else:
            start = today - timedelta(days=30)

        # Используем listing_id вместо id
        results = db.query(
            Listing,
            func.count(ListingViewStatistics.record_id).label('view_count')
        ).outerjoin(
            ListingViewStatistics,
            Listing.listing_id == ListingViewStatistics.listing_id
        ).filter(
            Listing.listing_status_id == 1,
            ListingViewStatistics.view_date >= start
        ).group_by(
            Listing.listing_id
        ).order_by(
            desc('view_count')
        ).limit(limit).all()

        popular = []
        for listing, view_count in results:
            photo = db.query(Photo).filter(Photo.listing_id == listing.listing_id).first()
            popular.append({
                "listing_id": listing.listing_id,
                "title": listing.title,
                "price": float(listing.price) if listing.price else 0,
                "address": listing.address,
                "views": view_count,
                "photo": photo.file_url if photo else None
            })

        return popular

    def get_price_stats(self, db: Session) -> Dict[str, Any]:
        active_listings = db.query(Listing).filter(
            Listing.listing_status_id == 1,
            Listing.price.isnot(None)
        ).all()

        if not active_listings:
            return {
                "total_active": 0,
                "avg_price": 0,
                "avg_price_per_m2": 0,
                "min_price": 0,
                "max_price": 0,
                "price_ranges": {},
                "by_type": []
            }

        prices = [float(l.price) for l in active_listings]

        # Цена за м²
        prices_per_m2 = []
        for l in active_listings:
            if l.price and l.total_area and l.total_area > 0:
                prices_per_m2.append(float(l.price) / float(l.total_area))

        # Ценовые диапазоны
        ranges = {"до 2 млн": 0, "2-4 млн": 0, "4-6 млн": 0,
                  "6-10 млн": 0, "10-15 млн": 0, "более 15 млн": 0}

        for p in prices:
            if p < 2_000_000:
                ranges["до 2 млн"] += 1
            elif p < 4_000_000:
                ranges["2-4 млн"] += 1
            elif p < 6_000_000:
                ranges["4-6 млн"] += 1
            elif p < 10_000_000:
                ranges["6-10 млн"] += 1
            elif p < 15_000_000:
                ranges["10-15 млн"] += 1
            else:
                ranges["более 15 млн"] += 1

        return {
            "total_active": len(active_listings),
            "avg_price": sum(prices) / len(prices) if prices else 0,
            "avg_price_per_m2": sum(prices_per_m2) / len(prices_per_m2) if prices_per_m2 else 0,
            "min_price": min(prices) if prices else 0,
            "max_price": max(prices) if prices else 0,
            "price_ranges": ranges,
            "by_type": []
        }

    def get_views_stats(self, db: Session, period: str) -> Dict[str, Any]:
        today = date.today()

        if period == "day":
            start = today - timedelta(days=1)
        elif period == "week":
            start = today - timedelta(days=7)
        else:
            start = today - timedelta(days=30)

        total_views = db.query(ListingViewStatistics).filter(
            ListingViewStatistics.view_date >= start
        ).count()

        unique_listings = db.query(ListingViewStatistics.listing_id).distinct().filter(
            ListingViewStatistics.view_date >= start
        ).count()

        unique_visitors = db.query(ListingViewStatistics.user_id).distinct().filter(
            ListingViewStatistics.view_date >= start,
            ListingViewStatistics.user_id.isnot(None)
        ).count()

        views_by_day = db.query(
            func.date(ListingViewStatistics.view_date).label('date'),
            func.count(ListingViewStatistics.record_id).label('count')
        ).filter(
            ListingViewStatistics.view_date >= start
        ).group_by(
            func.date(ListingViewStatistics.view_date)
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

    def get_search_queries(self, db: Session, days: int) -> Dict[str, Any]:
        from datetime import datetime
        start = datetime.now() - timedelta(days=days)

        popular = db.query(
            SearchStatistics.search_query,
            func.count(SearchStatistics.record_id).label('count')
        ).filter(
            SearchStatistics.search_datetime >= start,
            SearchStatistics.search_query.isnot(None)
        ).group_by(
            SearchStatistics.search_query
        ).order_by(
            desc('count')
        ).limit(20).all()

        total_searches = db.query(SearchStatistics).filter(
            SearchStatistics.search_datetime >= start
        ).count()

        return {
            "total_searches": total_searches,
            "popular_queries": [
                {"query": q[0] or "пустой запрос", "count": q[1]}
                for q in popular
            ]
        }

    def get_closed_deals(self, db: Session, period: str) -> Dict[str, Any]:
        today = date.today()

        if period == "week":
            start = today - timedelta(days=7)
        elif period == "month":
            start = today - timedelta(days=30)
        else:
            start = today - timedelta(days=365)

        closed = db.query(Listing).filter(
            Listing.listing_status_id == 3,
            Listing.moderation_date >= start
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

        return {
            "period": period,
            "total_closed": len(closed),
            "total_revenue": total_revenue,
            "avg_days_to_sell": round(avg_days, 1),
            "by_type": []
        }


analytics_crud = CRUDAnalytics()