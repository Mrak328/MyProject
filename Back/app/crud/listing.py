from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional, List
from datetime import date, datetime
from app.crud.base import CRUDBase
from app.models import Listing, ListingViewStatistics
from app.schemas.listing import ListingCreate, ListingUpdate


class CRUDListing(CRUDBase[Listing]):
    def get_active(
            self,
            db: Session,
            skip: int = 0,
            limit: int = 100
    ) -> List[Listing]:
        return db.query(Listing).filter(
            Listing.listing_status_id == 1,
            Listing.moderated == True
        ).order_by(
            Listing.publication_date.desc()
        ).offset(skip).limit(limit).all()

    def search(
            self,
            db: Session,
            skip: int = 0,
            limit: int = 50,
            city: Optional[str] = None,
            min_price: Optional[float] = None,
            max_price: Optional[float] = None,
            min_area: Optional[float] = None,
            max_area: Optional[float] = None,
            rooms: Optional[int] = None,
            deal_type: Optional[int] = None,
            property_type: Optional[int] = None
    ) -> List[Listing]:
        query = db.query(Listing).filter(
            Listing.listing_status_id == 1,
            Listing.moderated == True
        )

        if city:
            query = query.filter(Listing.address.ilike(f'%{city}%'))
        if min_price:
            query = query.filter(Listing.price >= min_price)
        if max_price:
            query = query.filter(Listing.price <= max_price)
        if min_area:
            query = query.filter(Listing.total_area >= min_area)
        if max_area:
            query = query.filter(Listing.total_area <= max_area)
        if rooms:
            query = query.filter(Listing.rooms == rooms)
        if deal_type:
            query = query.filter(Listing.deal_type_id == deal_type)
        if property_type:
            query = query.filter(Listing.property_type_id == property_type)

        return query.order_by(Listing.publication_date.desc()).offset(skip).limit(limit).all()

    def increment_views(self, db: Session, listing_id: int) -> None:
        listing = self.get(db, listing_id)
        if listing:
            listing.views = (listing.views or 0) + 1
            db.commit()

    def register_listing_view(
            self,
            db: Session,
            listing_id: int,
            user_id: Optional[int] = None,
            ip_address: str = "unknown",
            device: str = "Desktop",
            browser: str = "Unknown"
    ):
        """Зарегистрировать просмотр объявления"""
        try:
            view = ListingViewStatistics(
                listing_id=listing_id,
                user_id=user_id,
                view_date=date.today(),
                view_time=datetime.now().time(),
                ip_address=ip_address,
                device=device,
                browser=browser,
                referrer_source="Direct",
                view_depth_seconds=0,
                contacts_opened=False
            )
            db.add(view)
            db.commit()
            db.refresh(view)
            print(f"✅ Просмотр зарегистрирован: listing_id={listing_id}, user_id={user_id}")
            return view
        except Exception as e:
            print(f"❌ Ошибка регистрации просмотра: {e}")
            db.rollback()
            return None


listing_crud = CRUDListing(Listing)