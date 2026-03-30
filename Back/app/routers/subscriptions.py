from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.common import MessageResponse

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])

@router.get("/user/{user_id}")
async def get_subscriptions(user_id: int, db: Session = Depends(get_db)):
    return []

@router.post("/")
async def create_subscription(db: Session = Depends(get_db)):
    return MessageResponse(message="Subscription created")

@router.delete("/{subscription_id}")
async def delete_subscription(subscription_id: int, db: Session = Depends(get_db)):
    return MessageResponse(message="Subscription deleted")