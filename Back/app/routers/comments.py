from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.crud.comment import comment_crud
from app.crud.review import review_crud
from app.crud.action_log import action_log_crud
from app.schemas.comment import CommentCreate, CommentResponse
from app.schemas.common import MessageResponse
from app.core.dependencies import get_current_user
from app.models import Users

router = APIRouter(prefix="/comments", tags=["comments"])


@router.get("/review/{review_id}", response_model=List[CommentResponse])
async def get_comments(review_id: int, db: Session = Depends(get_db)):
    return comment_crud.get_by_review(db, review_id)


@router.post("/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(data: CommentCreate, db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    review = review_crud.get(db, data.review_id)
    if not review: raise HTTPException(status_code=404, detail="Отзыв не найден")
    result = comment_crud.create(db, {"review_id": data.review_id, "user_id": current_user.user_id, "content": data.content})
    action_log_crud.log(db, current_user.user_id, 6, details={"comment_id": result.comment_id, "review_id": data.review_id})
    return result


@router.delete("/{comment_id}", response_model=MessageResponse)
async def delete_comment(comment_id: int, db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    comment = comment_crud.get(db, comment_id)
    if not comment: raise HTTPException(status_code=404, detail="Комментарий не найден")
    if comment.user_id != current_user.user_id: raise HTTPException(status_code=403, detail="Нет доступа")
    comment_crud.delete(db, comment_id)
    return {"message": "Комментарий удалён", "success": True}