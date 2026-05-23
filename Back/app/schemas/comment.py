from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CommentCreate(BaseModel):
    profile_user_id: int
    content: str = Field(..., max_length=500)


class CommentResponse(BaseModel):
    comment_id: int
    author_id: int
    profile_user_id: int
    content: str
    created_date: datetime
    author_name: Optional[str] = None

    class Config:
        from_attributes = True