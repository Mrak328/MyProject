from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.crud.user import user_crud
from app.crud.listing import listing_crud
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/admin", tags=["admin"])

def check_admin(current_user: User = Depends(get_current_user)):
    if current_user.role_id != 1:  # 1 = admin
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

# 🔹 GET /api/admin/users - все пользователи (только админ)
@router.get("/users")
async def admin_get_users(
    db: Session = Depends(get_db),
    _: User = Depends(check_admin)
):
    return user_crud.get_multi(db, skip=0, limit=1000)

# 🔹 PUT /api/admin/users/{user_id}/block - блокировка пользователя
@router.put("/users/{user_id}/block")
async def block_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(check_admin)
):
    user = user_crud.get(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.status = "blocked"
    db.commit()
    return {"message": "User blocked"}

# 🔹 PUT /api/admin/listings/{listing_id}/moderate - модерация объявления
@router.put("/listings/{listing_id}/moderate")
async def moderate_listing(
    listing_id: int,
    moderated: bool = True,
    db: Session = Depends(get_db),
    _: User = Depends(check_admin)
):
    listing = listing_crud.get(db, listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    listing.moderated = moderated
    listing.moderation_date = datetime.now()
    db.commit()
    return {"message": "Listing moderated"}