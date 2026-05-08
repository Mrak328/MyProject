from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


# ============================================
# БАЗОВАЯ СХЕМА (ОБЩИЕ ПОЛЯ)
# ============================================

class ListingBase(BaseModel):
    property_type_id: int
    deal_type_id: int
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    price: Decimal = Field(..., gt=0)
    total_area: Optional[Decimal] = Field(None, gt=0)
    rooms: Optional[int] = Field(None, ge=1, le=10)
    floor: Optional[int] = None
    max_floor: Optional[int] = None
    renovation_condition_id: Optional[int] = None
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None
    market_type_id: Optional[int] = None
    developer_name: Optional[str] = None
    listing_status_id: int = 1


# ============================================
# СОЗДАНИЕ
# ============================================

class ListingCreate(ListingBase):
    """user_id берётся из токена"""
    # География — можно передать готовый address_id или компоненты
    address_id: Optional[int] = None

    # Либо компоненты адреса (для создания через географию)
    country_id: Optional[int] = None
    region_id: Optional[int] = None
    city_id: Optional[int] = None
    district_id: Optional[int] = None
    street_id: Optional[int] = None
    house_id: Optional[int] = None
    apartment_id: Optional[int] = None


# ============================================
# ОБНОВЛЕНИЕ
# ============================================

class ListingUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, gt=0)
    total_area: Optional[Decimal] = Field(None, gt=0)
    rooms: Optional[int] = Field(None, ge=1, le=10)
    floor: Optional[int] = None
    max_floor: Optional[int] = None
    listing_status_id: Optional[int] = None
    renovation_condition_id: Optional[int] = None
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None
    market_type_id: Optional[int] = None
    developer_name: Optional[str] = None


# ============================================
# ОТВЕТ
# ============================================

class ListingResponse(BaseModel):
    listing_id: int
    user_id: int
    property_type_id: int
    deal_type_id: int
    listing_status_id: int
    title: str
    description: Optional[str] = None
    price: Decimal
    total_area: Optional[Decimal] = None
    rooms: Optional[int] = None
    floor: Optional[int] = None
    max_floor: Optional[int] = None
    renovation_condition_id: Optional[int] = None
    market_type_id: Optional[int] = None
    developer_name: Optional[str] = None
    views: int
    moderated: bool
    publication_date: datetime
    update_date: Optional[datetime] = None
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None

    # Адрес (собирается JOIN)
    address: Optional[str] = None

    # Фото
    photos: List[str] = []

    class Config:
        from_attributes = True