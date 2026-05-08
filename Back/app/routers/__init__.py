from .auth import router as auth_router
from .users import router as users_router
from .listings import router as listings_router
from .photos import router as photos_router
from .favorites import router as favorites_router
from .reviews import router as reviews_router
from .complaints import router as complaints_router
from .admin import router as admin_router
from .moderation import router as moderation_router
from .analytics import router as analytics_router
from .chat import router as chat_router
from .agent import router as agent_router
from .search import router as search_router
from .geography import router as geography_router
from .public import router as public_router
from .comments import router as comments_router
from .activity import router as activity_router

routers = [
    auth_router,
    users_router,
    listings_router,
    photos_router,
    favorites_router,
    reviews_router,
    complaints_router,
    chat_router,
    agent_router,
    search_router,
    geography_router,
    public_router,
    analytics_router,
    moderation_router,
    admin_router,
    comments_router,
    activity_router,
]