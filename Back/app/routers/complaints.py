from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.crud.complaint import complaint_crud
from app.crud.listing import listing_crud
from app.crud.action_log import action_log_crud
from app.schemas.complaint import ComplaintCreate, ComplaintResponse
from app.schemas.common import MessageResponse
from app.core.dependencies import get_current_user
from app.models import Users

router = APIRouter(prefix="/complaints", tags=["complaints"])


@router.post("/{listing_id}", response_model=MessageResponse)
async def create_complaint(listing_id: int, data: ComplaintCreate, db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    listing = listing_crud.get(db, listing_id)
    if not listing: raise HTTPException(status_code=404, detail="Объявление не найдено")
    if listing.user_id == current_user.user_id: raise HTTPException(status_code=400, detail="Нельзя жаловаться на своё объявление")
    complaint = complaint_crud.create(db, complainant_user_id=current_user.user_id, listing_id=listing_id, violator_user_id=listing.user_id, complaint_type_id=data.complaint_type_id, description=data.description)
    action_log_crud.log(db, current_user.user_id, 8, listing_id=listing_id)
    return {"message": "Жалоба отправлена", "complaint_id": complaint.complaint_id, "success": True}


@router.get("/my", response_model=List[ComplaintResponse])
async def get_my_complaints(db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    return complaint_crud.get_by_complainant(db, current_user.user_id)


@router.get("/{complaint_id}", response_model=ComplaintResponse)
async def get_complaint(complaint_id: int, db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    complaint = complaint_crud.get(db, complaint_id)
    if not complaint: raise HTTPException(status_code=404, detail="Жалоба не найдена")
    return complaint