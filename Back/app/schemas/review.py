from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ReviewCreate(BaseModel):
    author_id: int
    user_id: int
    listing_id: Optional[int] = None
    content: Optional[str] = Field(None, max_length=1000)


class ReviewResponse(BaseModel):
    review_id: int
    author_id: int
    user_id: int
    listing_id: Optional[int] = None
    content: Optional[str] = None
    created_date: datetime

    class Config:
        from_attributes = True