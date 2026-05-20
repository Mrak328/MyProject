from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
from app.crud.base import CRUDBase
from app.models import Message


class CRUDMessage(CRUDBase[Message]):

    def get_by_chat(self, db: Session, chat_id: int, skip: int = 0, limit: int = 100) -> List[Message]:
        return db.query(Message).filter(Message.chat_id == chat_id).order_by(Message.sent_at).offset(skip).limit(
            limit).all()

    def mark_as_read(self, db: Session, chat_id: int, user_id: int) -> int:
        updated = db.query(Message).filter(Message.chat_id == chat_id, Message.sender_id != user_id,
                                           Message.is_read == False).update({Message.is_read: True},
                                                                            synchronize_session=False)
        db.commit()
        return updated


message_crud = CRUDMessage(Message)