from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db

router = APIRouter(prefix="/public", tags=["public"])

@router.get("/market-overview")
async def get_market_overview(db: Session = Depends(get_db)):
    return {"message": "Market overview", "total_listings": 0}