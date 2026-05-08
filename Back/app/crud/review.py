from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from app.crud.base import CRUDBase
from app.models import Review


class CRUDReview(CRUDBase[Review]):

    def get_by_author(self, db: Session, author_id: int) -> List[Review]:
        """Отзывы, которые оставил пользователь (автор)"""
        return (
            db.query(Review)
            .filter(Review.author_id == author_id)
            .order_by(desc(Review.created_date))
            .all()
        )

    def get_by_user(self, db: Session, user_id: int) -> List[Review]:
        """Отзывы о пользователе (получатель)"""
        return (
            db.query(Review)
            .filter(Review.user_id == user_id)
            .order_by(desc(Review.created_date))
            .all()
        )

    def get_by_listing(self, db: Session, listing_id: int) -> List[Review]:
        """Отзывы об объявлении"""
        return (
            db.query(Review)
            .filter(Review.listing_id == listing_id)
            .order_by(desc(Review.created_date))
            .all()
        )

    def get_by_author_and_listing(
            self,
            db: Session,
            author_id: int,
            listing_id: int
    ) -> Optional[Review]:
        """Конкретный отзыв автора на объявление"""
        return (
            db.query(Review)
            .filter(
                Review.author_id == author_id,
                Review.listing_id == listing_id
            )
            .first()
        )

    def count_by_user(self, db: Session, user_id: int) -> int:
        """Количество отзывов о пользователе"""
        return (
            db.query(Review)
            .filter(Review.user_id == user_id)
            .count()
        )

    def count_by_listing(self, db: Session, listing_id: int) -> int:
        """Количество отзывов об объявлении"""
        return (
            db.query(Review)
            .filter(Review.listing_id == listing_id)
            .count()
        )


review_crud = CRUDReview(Review)