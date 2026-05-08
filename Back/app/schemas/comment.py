from pydantic import BaseModel, Field
from datetime import datetime

class CommentCreate(BaseModel):
    review_id: int
    content: str = Field(..., max_length=500)

class CommentResponse(BaseModel):
    comment_id: int
    review_id: int
    user_id: int
    content: str
    created_date: datetime
    user_name: str = ""

    class Config:
        from_attributes = True