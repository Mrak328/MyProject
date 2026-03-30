from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class FavoriteBase(BaseModel):
    note: Optional[str] = None


class FavoriteCreate(FavoriteBase):
    user_id: int
    listing_id: int


class FavoriteResponse(FavoriteBase):
    id: int
    user_id: int
    listing_id: int
    created_at: datetime
    listing_title: Optional[str] = None
    listing_price: Optional[float] = None

    class Config:
        from_attributes = True