from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
from app.crud.base import CRUDBase
from app.models import Comment


class CRUDComment(CRUDBase[Comment]):

    def get_by_profile(self, db: Session, profile_user_id: int) -> List[Comment]:
        return (
            db.query(Comment)
            .filter(Comment.profile_user_id == profile_user_id)
            .order_by(desc(Comment.created_date))
            .all()
        )

    def get_by_author(self, db: Session, author_id: int) -> List[Comment]:
        return (
            db.query(Comment)
            .filter(Comment.author_id == author_id)
            .order_by(desc(Comment.created_date))
            .all()
        )

    def count_by_profile(self, db: Session, profile_user_id: int) -> int:
        return (
            db.query(Comment)
            .filter(Comment.profile_user_id == profile_user_id)
            .count()
        )


comment_crud = CRUDComment(Comment)