from sqlalchemy.orm import Session
from sqlalchemy import desc, exc
from typing import List, Optional
from app.models import Favorite, Listing


class CRUDFavorite:

    def add(self, db: Session, user_id: int, listing_id: int) -> Optional[Favorite]:
        """Добавить в избранное. Если уже есть — вернуть существующий"""
        existing = self.get_by_user_and_listing(db, user_id, listing_id)
        if existing:
            return existing

        favorite = Favorite(user_id=user_id, listing_id=listing_id)
        db.add(favorite)
        try:
            db.commit()
            db.refresh(favorite)
            return favorite
        except exc.IntegrityError:
            db.rollback()
            return self.get_by_user_and_listing(db, user_id, listing_id)

    def remove(self, db: Session, user_id: int, listing_id: int) -> bool:
        """Удалить из избранного. Возвращает True если удалено"""
        deleted = (
            db.query(Favorite)
            .filter(
                Favorite.user_id == user_id,
                Favorite.listing_id == listing_id
            )
            .delete()
        )
        db.commit()
        return deleted > 0

    def get_by_user(
            self,
            db: Session,
            user_id: int,
            skip: int = 0,
            limit: int = 50
    ) -> List[Favorite]:
        """Все избранные пользователя"""
        return (
            db.query(Favorite)
            .filter(Favorite.user_id == user_id)
            .order_by(desc(Favorite.added_date))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_user_and_listing(
            self,
            db: Session,
            user_id: int,
            listing_id: int
    ) -> Optional[Favorite]:
        """Конкретная запись избранного"""
        return (
            db.query(Favorite)
            .filter(
                Favorite.user_id == user_id,
                Favorite.listing_id == listing_id
            )
            .first()
        )

    def is_favorite(self, db: Session, user_id: int, listing_id: int) -> bool:
        """Проверить, в избранном ли объявление"""
        return self.get_by_user_and_listing(db, user_id, listing_id) is not None

    def count(self, db: Session, listing_id: int) -> int:
        """Сколько раз объявление добавлено в избранное"""
        return (
            db.query(Favorite)
            .filter(Favorite.listing_id == listing_id)
            .count()
        )

    def toggle(self, db: Session, user_id: int, listing_id: int) -> dict:
        """Переключить избранное: добавить/удалить. Возвращает статус"""
        if self.is_favorite(db, user_id, listing_id):
            self.remove(db, user_id, listing_id)
            return {"status": "removed", "listing_id": listing_id}
        else:
            self.add(db, user_id, listing_id)
            return {"status": "added", "listing_id": listing_id}


favorite_crud = CRUDFavorite()