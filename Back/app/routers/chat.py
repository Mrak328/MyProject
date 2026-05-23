from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.database import get_db
from app.crud.chat import chat_crud
from app.crud.message import message_crud
from app.schemas.chat import ChatResponse, ChatCreate
from app.schemas.message import MessageCreate, MessageResponse
from app.schemas.common import MessageResponse as MsgResponse
from app.core.dependencies import get_current_user
from app.models import Users, Chat, AgentProfile

router = APIRouter(prefix="/chats", tags=["chats"])


@router.get("/", response_model=List[ChatResponse])
async def get_my_chats(db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    chats = db.query(Chat).filter(
        (Chat.user_id == current_user.user_id) | (Chat.agent_id == current_user.user_id)
    ).order_by(Chat.updated_at.desc()).all()
    return chats


@router.post("/", response_model=ChatResponse, status_code=status.HTTP_201_CREATED)
async def create_chat(data: ChatCreate, db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    if data.user_id:
        other_user = db.query(Users).filter(Users.user_id == data.user_id).first()
        title = other_user.first_name if other_user else "Чат"

        agent = db.query(AgentProfile).filter(AgentProfile.user_id == data.user_id).first()
        agent_id = agent.agent_id if agent else None

        existing = db.query(Chat).filter(
            ((Chat.user_id == current_user.user_id) & (Chat.agent_id == agent_id)) |
            ((Chat.user_id == data.user_id) & (Chat.agent_id == current_user.user_id))
        ).first()
        if existing:
            if not existing.is_active:
                existing.is_active = True
                existing.updated_at = datetime.now()
                existing.title = title
                db.commit()
            return existing

        chat = Chat(user_id=current_user.user_id, agent_id=agent_id, title=title, is_active=True)
        db.add(chat)
        db.commit()
        db.refresh(chat)
        return chat

    if data.agent_id:
        existing = db.query(Chat).filter(
            Chat.user_id == current_user.user_id, Chat.agent_id == data.agent_id
        ).first()
        if existing:
            if not existing.is_active:
                existing.is_active = True
                existing.updated_at = datetime.now()
                db.commit()
            return existing
        chat = Chat(user_id=current_user.user_id, agent_id=data.agent_id, title=data.title or "Чат", is_active=True)
        db.add(chat)
        db.commit()
        db.refresh(chat)
        return chat

    raise HTTPException(status_code=400, detail="user_id или agent_id обязателен")


@router.get("/{chat_id}", response_model=ChatResponse)
async def get_chat(chat_id: int, db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    chat = chat_crud.get(db, chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Чат не найден")
    if chat.user_id != current_user.user_id and chat.agent_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Нет доступа")
    return chat


@router.put("/{chat_id}/close", response_model=MsgResponse)
async def close_chat(chat_id: int, db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    chat = chat_crud.get(db, chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Чат не найден")
    if chat.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Нет доступа")
    chat_crud.close(db, chat_id)
    return {"message": "Чат закрыт", "success": True}


@router.delete("/{chat_id}", response_model=MsgResponse)
async def delete_chat(chat_id: int, db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    chat = chat_crud.get(db, chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Чат не найден")
    if chat.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Нет доступа")
    chat_crud.delete(db, chat_id)
    return {"message": "Чат удалён", "success": True}


@router.get("/{chat_id}/messages", response_model=List[MessageResponse])
async def get_messages(chat_id: int, skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=500), db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    chat = chat_crud.get(db, chat_id)
    if not chat or (chat.user_id != current_user.user_id and chat.agent_id != current_user.user_id):
        raise HTTPException(status_code=403, detail="Нет доступа")
    message_crud.mark_as_read(db, chat_id, current_user.user_id)
    return message_crud.get_by_chat(db, chat_id, skip, limit)


@router.post("/{chat_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(chat_id: int, data: MessageCreate, db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    chat = chat_crud.get(db, chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Чат не найден")
    if chat.user_id != current_user.user_id and chat.agent_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Нет доступа")
    if not chat.is_active:
        raise HTTPException(status_code=400, detail="Чат закрыт")
    msg = message_crud.create(db, {
        "chat_id": chat_id,
        "sender_id": current_user.user_id,
        "content": data.content,
        "attachment_url": data.attachment_url
    })
    chat.updated_at = msg.sent_at
    db.commit()
    return msg