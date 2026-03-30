from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class ListingBase(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    property_type_id: int
    deal_type_id: int
    address: str
    price: Decimal = Field(..., gt=0)
    total_area: Optional[Decimal] = Field(None, gt=0)
    contact_phone: Optional[str] = None
    contact_person: Optional[str] = None
    # rooms: Optional[int] = None  # ← УДАЛИТЬ если есть


class ListingCreate(ListingBase):
    user_id: int


class ListingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, gt=0)
    listing_status_id: Optional[int] = None
    contact_phone: Optional[str] = None


class ListingResponse(ListingBase):
    listing_id: int
    user_id: int
    listing_status_id: int
    views: int
    moderated: bool
    publication_date: datetime
    photos: List[str] = []

    class Config:
        from_attributes = True