from sqlalchemy.orm import Session
from typing import List
from app.crud.base import CRUDBase
from app.models import Review
from app.schemas.review import ReviewCreate


class CRUDReview(CRUDBase[Review]):  # ← только 1 параметр
    def get_by_user(self, db: Session, user_id: int) -> List[Review]:
        return db.query(Review).filter(Review.user_id == user_id).all()

    def get_by_listing(self, db: Session, listing_id: int) -> List[Review]:
        return db.query(Review).filter(Review.listing_id == listing_id).all()

    def update_user_rating(self, db: Session, user_id: int) -> None:
        from app.crud.user import user_crud

        reviews = self.get_by_user(db, user_id)
        if reviews:
            avg_rating = sum(r.rating for r in reviews) / len(reviews)
            user = user_crud.get(db, user_id)
            if user:
                user.rating = avg_rating
                user.reviews_count = len(reviews)
                db.commit()


review_crud = CRUDReview(Review)