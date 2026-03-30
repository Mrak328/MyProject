from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.core.config import settings
from app.database import engine, Base  # ←
from app.models import *


app = FastAPI(
    title="Недвижимость API",
    description="API для сайта недвижимости",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Статика
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Импортируем роутеры
from app.routers.users import router as users_router
from app.routers.listings import router as listings_router
from app.routers.photos import router as photos_router
from app.routers.reviews import router as reviews_router
from app.routers.favorites import router as favorites_router
from app.routers.analytics import router as analytics_router
from app.routers.auth import router as auth_router
from app.routers.public import router as public_router
from app.routers.subscriptions import router as subscriptions_router

# Подключаем роутеры
app.include_router(users_router, prefix="/api")
app.include_router(listings_router, prefix="/api")
app.include_router(photos_router, prefix="/api")
app.include_router(reviews_router, prefix="/api")
app.include_router(favorites_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(public_router, prefix="/api")
app.include_router(subscriptions_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Недвижимость API", "docs": "/docs"}