from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ComplaintCreate(BaseModel):
    listing_id: Optional[int] = None
    violator_user_id: Optional[int] = None
    complaint_type_id: int
    description: Optional[str] = Field(None, max_length=500)


class ComplaintUpdate(BaseModel):
    resolution: Optional[str] = Field(None, max_length=500)


class ComplaintResponse(BaseModel):
    complaint_id: int
    complainant_user_id: int
    listing_id: Optional[int] = None
    violator_user_id: Optional[int] = None
    complaint_type_id: Optional[int] = None
    complaint_type_name: Optional[str] = None
    description: Optional[str] = None
    created_date: datetime
    processing_date: Optional[datetime] = None
    moderator_id: Optional[int] = None
    resolution: Optional[str] = None

    class Config:
        from_attributes = True