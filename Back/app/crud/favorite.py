from sqlalchemy.orm import Session
from typing import List, Optional
from app.crud.base import CRUDBase
from app.models import Favorite
from app.schemas.favorite import FavoriteCreate


class CRUDFavorite(CRUDBase[Favorite]):  # ← только 1 параметр
    def get_by_user(self, db: Session, user_id: int) -> List[Favorite]:
        return db.query(Favorite).filter(Favorite.user_id == user_id).all()

    def get_by_user_and_listing(
            self,
            db: Session,
            user_id: int,
            listing_id: int
    ) -> Optional[Favorite]:
        return db.query(Favorite).filter(
            Favorite.user_id == user_id,
            Favorite.listing_id == listing_id
        ).first()

    def delete_by_user_and_listing(
            self,
            db: Session,
            user_id: int,
            listing_id: int
    ) -> bool:
        favorite = self.get_by_user_and_listing(db, user_id, listing_id)
        if favorite:
            db.delete(favorite)
            db.commit()
            return True
        return False


favorite_crud = CRUDFavorite(Favorite)