from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.crud.agent import agent_crud
from app.schemas.agent import AgentProfileCreate, AgentProfileUpdate, AgentProfileResponse
from app.schemas.common import MessageResponse
from app.core.dependencies import get_current_user
from app.models import Users

router = APIRouter(prefix="/agents", tags=["agents"])


@router.get("/", response_model=List[AgentProfileResponse])
async def get_agents(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Список агентов"""
    return agent_crud.get_active_agents(db, skip, limit)


@router.get("/{agent_id}", response_model=AgentProfileResponse)
async def get_agent(agent_id: int, db: Session = Depends(get_db)):
    """Профиль агента"""
    agent = agent_crud.get(db, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Агент не найден")
    return agent


@router.post("/", response_model=AgentProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_agent_profile(
    data: AgentProfileCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Стать агентом"""
    existing = agent_crud.get_by_user(db, current_user.user_id)
    if existing:
        raise HTTPException(status_code=409, detail="Профиль агента уже существует")

    return agent_crud.create(db, {
        "user_id": current_user.user_id,
        "company_name": data.company_name,
        "license_number": data.license_number,
        "about": data.about
    })


@router.put("/me", response_model=AgentProfileResponse)
async def update_my_agent_profile(
    data: AgentProfileUpdate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Обновить свой профиль агента"""
    agent = agent_crud.get_by_user(db, current_user.user_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Профиль агента не найден")

    return agent_crud.update(db, agent, data)