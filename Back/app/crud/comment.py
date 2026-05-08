from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
from app.crud.base import CRUDBase
from app.models import Comment

class CRUDComment(CRUDBase[Comment]):
    def get_by_review(self, db: Session, review_id: int) -> List[Comment]:
        return db.query(Comment).filter(Comment.review_id == review_id).order_by(Comment.created_date).all()

    def count_by_review(self, db: Session, review_id: int) -> int:
        return db.query(Comment).filter(Comment.review_id == review_id).count()

comment_crud = CRUDComment(Comment)