from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.crud.review import review_crud
from app.crud.listing import listing_crud
from app.crud.action_log import action_log_crud
from app.schemas.review import ReviewCreate, ReviewResponse
from app.schemas.common import MessageResponse
from app.core.dependencies import get_current_user
from app.models import Users

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.get("/user/{user_id}", response_model=List[ReviewResponse])
async def get_user_reviews(user_id: int, skip: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=100), db: Session = Depends(get_db)):
    return review_crud.get_by_user(db, user_id)[skip:skip + limit]


@router.get("/listing/{listing_id}", response_model=List[ReviewResponse])
async def get_listing_reviews(listing_id: int, skip: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=100), db: Session = Depends(get_db)):
    return review_crud.get_by_listing(db, listing_id)[skip:skip + limit]


@router.get("/my", response_model=List[ReviewResponse])
async def get_my_reviews(skip: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=100), db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    return review_crud.get_by_author(db, current_user.user_id)[skip:skip + limit]


@router.get("/about-me", response_model=List[ReviewResponse])
async def get_reviews_about_me(skip: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=100), db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    return review_crud.get_by_user(db, current_user.user_id)[skip:skip + limit]


@router.post("/", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(review_data: ReviewCreate, db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    if review_data.user_id == current_user.user_id: raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Нельзя оставить отзыв самому себе")
    if review_data.listing_id:
        listing = listing_crud.get(db, review_data.listing_id)
        if not listing: raise HTTPException(status_code=404, detail="Объявление не найдено")
        if listing.user_id == current_user.user_id: raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Нельзя оставить отзыв на своё объявление")
        existing = review_crud.get_by_author_and_listing(db, current_user.user_id, review_data.listing_id)
        if existing: raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Вы уже оставили отзыв на это объявление")
    result = review_crud.create(db, {"author_id": current_user.user_id, "user_id": review_data.user_id, "listing_id": review_data.listing_id, "content": review_data.content})
    action_log_crud.log(db, current_user.user_id, 5, listing_id=review_data.listing_id, details={"review_id": result.review_id})
    return result


@router.put("/{review_id}", response_model=ReviewResponse)
async def update_review(review_id: int, review_data: ReviewCreate, db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    review = review_crud.get(db, review_id)
    if not review: raise HTTPException(status_code=404, detail="Отзыв не найден")
    if review.author_id != current_user.user_id: raise HTTPException(status_code=403, detail="Нет доступа")
    return review_crud.update(db, review, {"content": review_data.content, "user_id": review_data.user_id, "listing_id": review_data.listing_id})


@router.delete("/{review_id}", response_model=MessageResponse)
async def delete_review(review_id: int, db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    review = review_crud.get(db, review_id)
    if not review: raise HTTPException(status_code=404, detail="Отзыв не найден")
    if review.author_id != current_user.user_id: raise HTTPException(status_code=403, detail="Нет доступа")
    review_crud.delete(db, review_id)
    return {"message": "Отзыв удалён", "success": True}