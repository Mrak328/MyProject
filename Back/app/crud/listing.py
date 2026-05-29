from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc, or_
from typing import Optional, List
from datetime import date, datetime
from app.crud.base import CRUDBase
from app.models import Listing, ListingViewStatistics, Address, City, Street
from app.schemas.listing import ListingCreate, ListingUpdate


class CRUDListing(CRUDBase[Listing]):
    ACTIVE_STATUS_ID = 1

    def get_active(
            self,
            db: Session,
            skip: int = 0,
            limit: int = 100
    ) -> List[Listing]:
        return (
            db.query(Listing)
            .filter(
                Listing.listing_status_id == self.ACTIVE_STATUS_ID,
                Listing.moderated == True
            )
            .order_by(Listing.publication_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

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
            deal_type_id: Optional[int] = None,
            property_type_id: Optional[int] = None,
            market_type_id: Optional[int] = None,
            renovation_condition_id: Optional[int] = None,
            floor: Optional[int] = None
    ) -> List[Listing]:
        query = (
            db.query(Listing)
            .filter(
                Listing.listing_status_id == self.ACTIVE_STATUS_ID,
                Listing.moderated == True
            )
        )

        # Поиск по городу через JOIN с географией
        if city:
            query = (
                query
                .join(Address, Listing.address_id == Address.address_id)
                .join(City, Address.city_id == City.city_id)
                .filter(City.name.ilike(f"%{city}%"))
            )

        # Поиск по улице
        # if street:
        #     query = (
        #         query
        #         .join(Address, Listing.address_id == Address.address_id)
        #         .join(Street, Address.street_id == Street.street_id)
        #         .filter(Street.name.ilike(f"%{street}%"))
        #     )

        if min_price is not None:
            query = query.filter(Listing.price >= min_price)
        if max_price is not None:
            query = query.filter(Listing.price <= max_price)
        if min_area is not None:
            query = query.filter(Listing.total_area >= min_area)
        if max_area is not None:
            query = query.filter(Listing.total_area <= max_area)
        if rooms is not None:
            query = query.filter(Listing.rooms == rooms)
        if deal_type_id is not None:
            query = query.filter(Listing.deal_type_id == deal_type_id)
        if property_type_id is not None:
            query = query.filter(Listing.property_type_id == property_type_id)
        if market_type_id is not None:
            query = query.filter(Listing.market_type_id == market_type_id)
        if renovation_condition_id is not None:
            query = query.filter(Listing.renovation_condition_id == renovation_condition_id)
        if floor is not None:
            query = query.filter(Listing.floor == floor)

        return (
            query
            .order_by(Listing.publication_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def increment_views(self, db: Session, listing_id: int) -> bool:
        """Увеличить счётчик просмотров на 1"""
        updated = (
            db.query(Listing)
            .filter(Listing.listing_id == listing_id)
            .update(
                {Listing.views: Listing.views + 1},
                synchronize_session=False
            )
        )
        db.commit()
        return updated > 0

    def register_view(
            self,
            db: Session,
            listing_id: int,
            user_id: Optional[int] = None,
            ip_address: Optional[str] = None,
            device_type_id: Optional[int] = None,
            browser_type_id: Optional[int] = None,
            source_type_id: Optional[int] = None,
            view_depth_seconds: int = 0,
            contacts_opened: bool = False
    ) -> Optional[ListingViewStatistics]:
        """Зарегистрировать просмотр объявления"""
        try:
            view = ListingViewStatistics(
                listing_id=listing_id,
                user_id=user_id,
                view_date=date.today(),
                view_time=datetime.now().time(),
                ip_address=ip_address,
                device_type_id=device_type_id,
                browser_type_id=browser_type_id,
                source_type_id=source_type_id,
                view_depth_seconds=view_depth_seconds,
                contacts_opened=contacts_opened
            )
            db.add(view)
            db.commit()
            db.refresh(view)
            return view
        except Exception:
            db.rollback()
            return None

    def create(self, db: Session, obj_in: ListingCreate, user_id: int) -> Listing:
        data = obj_in.dict(exclude={
            'address_id', 'country_id', 'region_id', 'city_id',
            'district_id', 'street_id', 'house_id', 'apartment_id',
            'listing_status_id'
        })

        db_obj = Listing(
            user_id=user_id,
            listing_status_id=1,
            moderated=False,
            **data
        )

        if obj_in.address_id:
            db_obj.address_id = obj_in.address_id

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_user(
            self,
            db: Session,
            user_id: int,
            skip: int = 0,
            limit: int = 50
    ) -> List[Listing]:
        """Все объявления пользователя"""
        return (
            db.query(Listing)
            .filter(Listing.user_id == user_id)
            .order_by(Listing.publication_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_user_count(self, db: Session, user_id: int) -> int:
        """Количество объявлений пользователя"""
        return (
            db.query(Listing)
            .filter(Listing.user_id == user_id)
            .count()
        )

    def update_status(
            self,
            db: Session,
            listing_id: int,
            status_id: int
    ) -> Optional[Listing]:
        """Быстрая смена статуса"""
        listing = self.get(db, listing_id)
        if listing:
            listing.listing_status_id = status_id
            listing.update_date = datetime.now()
            db.commit()
            db.refresh(listing)
        return listing


listing_crud = CRUDListing(Listing)