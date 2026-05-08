from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
from app.database import get_db
from app.crud import (
    user_crud,
    listing_crud,
    complaint_crud,
    block_crud
)
from app.core.dependencies import get_current_user
from app.models import Users
from app.schemas.user import UserResponse
from app.schemas.listing import ListingResponse
from app.schemas.complaint import ComplaintResponse
from app.schemas.block import BlockCreate, BlockResponse

router = APIRouter(prefix="/admin", tags=["admin"])


def check_admin(current_user: Users = Depends(get_current_user)):
    if current_user.role_id != 1:  # 1 = admin
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


# ============================================
# ПОЛЬЗОВАТЕЛИ
# ============================================

@router.get("/users", response_model=List[UserResponse])
async def admin_get_users(
        skip: int = 0,
        limit: int = 100,
        role_id: Optional[int] = None,
        db: Session = Depends(get_db),
        _: Users = Depends(check_admin)
):
    filters = {}
    if role_id:
        filters["role_id"] = role_id
    return user_crud.get_multi(db, skip=skip, limit=limit, filters=filters)


@router.get("/users/{user_id}", response_model=UserResponse)
async def admin_get_user(
        user_id: int,
        db: Session = Depends(get_db),
        _: Users = Depends(check_admin)
):
    user = user_crud.get(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# ============================================
# БЛОКИРОВКИ (через blocks_and_violations)
# ============================================

@router.post("/users/{user_id}/block", response_model=BlockResponse)
async def block_user(
        user_id: int,
        violation_type_id: int,
        description: Optional[str] = None,
        listing_id: Optional[int] = None,
        db: Session = Depends(get_db),
        admin: Users = Depends(check_admin)
):
    user = user_crud.get(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return block_crud.create(db, BlockCreate(
        user_id=user_id,
        violation_type_id=violation_type_id,
        description=description,
        listing_id=listing_id,
        block_status_id=1
    ), commit=True)


@router.put("/users/{user_id}/unblock")
async def unblock_user(
        user_id: int,
        db: Session = Depends(get_db),
        _: Users = Depends(check_admin)
):
    """Снять все активные блокировки с пользователя"""
    blocks = block_crud.get_by_user(db, user_id, only_active=True)
    for block in blocks:
        block_crud.unblock(db, block.block_id)
    return {"message": f"User {user_id} unblocked", "blocks_removed": len(blocks)}


@router.get("/users/{user_id}/blocks", response_model=List[BlockResponse])
async def get_user_blocks(
        user_id: int,
        db: Session = Depends(get_db),
        _: Users = Depends(check_admin)
):
    return block_crud.get_by_user(db, user_id)


# ============================================
# ОБЪЯВЛЕНИЯ
# ============================================

@router.get("/listings", response_model=List[ListingResponse])
async def admin_get_listings(
        skip: int = 0,
        limit: int = 100,
        moderated: Optional[bool] = None,
        listing_status_id: Optional[int] = None,
        db: Session = Depends(get_db),
        _: Users = Depends(check_admin)
):
    filters = {}
    if moderated is not None:
        filters["moderated"] = moderated
    if listing_status_id is not None:
        filters["listing_status_id"] = listing_status_id
    return listing_crud.get_multi(db, skip=skip, limit=limit, filters=filters)


@router.put("/listings/{listing_id}/moderate")
async def moderate_listing(
        listing_id: int,
        moderated: bool = True,
        db: Session = Depends(get_db),
        _: Users = Depends(check_admin)
):
    listing = listing_crud.get(db, listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    listing.moderated = moderated
    db.commit()
    status_text = "approved" if moderated else "rejected"
    return {"message": f"Listing {status_text}", "listing_id": listing_id}


@router.put("/listings/{listing_id}/status")
async def change_listing_status(
        listing_id: int,
        listing_status_id: int,
        db: Session = Depends(get_db),
        _: Users = Depends(check_admin)
):
    listing = listing_crud.update_status(db, listing_id, listing_status_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return {"message": "Status updated", "listing_id": listing_id, "status_id": listing_status_id}


# ============================================
# ЖАЛОБЫ
# ============================================

@router.get("/complaints", response_model=List[ComplaintResponse])
async def admin_get_complaints(
        skip: int = 0,
        limit: int = 100,
        resolved: Optional[bool] = None,
        db: Session = Depends(get_db),
        _: Users = Depends(check_admin)
):
    if resolved is True:
        return [c for c in complaint_crud.get_all(db, skip, limit) if c.resolution is not None]
    elif resolved is False:
        return complaint_crud.get_pending(db)
    return complaint_crud.get_all(db, skip, limit)


@router.put("/complaints/{complaint_id}/resolve")
async def resolve_complaint(
        complaint_id: int,
        resolution: str,
        db: Session = Depends(get_db),
        admin: Users = Depends(check_admin)
):
    complaint = complaint_crud.resolve(db, complaint_id, admin.user_id, resolution)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return {"message": "Complaint resolved", "complaint_id": complaint_id}


# ============================================
# СТАТИСТИКА АДМИНА
# ============================================

@router.get("/stats")
async def admin_stats(
        db: Session = Depends(get_db),
        _: Users = Depends(check_admin)
):
    return {
        "total_users": user_crud.count(db),
        "total_listings": listing_crud.count(db),
        "pending_listings": listing_crud.count(db, {"moderated": False}),
        "pending_complaints": len(complaint_crud.get_pending(db)),
        "active_blocks": len(block_crud.get_multi(db, limit=10000, filters={"block_status_id": 1}))
    }