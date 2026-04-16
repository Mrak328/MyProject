from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.crud.listing import listing_crud
from app.crud.complaint import complaint_crud
from app.models import Listing, Complaint, Users
from app.schemas.listing import ListingResponse
from app.schemas.common import MessageResponse

router = APIRouter(prefix="/moderation", tags=["moderation"])


# ==================== ОБЪЯВЛЕНИЯ НА МОДЕРАЦИЮ ====================

@router.get("/pending-listings", response_model=List[ListingResponse])
async def get_pending_listings(
    db: Session = Depends(get_db)
):
    """Список объявлений на модерацию (непроверенные)"""
    listings = db.query(Listing).filter(
        Listing.moderated == False,
        Listing.listing_status_id == 1
    ).order_by(Listing.publication_date.desc()).all()

    from app.crud.photo import photo_crud
    result = []
    for listing in listings:
        photos = photo_crud.get_by_listing(db, listing.listing_id)
        listing_dict = {
            "listing_id": listing.listing_id,
            "title": listing.title,
            "description": listing.description,
            "price": listing.price,
            "address": listing.address,
            "total_area": listing.total_area,
            "rooms": listing.rooms,
            "property_type_id": listing.property_type_id,
            "deal_type_id": listing.deal_type_id,
            "user_id": listing.user_id,
            "listing_status_id": listing.listing_status_id,
            "views": listing.views,
            "moderated": listing.moderated,
            "publication_date": listing.publication_date,
            "contact_phone": listing.contact_phone,
            "contact_person": listing.contact_person,
            "photos": [p.file_url for p in photos]
        }
        result.append(listing_dict)

    return result


@router.put("/approve-listing/{listing_id}")
async def approve_listing(
    listing_id: int,
    db: Session = Depends(get_db)
):
    """Одобрить объявление"""
    listing = listing_crud.get(db, listing_id)
    if not listing:
        raise HTTPException(404, "Объявление не найдено")

    listing.moderated = True
    listing.moderation_date = datetime.now()
    db.commit()

    return MessageResponse(message="Объявление одобрено")


@router.delete("/reject-listing/{listing_id}")
async def reject_listing(
    listing_id: int,
    reason: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Отклонить объявление (удалить)"""
    listing = listing_crud.get(db, listing_id)
    if not listing:
        raise HTTPException(404, "Объявление не найдено")

    if reason:
        print(f"Объявление {listing_id} отклонено. Причина: {reason}")

    listing_crud.delete(db, listing_id)

    return MessageResponse(message="Объявление отклонено и удалено")


# ==================== ЖАЛОБЫ ====================

@router.get("/complaints")
async def get_complaints(
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Список жалоб (фильтр по статусу)"""
    query = db.query(Complaint).order_by(Complaint.created_date.desc())

    if status:
        query = query.filter(Complaint.processing_status == status)

    complaints = query.all()

    result = []
    for c in complaints:
        listing = db.query(Listing).filter(Listing.listing_id == c.listing_id).first()
        result.append({
            "complaint_id": c.complaint_id,
            "complaint_type": c.complaint_type,
            "description": c.description,
            "status": c.processing_status,
            "created_date": c.created_date,
            "listing": {
                "listing_id": listing.listing_id if listing else None,
                "title": listing.title if listing else "Объявление удалено",
                "address": listing.address if listing else None,
                "user_id": listing.user_id if listing else None
            },
            "complainant_user_id": c.complainant_user_id,
            "violator_user_id": c.violator_user_id
        })

    return result


@router.get("/complaints/{complaint_id}")
async def get_complaint_detail(
    complaint_id: int,
    db: Session = Depends(get_db)
):
    """Детали жалобы"""
    complaint = db.query(Complaint).filter(Complaint.complaint_id == complaint_id).first()
    if not complaint:
        raise HTTPException(404, "Жалоба не найдена")

    listing = db.query(Listing).filter(Listing.listing_id == complaint.listing_id).first()

    return {
        "complaint_id": complaint.complaint_id,
        "complaint_type": complaint.complaint_type,
        "description": complaint.description,
        "status": complaint.processing_status,
        "created_date": complaint.created_date,
        "processing_date": complaint.processing_date,
        "moderator_id": complaint.moderator_id,
        "resolution": complaint.resolution,
        "listing": {
            "listing_id": listing.listing_id if listing else None,
            "title": listing.title if listing else "Объявление удалено",
            "address": listing.address if listing else None,
            "user_id": listing.user_id if listing else None
        },
        "complainant_user_id": complaint.complainant_user_id,
        "violator_user_id": complaint.violator_user_id
    }


@router.put("/complaints/{complaint_id}/approve")
async def approve_complaint(
    complaint_id: int,
    action: str = "hide_listing",
    resolution: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Одобрить жалобу и применить действие"""
    complaint = db.query(Complaint).filter(Complaint.complaint_id == complaint_id).first()
    if not complaint:
        raise HTTPException(404, "Жалоба не найдена")

    complaint.processing_status = "approved"
    complaint.processing_date = datetime.now()
    complaint.resolution = resolution or f"Применено действие: {action}"

    listing = db.query(Listing).filter(Listing.listing_id == complaint.listing_id).first()

    if action == "hide_listing" and listing:
        listing.listing_status_id = 2
        listing.moderated = False
    elif action == "delete_listing" and listing:
        db.delete(listing)
    elif action == "warn_user" and listing:
        pass
    elif action == "ban_user" and listing:
        user = db.query(Users).filter(Users.user_id == listing.user_id).first()
        if user:
            user.status = "banned"

    db.commit()

    return MessageResponse(message="Жалоба одобрена")


@router.put("/complaints/{complaint_id}/reject")
async def reject_complaint(
    complaint_id: int,
    resolution: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Отклонить жалобу"""
    complaint = db.query(Complaint).filter(Complaint.complaint_id == complaint_id).first()
    if not complaint:
        raise HTTPException(404, "Жалоба не найдена")

    complaint.processing_status = "rejected"
    complaint.processing_date = datetime.now()
    complaint.resolution = resolution or "Жалоба отклонена"
    db.commit()

    return MessageResponse(message="Жалоба отклонена")