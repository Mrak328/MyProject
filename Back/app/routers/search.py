from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.crud.search import search_request_crud, search_history_crud
from app.schemas.search_request import SearchRequestCreate, SearchRequestResponse
from app.schemas.common import MessageResponse
from app.core.dependencies import get_current_user
from app.models import Users

router = APIRouter(prefix="/search-requests", tags=["search-requests"])


@router.get("/", response_model=List[SearchRequestResponse])
async def get_my_requests(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Мои запросы на подбор"""
    return search_request_crud.get_by_user(db, current_user.user_id, skip, limit)


@router.post("/", response_model=SearchRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_request(
    data: SearchRequestCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Создать запрос на подбор (для агентов)"""
    return search_request_crud.create(db, {
        **data.dict(),
        "user_id": current_user.user_id
    })


@router.delete("/{request_id}", response_model=MessageResponse)
async def delete_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Удалить запрос на подбор"""
    req = search_request_crud.get(db, request_id)
    if not req:
        raise HTTPException(status_code=404, detail="Запрос не найден")
    if req.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Нет доступа")

    search_request_crud.delete(db, request_id)
    return {"message": "Запрос удалён", "success": True}


@router.get("/history", response_model=List[dict])
async def get_search_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """История поиска"""
    history = search_history_crud.get_by_user(db, current_user.user_id, skip, limit)
    return [
        {
            "history_id": h.history_id,
            "search_query": h.search_query,
            "filter_parameters": h.filter_parameters,
            "search_date": h.search_date,
            "results_count": h.results_count
        }
        for h in history
    ]


@router.delete("/history", response_model=MessageResponse)
async def clear_search_history(
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Очистить историю поиска"""
    deleted = search_history_crud.clear(db, current_user.user_id)
    return {"message": f"История очищена, удалено записей: {deleted}", "success": True}