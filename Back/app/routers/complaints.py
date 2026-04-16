from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.database import get_db
from app.crud.complaint import complaint_crud
from app.crud.listing import listing_crud
from app.core.dependencies import get_current_user
from app.models import Users

router = APIRouter(prefix="/complaints", tags=["complaints"])


class ComplaintCreate(BaseModel):
    complaint_type: str
    description: Optional[str] = None


@router.post("/{listing_id}")
def create_complaint(
        listing_id: int,
        data: ComplaintCreate,
        db: Session = Depends(get_db),
        current_user: Users = Depends(get_current_user)
):
    listing = listing_crud.get(db, listing_id)
    if not listing:
        raise HTTPException(404, "Объявление не найдено")

    complaint = complaint_crud.create_complaint(
        db,
        current_user.user_id,
        listing_id,
        data.complaint_type,
        data.description
    )
    return {"message": "Жалоба отправлена", "complaint_id": complaint.complaint_id}