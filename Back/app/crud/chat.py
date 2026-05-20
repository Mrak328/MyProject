from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from app.crud.base import CRUDBase
from app.models import Chat


class CRUDChat(CRUDBase[Chat]):

    def get_by_user(self, db: Session, user_id: int) -> List[Chat]:
        return db.query(Chat).filter(Chat.user_id == user_id).order_by(desc(Chat.updated_at)).all()

    def get_by_agent(self, db: Session, agent_id: int) -> List[Chat]:
        return db.query(Chat).filter(Chat.agent_id == agent_id).order_by(desc(Chat.updated_at)).all()

    def get_active(self, db: Session, user_id: int, agent_id: int) -> Optional[Chat]:
        return db.query(Chat).filter(Chat.user_id == user_id, Chat.agent_id == agent_id, Chat.is_active == True).first()

    def close(self, db: Session, chat_id: int) -> Optional[Chat]:
        chat = self.get(db, chat_id)
        if chat:
            chat.is_active = False
            db.commit()
            db.refresh(chat)
        return chat


chat_crud = CRUDChat(Chat)