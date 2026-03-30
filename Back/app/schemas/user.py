from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    phone_number: str = Field(..., pattern=r'^\+?[0-9]{10,15}$')
    email: Optional[EmailStr] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1)
    email: Optional[EmailStr] = None
    phone_confirmed: Optional[bool] = None
    email_confirmed: Optional[bool] = None
    avatar_url: Optional[str] = None
    status: Optional[str] = None


class UserResponse(UserBase):
    user_id: int  # ← user_id вместо id
    role_id: int
    rating: float
    reviews_count: int
    status: str
    registration_date: datetime  # ← registration_date вместо created_at
    avatar_url: Optional[str] = None

    class Config:
        from_attributes = True