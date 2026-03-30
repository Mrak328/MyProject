from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ReviewBase(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    content: Optional[str] = Field(None, max_length=1000)


class ReviewCreate(ReviewBase):
    author_id: int
    user_id: int
    listing_id: Optional[int] = None


class ReviewResponse(ReviewBase):
    review_id: int  # ← review_id вместо id
    author_id: int
    user_id: int
    listing_id: Optional[int] = None
    created_date: datetime  # ← created_date вместо created_at

    class Config:
        from_attributes = True