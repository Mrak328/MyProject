from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    phone_number: str = Field(..., pattern=r'^\+?[0-9]{10,15}$')
    email: Optional[str] = None
    password: str = Field(..., min_length=6)
    role_id: int = 3


class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[str] = None
    avatar_url: Optional[str] = None


class UserResponse(BaseModel):
    user_id: int
    first_name: str
    phone_number: str
    email: Optional[str] = None
    role_id: int
    registration_date: datetime
    last_activity: Optional[datetime] = None
    avatar_url: Optional[str] = None

    class Config:
        from_attributes = True