from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.crud.user import user_crud
from app.schemas.auth import LoginRequest, Token
from app.schemas.user import UserCreate, UserResponse
from app.services.auth import auth_service
from app.core.config import settings
from app.core.dependencies import get_current_user
from app.models import Users

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Вход по email ИЛИ телефону + пароль"""

    # 1. Найти пользователя по email ИЛИ телефону
    user = user_crud.get_by_email_or_phone(db, request.email_or_phone)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email/phone or password")

    # 2. Проверить пароль
    if not auth_service.verify_password(request.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email/phone or password")

    # 3. Создать токен
    access_token = auth_service.create_access_token(
        data={"sub": str(user.user_id)}
    )

    return Token(
        access_token=access_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/register", response_model=Token)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Регистрация нового пользователя"""

    # Проверка email
    if user_data.email:
        existing = user_crud.get_by_email(db, user_data.email)
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

    # Проверка телефона
    if user_data.phone_number:
        existing_phone = user_crud.get_by_phone(db, user_data.phone_number)
        if existing_phone:
            raise HTTPException(status_code=400, detail="Phone already registered")

    # Хешируем пароль
    hashed_password = auth_service.hash_password(user_data.password)

    # Создаем пользователя
    user_create = UserCreate(
        first_name=user_data.first_name,
        phone_number=user_data.phone_number,
        email=user_data.email,
        password=hashed_password
    )
    new_user = user_crud.create(db, user_create)

    # Создаем токен
    access_token = auth_service.create_access_token(
        data={"sub": str(new_user.user_id)}
    )

    return Token(
        access_token=access_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
        current_user: Users = Depends(get_current_user)
):
    """Получить информацию о текущем пользователе"""
    return current_user