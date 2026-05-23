from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ChatCreate(BaseModel):
    user_id: Optional[int] = None
    agent_id: Optional[int] = None
    title: Optional[str] = Field(None, max_length=200)


class ChatResponse(BaseModel):
    chat_id: int
    user_id: int
    agent_id: Optional[int] = None
    title: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool
    agent_name: Optional[str] = None

    class Config:
        from_attributes = True