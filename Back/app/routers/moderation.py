from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.crud.listing import listing_crud
from app.crud.review import review_crud
from app.schemas.listing import ListingResponse
from app.schemas.review import ReviewResponse
from app.core.dependencies import get_current_moderator
from app.models import Users

router = APIRouter(prefix="/moderation", tags=["moderation"])


@router.get("/pending-listings", response_model=List[ListingResponse])
async def get_pending_listings(
        db: Session = Depends(get_db),
        current_user: Users = Depends(get_current_moderator)
):
    """Список объявлений на модерацию (только для модератора)"""
    listings = db.query(Listing).filter(Listing.moderated == False).all()
    return listings


@router.put("/approve-listing/{listing_id}")
async def approve_listing(
        listing_id: int,
        db: Session = Depends(get_db),
        current_user: Users = Depends(get_current_moderator)
):
    """Одобрить объявление (только для модератора)"""
    listing = listing_crud.get(db, listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    listing.moderated = True
    listing.moderator_id = current_user.user_id
    listing.moderation_date = datetime.now()
    db.commit()

    return {"message": "Listing approved"}


@router.delete("/reject-listing/{listing_id}")
async def reject_listing(
        listing_id: int,
        db: Session = Depends(get_db),
        current_user: Users = Depends(get_current_moderator)
):
    """Отклонить объявление (только для модератора)"""
    listing = listing_crud.delete(db, listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    return {"message": "Listing rejected and deleted"}


@router.get("/complaints", response_model=List[dict])
async def get_complaints(
        db: Session = Depends(get_db),
        current_user: Users = Depends(get_current_moderator)
):
    """Список жалоб (только для модератора)"""
    complaints = db.query(Complaint).filter(
        Complaint.processing_status == "new"
    ).all()
    return complaints