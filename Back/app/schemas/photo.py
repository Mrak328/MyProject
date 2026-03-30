from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PhotoBase(BaseModel):
    file_url: str
    title: Optional[str] = None


class PhotoCreate(PhotoBase):
    listing_id: int


class PhotoResponse(PhotoBase):
    id: int
    listing_id: int
    file_size: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True