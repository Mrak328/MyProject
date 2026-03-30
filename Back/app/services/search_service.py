from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional, List
from app.models import Listing
from app.models import PropertyType, DealType  # ← правильный импорт


class SearchService:
    """Сервис для поиска и фильтрации объявлений"""

    @staticmethod
    def search(
            db: Session,
            query: Optional[str] = None,
            city: Optional[str] = None,
            min_price: Optional[float] = None,
            max_price: Optional[float] = None,
            min_area: Optional[float] = None,
            max_area: Optional[float] = None,
            rooms: Optional[int] = None,
            deal_type_id: Optional[int] = None,
            property_type_id: Optional[int] = None,
            sort_by: str = "date_desc",
            skip: int = 0,
            limit: int = 20
    ) -> List[Listing]:
        """Расширенный поиск объявлений"""
        q = db.query(Listing).filter(
            Listing.listing_status_id == 1,
            Listing.moderated == True
        )

        # Поиск по тексту (заголовок, описание, адрес)
        if query:
            q = q.filter(
                or_(
                    Listing.title.ilike(f"%{query}%"),
                    Listing.description.ilike(f"%{query}%"),
                    Listing.address.ilike(f"%{query}%")
                )
            )

        # Фильтр по городу
        if city:
            q = q.filter(Listing.address.ilike(f"%{city}%"))

        # Фильтр по цене
        if min_price:
            q = q.filter(Listing.price >= min_price)
        if max_price:
            q = q.filter(Listing.price <= max_price)

        # Фильтр по площади
        if min_area:
            q = q.filter(Listing.total_area >= min_area)
        if max_area:
            q = q.filter(Listing.total_area <= max_area)

        # Фильтр по комнатам
        if rooms:
            q = q.filter(Listing.rooms == rooms)

        # Фильтр по типу сделки
        if deal_type_id:
            q = q.filter(Listing.deal_type_id == deal_type_id)

        # Фильтр по типу недвижимости
        if property_type_id:
            q = q.filter(Listing.property_type_id == property_type_id)

        # Сортировка
        if sort_by == "price_asc":
            q = q.order_by(Listing.price.asc())
        elif sort_by == "price_desc":
            q = q.order_by(Listing.price.desc())
        elif sort_by == "views_desc":
            q = q.order_by(Listing.views.desc())
        else:  # date_desc
            q = q.order_by(Listing.created_at.desc())

        return q.offset(skip).limit(limit).all()

    @staticmethod
    def get_similar_listings(
            db: Session,
            listing_id: int,
            limit: int = 5
    ) -> List[Listing]:
        """Поиск похожих объявлений"""
        listing = db.get(Listing, listing_id)
        if not listing:
            return []

        # Извлекаем город из адреса (первые слова)
        city = listing.address.split(",")[0] if listing.address else ""
        price_range = 0.3  # ±30%

        similar = db.query(Listing).filter(
            Listing.id != listing_id,
            Listing.listing_status_id == 1,
            Listing.moderated == True,
            Listing.address.ilike(f"%{city}%"),
            Listing.property_type_id == listing.property_type_id,
            Listing.price.between(
                listing.price * (1 - price_range),
                listing.price * (1 + price_range)
            )
        ).order_by(
            Listing.created_at.desc()
        ).limit(limit).all()

        return similar


search_service = SearchService()