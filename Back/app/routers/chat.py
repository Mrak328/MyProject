from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.crud.chat import chat_crud
from app.crud.message import message_crud
from app.schemas.chat import ChatCreate, ChatResponse
from app.schemas.message import MessageCreate, MessageResponse
from app.schemas.common import MessageResponse
from app.core.dependencies import get_current_user
from app.models import Users

router = APIRouter(prefix="/chats", tags=["chats"])


@router.get("/", response_model=List[ChatResponse])
async def get_my_chats(
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Мои чаты"""
    return chat_crud.get_by_user(db, current_user.user_id)


@router.post("/", response_model=ChatResponse, status_code=status.HTTP_201_CREATED)
async def create_chat(
    data: ChatCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Начать чат с агентом"""
    # Проверка: нет ли уже активного чата
    existing = chat_crud.get_active(db, current_user.user_id, data.agent_id)
    if existing:
        return existing

    return chat_crud.create(db, {
        "user_id": current_user.user_id,
        "agent_id": data.agent_id,
        "title": data.title
    })


@router.get("/{chat_id}", response_model=ChatResponse)
async def get_chat(
    chat_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    chat = chat_crud.get(db, chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Чат не найден")
    if chat.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Нет доступа")
    return chat


@router.put("/{chat_id}/close", response_model=MessageResponse)
async def close_chat(
    chat_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Закрыть чат"""
    chat = chat_crud.get(db, chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Чат не найден")
    if chat.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Нет доступа")

    chat_crud.close(db, chat_id)
    return {"message": "Чат закрыт", "success": True}


# ============================================
# СООБЩЕНИЯ
# ============================================

@router.get("/{chat_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    chat_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Сообщения чата"""
    chat = chat_crud.get(db, chat_id)
    if not chat or chat.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Нет доступа")

    # Отмечаем как прочитанные
    message_crud.mark_as_read(db, chat_id, current_user.user_id)

    return message_crud.get_by_chat(db, chat_id, skip, limit)


@router.post("/{chat_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    chat_id: int,
    data: MessageCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Отправить сообщение"""
    chat = chat_crud.get(db, chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Чат не найден")
    if not chat.is_active:
        raise HTTPException(status_code=400, detail="Чат закрыт")

    return message_crud.create(db, {
        "chat_id": chat_id,
        "sender_id": current_user.user_id,
        "content": data.content,
        "attachment_url": data.attachment_url
    })