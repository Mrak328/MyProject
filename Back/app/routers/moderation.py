from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.crud.listing import listing_crud
from app.crud.complaint import complaint_crud
from app.crud.block import block_crud
from app.crud.photo import photo_crud
from app.crud.analytics import analytics_crud
from app.models import Listing, Complaint
from app.schemas.listing import ListingResponse
from app.schemas.common import MessageResponse

router = APIRouter(prefix="/moderation", tags=["moderation"])


def _enrich_listing(listing, db: Session) -> dict:
    photos = photo_crud.get_by_listing(db, listing.listing_id)
    return {
        "listing_id": listing.listing_id,
        "title": listing.title,
        "description": listing.description,
        "price": listing.price,
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
        "address": analytics_crud._build_address(db, listing.address_id),
        "photos": [p.file_url for p in photos]
    }


# ============================================
# ОБЪЯВЛЕНИЯ НА МОДЕРАЦИЮ
# ============================================

@router.get("/pending-listings", response_model=List[ListingResponse])
async def get_pending_listings(db: Session = Depends(get_db)):
    listings = (
        db.query(Listing)
        .filter(
            Listing.moderated == False,
            Listing.listing_status_id == 1
        )
        .order_by(Listing.publication_date.desc())
        .all()
    )
    return [_enrich_listing(l, db) for l in listings]


@router.put("/listings/{listing_id}/approve", response_model=MessageResponse)
async def approve_listing(listing_id: int, db: Session = Depends(get_db)):
    listing = listing_crud.get(db, listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Объявление не найдено")

    listing.moderated = True
    listing.update_date = datetime.now()
    db.commit()
    return {"message": "Объявление одобрено", "success": True}


@router.put("/listings/{listing_id}/reject", response_model=MessageResponse)
async def reject_listing(
    listing_id: int,
    reason: Optional[str] = None,
    db: Session = Depends(get_db)
):
    listing = listing_crud.get(db, listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Объявление не найдено")

    listing.listing_status_id = 2
    listing.moderated = False
    listing.update_date = datetime.now()
    db.commit()
    return {"message": f"Объявление отклонено. Причина: {reason or 'не указана'}", "success": True}


# ============================================
# ЖАЛОБЫ
# ============================================

@router.get("/complaints")
async def get_complaints(
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db)
):
    if status_filter == "pending":
        complaints = complaint_crud.get_pending(db)
    elif status_filter == "resolved":
        all_complaints = complaint_crud.get_all(db)
        complaints = [c for c in all_complaints if c.resolution is not None]
    else:
        complaints = complaint_crud.get_all(db)

    result = []
    for c in complaints:
        listing = listing_crud.get(db, c.listing_id) if c.listing_id else None
        result.append({
            "complaint_id": c.complaint_id,
            "complaint_type_id": c.complaint_type_id,
            "description": c.description,
            "is_resolved": c.resolution is not None,
            "resolution": c.resolution,
            "created_date": c.created_date,
            "processing_date": c.processing_date,
            "listing": {
                "listing_id": listing.listing_id if listing else None,
                "title": listing.title if listing else "Объявление удалено",
                "address": analytics_crud._build_address(db, listing.address_id) if listing else None,
                "user_id": listing.user_id if listing else None
            } if listing else None,
            "complainant_user_id": c.complainant_user_id,
            "violator_user_id": c.violator_user_id
        })

    return result


@router.get("/complaints/{complaint_id}")
async def get_complaint_detail(complaint_id: int, db: Session = Depends(get_db)):
    complaint = complaint_crud.get(db, complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Жалоба не найдена")

    listing = listing_crud.get(db, complaint.listing_id) if complaint.listing_id else None

    return {
        "complaint_id": complaint.complaint_id,
        "complaint_type_id": complaint.complaint_type_id,
        "description": complaint.description,
        "is_resolved": complaint.resolution is not None,
        "resolution": complaint.resolution,
        "created_date": complaint.created_date,
        "processing_date": complaint.processing_date,
        "moderator_id": complaint.moderator_id,
        "listing": {
            "listing_id": listing.listing_id if listing else None,
            "title": listing.title if listing else "Объявление удалено",
            "address": analytics_crud._build_address(db, listing.address_id) if listing else None,
            "user_id": listing.user_id if listing else None
        } if listing else None,
        "complainant_user_id": complaint.complainant_user_id,
        "violator_user_id": complaint.violator_user_id
    }


@router.put("/complaints/{complaint_id}/resolve", response_model=MessageResponse)
async def resolve_complaint(
    complaint_id: int,
    action: str = "hide_listing",
    resolution: Optional[str] = None,
    moderator_id: int = 1,
    db: Session = Depends(get_db)
):
    complaint = complaint_crud.get(db, complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Жалоба не найдена")

    resolution_text = resolution or f"Применено действие: {action}"
    complaint_crud.resolve(db, complaint_id, moderator_id, resolution_text)

    listing = listing_crud.get(db, complaint.listing_id) if complaint.listing_id else None

    if listing:
        if action == "hide_listing":
            listing.listing_status_id = 2
            listing.moderated = False
            listing.update_date = datetime.now()
        elif action == "delete_listing":
            listing_crud.delete_obj(db, listing)
        elif action == "ban_user":
            block_crud.create(db, {
                "user_id": listing.user_id,
                "violation_type_id": 1,
                "listing_id": listing.listing_id,
                "description": f"Бан по жалобе #{complaint_id}",
                "block_status_id": 1
            })

    db.commit()
    return {"message": "Жалоба обработана", "success": True}