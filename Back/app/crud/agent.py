from sqlalchemy.orm import Session
from typing import Optional, List
from app.crud.base import CRUDBase
from app.models import AgentProfile


class CRUDAgent(CRUDBase[AgentProfile]):

    def get_by_user(self, db: Session, user_id: int) -> Optional[AgentProfile]:
        return (
            db.query(AgentProfile)
            .filter(AgentProfile.user_id == user_id)
            .first()
        )

    def get_active_agents(
            self,
            db: Session,
            skip: int = 0,
            limit: int = 50
    ) -> List[AgentProfile]:
        """Агенты, у которых есть активные объявления (через user.listing)"""
        from app.models import Listing
        return (
            db.query(AgentProfile)
            .join(Listing, Listing.user_id == AgentProfile.user_id)
            .filter(Listing.listing_status_id == 1)
            .distinct()
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_company(self, db: Session, company_name: str) -> List[AgentProfile]:
        """Поиск по названию компании"""
        return (
            db.query(AgentProfile)
            .filter(AgentProfile.company_name.ilike(f"%{company_name}%"))
            .all()
        )


agent_crud = CRUDAgent(AgentProfile)