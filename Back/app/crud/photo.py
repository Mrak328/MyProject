from sqlalchemy.orm import Session
from typing import List, Optional
from app.crud.base import CRUDBase
from app.models import Photo


class CRUDPhoto(CRUDBase[Photo]):

    def get_by_listing(
            self,
            db: Session,
            listing_id: int
    ) -> List[Photo]:
        return (
            db.query(Photo)
            .filter(Photo.listing_id == listing_id)
            .order_by(Photo.photo_id)
            .all()
        )

    def get_first_by_listing(
            self,
            db: Session,
            listing_id: int
    ) -> Optional[Photo]:
        """Первое фото объявления (для превью)"""
        return (
            db.query(Photo)
            .filter(Photo.listing_id == listing_id)
            .order_by(Photo.photo_id)
            .first()
        )

    def delete_by_listing(self, db: Session, listing_id: int) -> int:
        deleted = (
            db.query(Photo)
            .filter(Photo.listing_id == listing_id)
            .delete()
        )
        db.commit()
        return deleted

    def create_bulk(
            self,
            db: Session,
            listing_id: int,
            photo_urls: List[str]
    ) -> List[Photo]:
        """Массовое добавление фото"""
        photos = [
            Photo(listing_id=listing_id, file_url=url)
            for url in photo_urls
        ]
        db.add_all(photos)
        db.commit()
        for p in photos:
            db.refresh(p)
        return photos


photo_crud = CRUDPhoto(Photo)