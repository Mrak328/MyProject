from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.crud.comment import comment_crud
from app.crud.user import user_crud
from app.crud.action_log import action_log_crud
from app.schemas.comment import CommentCreate, CommentResponse
from app.schemas.common import MessageResponse
from app.core.dependencies import get_current_user
from app.models import Users, Comment

router = APIRouter(prefix="/comments", tags=["comments"])


@router.get("/profile/{user_id}", response_model=List[CommentResponse])
async def get_profile_comments(user_id: int, db: Session = Depends(get_db)):
    comments = comment_crud.get_by_profile(db, user_id)
    result = []
    for c in comments:
        author = user_crud.get(db, c.author_id)
        result.append({
            "comment_id": c.comment_id,
            "author_id": c.author_id,
            "profile_user_id": c.profile_user_id,
            "content": c.content,
            "created_date": c.created_date,
            "author_name": author.first_name if author else None
        })
    return result


@router.post("/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    if data.profile_user_id == current_user.user_id:
        raise HTTPException(status_code=400, detail="Нельзя комментировать самого себя")

    profile = user_crud.get(db, data.profile_user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    result = comment_crud.create(db, {
        "author_id": current_user.user_id,
        "profile_user_id": data.profile_user_id,
        "content": data.content
    })
    action_log_crud.log(db, current_user.user_id, 6, details={"comment_id": result.comment_id})
    return result


@router.delete("/{comment_id}", response_model=MessageResponse)
async def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    comment = comment_crud.get(db, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Комментарий не найден")
    if comment.author_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Нет доступа")
    comment_crud.delete(db, comment_id)
    return {"message": "Комментарий удалён", "success": True}