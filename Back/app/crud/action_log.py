from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from app.crud.base import CRUDBase
from app.models import ActionLog


class CRUDActionLog(CRUDBase[ActionLog]):

    def get_by_user(self, db: Session, user_id: int, skip: int = 0, limit: int = 50) -> List[ActionLog]:
        return db.query(ActionLog).filter(ActionLog.user_id == user_id).order_by(
            desc(ActionLog.action_datetime)).offset(skip).limit(limit).all()

    def get_by_listing(self, db: Session, listing_id: int) -> List[ActionLog]:
        return db.query(ActionLog).filter(ActionLog.listing_id == listing_id).order_by(
            desc(ActionLog.action_datetime)).all()

    def log(self, db: Session, user_id: int, action_type_id: int, listing_id: Optional[int] = None,
            ip_address: Optional[str] = None, user_agent: Optional[str] = None,
            details: Optional[dict] = None) -> ActionLog:
        log = ActionLog(
            user_id=user_id,
            action_type_id=action_type_id,
            listing_id=listing_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log


action_log_crud = CRUDActionLog(ActionLog)