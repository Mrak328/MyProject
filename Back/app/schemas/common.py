from pydantic import BaseModel
from typing import Optional, Generic, TypeVar, List

T = TypeVar('T')

class MessageResponse(BaseModel):
    message: str
    success: bool = True

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    size: int
    pages: int

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    status_code: int
