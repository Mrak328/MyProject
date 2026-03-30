import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.database import get_db
from app.crud.listing import listing_crud
from app.crud.photo import photo_crud
from app.schemas.photo import PhotoCreate, PhotoResponse
from app.core.config import settings

router = APIRouter(prefix="/photos", tags=["photos"])


@router.post("/upload/{listing_id}", response_model=PhotoResponse)
async def upload_photo(
        listing_id: int,
        file: UploadFile = File(...),
        db: Session = Depends(get_db)
):
    listing = listing_crud.get(db, id=listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Extension {ext} not allowed")

    filename = f"listing_{listing_id}_{datetime.now().timestamp()}{ext}"
    filepath = os.path.join(settings.UPLOAD_DIR, filename)

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    photo_data = PhotoCreate(
        listing_id=listing_id,
        file_url=f"/static/photos/{filename}",
        title=file.filename
    )

    return photo_crud.create(db, photo_data)


@router.delete("/{photo_id}")
async def delete_photo(photo_id: int, db: Session = Depends(get_db)):
    photo = photo_crud.get(db, id=photo_id)
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    filepath = os.path.join(settings.UPLOAD_DIR, os.path.basename(photo.file_url))
    if os.path.exists(filepath):
        os.remove(filepath)

    photo_crud.delete(db, id=photo_id)
    return {"message": "Photo deleted"}