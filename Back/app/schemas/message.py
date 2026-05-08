from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class MessageCreate(BaseModel):
    chat_id: int
    sender_id: int
    content: Optional[str] = None
    attachment_url: Optional[str] = None


class MessageResponse(BaseModel):
    message_id: int
    chat_id: int
    sender_id: int
    content: Optional[str] = None
    sent_at: datetime
    is_read: bool
    attachment_url: Optional[str] = None

    class Config:
        from_attributes = True