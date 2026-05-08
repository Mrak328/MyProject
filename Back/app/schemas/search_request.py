from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


class SearchRequestCreate(BaseModel):
    user_id: Optional[int] = None
    agent_id: Optional[int] = None
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    min_area: Optional[Decimal] = None
    max_area: Optional[Decimal] = None
    rooms: Optional[int] = None
    country_id: Optional[int] = None
    region_id: Optional[int] = None
    city_id: Optional[int] = None
    district_id: Optional[int] = None
    street_id: Optional[int] = None
    house_id: Optional[int] = None
    description: Optional[str] = None


class SearchRequestResponse(BaseModel):
    request_id: int
    user_id: Optional[int] = None
    agent_id: Optional[int] = None
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    min_area: Optional[Decimal] = None
    max_area: Optional[Decimal] = None
    rooms: Optional[int] = None
    country_id: Optional[int] = None
    region_id: Optional[int] = None
    city_id: Optional[int] = None
    district_id: Optional[int] = None
    street_id: Optional[int] = None
    house_id: Optional[int] = None
    description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True