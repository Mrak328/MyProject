from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class BlockCreate(BaseModel):
    user_id: int
    violation_type_id: int
    description: Optional[str] = Field(None, max_length=500)
    listing_id: Optional[int] = None
    block_status_id: int = 1


class BlockUpdate(BaseModel):
    unblock_date: Optional[datetime] = None
    block_status_id: Optional[int] = None
    description: Optional[str] = Field(None, max_length=500)


class BlockResponse(BaseModel):
    block_id: int
    user_id: int
    violation_type_id: Optional[int] = None
    violation_type_name: Optional[str] = None
    description: Optional[str] = None
    listing_id: Optional[int] = None
    block_date: datetime
    unblock_date: Optional[datetime] = None
    blocked_by_admin: Optional[int] = None
    block_status_id: Optional[int] = None
    block_status_name: Optional[str] = None

    class Config:
        from_attributes = True