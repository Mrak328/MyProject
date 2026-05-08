from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.crud.user import user_crud
from app.crud.action_log import action_log_crud
from app.schemas.auth import LoginRequest, Token
from app.schemas.user import UserCreate, UserResponse
from app.services.auth import auth_service
from app.core.config import settings
from app.core.dependencies import get_current_user
from app.models import Users

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
async def login(request: LoginRequest, req: Request, db: Session = Depends(get_db)):
    user = user_crud.get_by_email_or_phone(db, request.email_or_phone)
    if not user or not auth_service.verify_password(request.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный email/телефон или пароль")

    access_token = auth_service.create_access_token(data={"sub": str(user.user_id), "role_id": user.role_id})

    action_log_crud.log(db, user.user_id, 10, ip_address=req.client.host, user_agent=req.headers.get("user-agent"))
    user_crud.update_last_activity(db, user.user_id)

    return Token(access_token=access_token, expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, req: Request, db: Session = Depends(get_db)):
    if user_crud.is_phone_taken(db, user_data.phone_number):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Телефон уже зарегистрирован")
    if user_data.email and user_crud.is_email_taken(db, user_data.email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email уже зарегистрирован")

    hashed_password = auth_service.hash_password(user_data.password)
    new_user = user_crud.create(db, {
        "first_name": user_data.first_name,
        "phone_number": user_data.phone_number,
        "email": user_data.email,
        "password": hashed_password,
        "role_id": user_data.role_id
    })

    action_log_crud.log(db, new_user.user_id, 9, ip_address=req.client.host, user_agent=req.headers.get("user-agent"))

    return new_user


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: Users = Depends(get_current_user)):
    return current_user


@router.post("/logout")
async def logout(current_user: Users = Depends(get_current_user)):
    return {"message": "Logged out successfully"}