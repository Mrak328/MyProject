from sqlalchemy.orm import Session
from typing import List
from app.crud.base import CRUDBase
from app.models import Photo
from app.schemas.photo import PhotoCreate


class CRUDPhoto(CRUDBase[Photo]):  # ← только 1 параметр
    def get_by_listing(self, db: Session, listing_id: int) -> List[Photo]:
        return db.query(Photo).filter(
            Photo.listing_id == listing_id
        ).order_by(Photo.photo_id).all()

    def delete_by_listing(self, db: Session, listing_id: int) -> int:
        deleted = db.query(Photo).filter(Photo.listing_id == listing_id).delete()
        db.commit()
        return deleted


photo_crud = CRUDPhoto(Photo)