import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.crud.listing import listing_crud
from app.crud.photo import photo_crud
from app.schemas.photo import PhotoResponse
from app.core.config import settings
from app.core.dependencies import get_current_user
from app.models import Users

router = APIRouter(prefix="/photos", tags=["photos"])


def _save_file(file: UploadFile, listing_id: int) -> str:
    """Сохранить файл на диск, вернуть относительный путь"""
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Недопустимое расширение: {ext}. Разрешены: {settings.ALLOWED_EXTENSIONS}"
        )

    # Уникальное имя файла
    filename = f"listing_{listing_id}_{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(settings.UPLOAD_DIR, filename)

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    with open(filepath, "wb") as buffer:
        buffer.write(file.file.read())

    return f"/static/photos/{filename}"


@router.post("/upload/{listing_id}", response_model=PhotoResponse)
async def upload_photo(
    listing_id: int,
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Загрузить фото к объявлению"""
    listing = listing_crud.get(db, listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Объявление не найдено")
    if listing.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Нет доступа")

    # Проверка размера файла
    contents = await file.read()
    file_size = len(contents)
    await file.seek(0)  # сброс указателя для последующего чтения

    if file_size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Файл слишком большой. Максимум: {settings.MAX_UPLOAD_SIZE // (1024*1024)} МБ"
        )

    file_url = _save_file(file, listing_id)

    photo = photo_crud.create(db, {
        "listing_id": listing_id,
        "file_url": file_url,
        "title": title or file.filename,
        "file_size": file_size
    })

    return photo


@router.post("/upload/{listing_id}/multiple", response_model=List[PhotoResponse])
async def upload_multiple_photos(
    listing_id: int,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Загрузить несколько фото к объявлению"""
    listing = listing_crud.get(db, listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Объявление не найдено")
    if listing.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Нет доступа")

    photos = []
    for file in files:
        contents = await file.read()
        file_size = len(contents)
        await file.seek(0)

        if file_size > settings.MAX_UPLOAD_SIZE:
            continue  # пропускаем слишком большие

        file_url = _save_file(file, listing_id)

        photo = photo_crud.create(db, {
            "listing_id": listing_id,
            "file_url": file_url,
            "title": file.filename,
            "file_size": file_size
        })
        photos.append(photo)

    return photos


@router.delete("/{photo_id}")
async def delete_photo(
    photo_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Удалить фото"""
    photo = photo_crud.get(db, photo_id)
    if not photo:
        raise HTTPException(status_code=404, detail="Фото не найдено")

    # Проверка владельца через объявление
    listing = listing_crud.get(db, photo.listing_id)
    if listing and listing.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Нет доступа")

    # Удалить файл с диска
    filepath = os.path.join(settings.UPLOAD_DIR, os.path.basename(photo.file_url))
    if os.path.exists(filepath):
        os.remove(filepath)

    photo_crud.delete(db, photo_id)
    return {"message": "Фото удалено", "success": True}


@router.put("/{photo_id}/title")
async def update_photo_title(
    photo_id: int,
    title: str = Form(...),
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Обновить название фото"""
    photo = photo_crud.get(db, photo_id)
    if not photo:
        raise HTTPException(status_code=404, detail="Фото не найдено")

    listing = listing_crud.get(db, photo.listing_id)
    if listing and listing.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Нет доступа")

    photo = photo_crud.update(db, photo, {"title": title})
    return {"message": "Название обновлено", "success": True}