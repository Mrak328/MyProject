from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import users, listings, analytics, public, favorites, subscriptions

app = FastAPI(
    title="Недвижимость API",
    description="Поиск и просмотр объявлений о продаже/аренде недвижимости",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Роутеры
app.include_router(users.router, prefix="/api/users", tags=["Пользователи"])
app.include_router(listings.router, prefix="/api/listings", tags=["Объявления"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(public.router, prefix="/api", tags=["Публичная статистика"])
app.include_router(favorites.router, prefix="/api", tags=["Избранное"])
app.include_router(subscriptions.router, prefix="/api", tags=["Подписки"])

@app.get("/")
async def root():
    return {
        "name": "Недвижимость API",
        "description": "Поиск объявлений о продаже и аренде недвижимости",
        "endpoints": {
            "Поиск": "/api/listings/?city=москва&deal_type=sale",
            "Объявление": "/api/listings/123",
            "Продавец": "/api/users/123",
            "Статистика": "/api/public/market-overview?city=москва"
        }
    }