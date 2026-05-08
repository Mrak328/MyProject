from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime
from app.crud.base import CRUDBase
from app.models import BlocksAndViolations


class CRUDBlock(CRUDBase[BlocksAndViolations]):

    def get_by_user(
            self,
            db: Session,
            user_id: int,
            only_active: bool = False
    ) -> List[BlocksAndViolations]:
        query = db.query(BlocksAndViolations).filter(
            BlocksAndViolations.user_id == user_id
        )
        if only_active:
            query = query.filter(BlocksAndViolations.block_status_id == 1)
        return query.order_by(desc(BlocksAndViolations.block_date)).all()

    def get_by_listing(self, db: Session, listing_id: int) -> List[BlocksAndViolations]:
        return (
            db.query(BlocksAndViolations)
            .filter(BlocksAndViolations.listing_id == listing_id)
            .order_by(desc(BlocksAndViolations.block_date))
            .all()
        )

    def is_blocked(self, db: Session, user_id: int) -> bool:
        """Активна ли блокировка у пользователя"""
        return (
                db.query(BlocksAndViolations)
                .filter(
                    BlocksAndViolations.user_id == user_id,
                    BlocksAndViolations.block_status_id == 1,
                    BlocksAndViolations.unblock_date.is_(None) |
                    (BlocksAndViolations.unblock_date > datetime.now())
                )
                .first() is not None
        )

    def unblock(self, db: Session, block_id: int) -> Optional[BlocksAndViolations]:
        """Разблокировать"""
        block = self.get(db, block_id)
        if block:
            block.block_status_id = 2  # неактивен
            block.unblock_date = datetime.now()
            db.commit()
            db.refresh(block)
        return block


block_crud = CRUDBlock(BlocksAndViolations)