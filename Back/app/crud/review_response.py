from sqlalchemy.orm import Session
from typing import List
from app.crud.base import CRUDBase
from app.models import ReviewResponse


class CRUDReviewResponse(CRUDBase[ReviewResponse]):

    def get_by_review(self, db: Session, review_id: int) -> List[ReviewResponse]:
        return (
            db.query(ReviewResponse)
            .filter(ReviewResponse.review_id == review_id)
            .order_by(ReviewResponse.response_date)
            .all()
        )


review_response_crud = CRUDReviewResponse(ReviewResponse)