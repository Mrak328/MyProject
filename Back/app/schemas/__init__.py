# User
from app.schemas.user import UserCreate, UserUpdate, UserResponse

# Listing
from app.schemas.listing import ListingCreate, ListingUpdate, ListingResponse

# Photo
from app.schemas.photo import PhotoCreate, PhotoResponse

# Review
from app.schemas.review import ReviewCreate, ReviewResponse

# Favorite
from app.schemas.favorite import FavoriteCreate, FavoriteResponse

# Analytics
from app.schemas.analytics import (
    DashboardResponse,
    PopularListingResponse,
    PriceStatsResponse,
    ViewsStatsResponse,
    SearchQueriesResponse,
    ClosedDealsResponse
)

# Common
from app.schemas.common import PaginatedResponse, MessageResponse, ErrorResponse

# Auth
from app.schemas.auth import Token, LoginRequest, TokenData

# Создаем алиасы для удобства
User = UserResponse
Listing = ListingResponse
Photo = PhotoResponse
Review = ReviewResponse
Favorite = FavoriteResponse

__all__ = [
    # User
    "User",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    # Listing
    "Listing",
    "ListingCreate",
    "ListingUpdate",
    "ListingResponse",
    # Photo
    "Photo",
    "PhotoCreate",
    "PhotoResponse",
    # Review
    "Review",
    "ReviewCreate",
    "ReviewResponse",
    # Favorite
    "Favorite",
    "FavoriteCreate",
    "FavoriteResponse",
    # Analytics
    "DashboardResponse",
    "PopularListingResponse",
    "PriceStatsResponse",
    "ViewsStatsResponse",
    "SearchQueriesResponse",
    "ClosedDealsResponse",
    # Common
    "PaginatedResponse",
    "MessageResponse",
    "ErrorResponse",
    # Auth
    "Token",
    "LoginRequest",
    "TokenData"
]