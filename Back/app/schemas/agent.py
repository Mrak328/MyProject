from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AgentProfileCreate(BaseModel):
    user_id: int
    company_name: Optional[str] = Field(None, max_length=200)
    license_number: Optional[str] = Field(None, max_length=50)
    about: Optional[str] = None


class AgentProfileUpdate(BaseModel):
    company_name: Optional[str] = Field(None, max_length=200)
    license_number: Optional[str] = Field(None, max_length=50)
    about: Optional[str] = None


class AgentProfileResponse(BaseModel):
    agent_id: int
    user_id: int
    company_name: Optional[str] = None
    license_number: Optional[str] = None
    about: Optional[str] = None
    created_at: datetime
    user_name: Optional[str] = None
    user_phone: Optional[str] = None

    class Config:
        from_attributes = True