from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.crud.action_log import action_log_crud
from app.core.dependencies import get_current_admin
from app.models import Users
from app.models import ActionLog
from sqlalchemy import desc

router = APIRouter(prefix="/activity", tags=["activity"])

@router.get("/user/{user_id}")
async def get_user_activity(user_id: int, skip: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=200), db: Session = Depends(get_db), _: Users = Depends(get_current_admin)):
    logs = action_log_crud.get_by_user(db, user_id, skip, limit)
    return [{"log_id": l.log_id,
             "action_type_id": l.action_type_id,
             "listing_id": l.listing_id, "ip_address": l.ip_address,
             "user_agent": l.user_agent,
             "action_datetime": l.action_datetime,
             "details": l.details} for l in logs]

@router.get("/all")
async def get_all_activity(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    _: Users = Depends(get_current_admin)
):
    logs = db.query(ActionLog).order_by(desc(ActionLog.action_datetime)).offset(skip).limit(limit).all()
    return [
        {
            "log_id": l.log_id,
            "user_id": l.user_id,
            "action_type_id": l.action_type_id,
            "listing_id": l.listing_id,
            "ip_address": l.ip_address,
            "user_agent": l.user_agent,
            "action_datetime": l.action_datetime.isoformat() if l.action_datetime else None,
            "details": l.details
        }
        for l in logs
    ]