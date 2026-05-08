from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ChatCreate(BaseModel):
    user_id: int
    agent_id: int
    title: Optional[str] = Field(None, max_length=200)


class ChatResponse(BaseModel):
    chat_id: int
    user_id: int
    agent_id: int
    title: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool

    class Config:
        from_attributes = True