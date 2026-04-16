from sqlalchemy.orm import Session
from app.models import Favorite


class CRUDFavorite:
    def add_favorite(self, db: Session, user_id: int, listing_id: int):
        favorite = Favorite(user_id=user_id, listing_id=listing_id)
        db.add(favorite)
        db.commit()
        db.refresh(favorite)
        return favorite

    def remove_favorite(self, db: Session, user_id: int, listing_id: int):
        db.query(Favorite).filter(
            Favorite.user_id == user_id,
            Favorite.listing_id == listing_id
        ).delete()
        db.commit()

    def get_user_favorites(self, db: Session, user_id: int):
        return db.query(Favorite).filter(Favorite.user_id == user_id).all()

    def is_favorite(self, db: Session, user_id: int, listing_id: int):
        return db.query(Favorite).filter(
            Favorite.user_id == user_id,
            Favorite.listing_id == listing_id
        ).first() is not None


favorite_crud = CRUDFavorite()