from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal


class FavoriteCreate(BaseModel):
    user_id: int
    listing_id: int


class FavoriteResponse(BaseModel):
    favorite_id: int
    user_id: int
    listing_id: int
    added_date: Optional[datetime] = None
    listing_title: Optional[str] = None
    listing_price: Optional[Decimal] = None
    listing_photo: Optional[str] = None

    class Config:
        from_attributes = True