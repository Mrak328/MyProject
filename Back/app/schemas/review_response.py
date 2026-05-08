from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ReviewResponseCreate(BaseModel):
    review_id: int
    user_id: int
    content: str = Field(..., max_length=500)


class ReviewResponseOut(BaseModel):
    response_id: int
    review_id: int
    user_id: int
    content: str
    response_date: datetime

    class Config:
        from_attributes = True