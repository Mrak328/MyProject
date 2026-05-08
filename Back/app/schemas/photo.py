from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PhotoCreate(BaseModel):
    listing_id: int
    file_url: str
    title: Optional[str] = None
    file_size: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None


class PhotoResponse(BaseModel):
    photo_id: int
    listing_id: int
    file_url: str
    title: Optional[str] = None
    file_size: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    upload_date: datetime

    class Config:
        from_attributes = True