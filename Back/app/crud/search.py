from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from app.crud.base import CRUDBase
from app.models import SearchHistory, SearchRequest


class CRUDSearchHistory(CRUDBase[SearchHistory]):

    def get_by_user(
            self,
            db: Session,
            user_id: int,
            skip: int = 0,
            limit: int = 50
    ) -> List[SearchHistory]:
        return (
            db.query(SearchHistory)
            .filter(SearchHistory.user_id == user_id)
            .order_by(desc(SearchHistory.search_date))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def clear(self, db: Session, user_id: int) -> int:
        deleted = (
            db.query(SearchHistory)
            .filter(SearchHistory.user_id == user_id)
            .delete()
        )
        db.commit()
        return deleted


class CRUDSearchRequest(CRUDBase[SearchRequest]):

    def get_by_user(
            self,
            db: Session,
            user_id: int,
            skip: int = 0,
            limit: int = 50
    ) -> List[SearchRequest]:
        return (
            db.query(SearchRequest)
            .filter(SearchRequest.user_id == user_id)
            .order_by(desc(SearchRequest.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_agent(
            self,
            db: Session,
            agent_id: int,
            skip: int = 0,
            limit: int = 50
    ) -> List[SearchRequest]:
        return (
            db.query(SearchRequest)
            .filter(SearchRequest.agent_id == agent_id)
            .order_by(desc(SearchRequest.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )


search_history_crud = CRUDSearchHistory(SearchHistory)
search_request_crud = CRUDSearchRequest(SearchRequest)