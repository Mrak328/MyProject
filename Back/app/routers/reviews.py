from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.crud.review import review_crud
from app.schemas.review import ReviewCreate, ReviewResponse
from app.schemas.common import MessageResponse

router = APIRouter(prefix="/reviews", tags=["reviews"])

@router.get("/user/{user_id}", response_model=List[ReviewResponse])
async def get_user_reviews(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    reviews = review_crud.get_by_user(db, user_id)[skip:skip+limit]
    return reviews  # SQLAlchemy автоматически преобразует в ReviewResponse

@router.get("/listing/{listing_id}", response_model=List[ReviewResponse])
async def get_listing_reviews(
    listing_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    reviews = review_crud.get_by_listing(db, listing_id)[skip:skip+limit]
    return reviews

@router.post("/", response_model=ReviewResponse)
async def create_review(review: ReviewCreate, db: Session = Depends(get_db)):
    result = review_crud.create(db, review)
    review_crud.update_user_rating(db, review.user_id)
    return result

@router.delete("/{review_id}", response_model=MessageResponse)
async def delete_review(review_id: int, db: Session = Depends(get_db)):
    review = review_crud.get(db, id=review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    user_id = review.user_id
    review_crud.delete(db, id=review_id)
    review_crud.update_user_rating(db, user_id)
    return MessageResponse(message="Review deleted")