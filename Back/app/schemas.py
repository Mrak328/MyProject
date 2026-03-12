from pydantic import BaseModel, Field
from datetime import datetime, date, time
from decimal import Decimal
from typing import Optional, List


# Role schemas
class RoleBase(BaseModel):
    name: str
    role_code: Optional[str] = None
    description: Optional[str] = None


class RoleCreate(RoleBase):
    pass


class Role(RoleBase):
    role_id: int

    class Config:
        from_attributes = True


# User schemas
class UserBase(BaseModel):
    first_name: str
    phone_number: str
    email: Optional[str] = None
    role_id: int = 3


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    email: Optional[str] = None
    phone_confirmed: Optional[bool] = None
    email_confirmed: Optional[bool] = None
    status: Optional[str] = None
    avatar_url: Optional[str] = None


class User(UserBase):
    user_id: int
    registration_date: datetime
    last_activity: Optional[datetime] = None
    phone_confirmed: bool
    email_confirmed: bool
    rating: Decimal
    reviews_count: int
    status: str
    avatar_url: Optional[str] = None

    class Config:
        from_attributes = True


# Listing schemas
class ListingBase(BaseModel):
    title: str
    description: Optional[str] = None
    property_type_id: int
    deal_type_id: int
    address: str
    price: Decimal
    currency: str = "RUB"
    total_area: Optional[Decimal] = None
    renovation_condition_id: Optional[int] = None
    utilities_included: bool = False
    deposit: Optional[Decimal] = None
    mortgage_available: bool = False
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None


class ListingCreate(ListingBase):
    user_id: int


class ListingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    listing_status_id: Optional[int] = None
    update_date: datetime = Field(default_factory=datetime.now)


class Listing(ListingBase):
    listing_id: int
    user_id: int
    listing_status_id: int
    publication_date: datetime
    update_date: datetime
    expiration_date: Optional[datetime] = None
    views: int
    moderated: bool
    moderator_id: Optional[int] = None
    moderation_date: Optional[datetime] = None

    class Config:
        from_attributes = True


class ListingDetail(Listing):
    photos: List[Photo] = []

    class Config:
        from_attributes = True

# Photo schemas
class PhotoBase(BaseModel):
    file_url: str
    title: Optional[str] = None
    file_size: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None


class PhotoCreate(PhotoBase):
    listing_id: int


class Photo(PhotoBase):
    photo_id: int
    listing_id: int
    upload_date: datetime

    class Config:
        from_attributes = True


# Review schemas
class ReviewBase(BaseModel):
    rating: int = Field(ge=1, le=5)
    content: Optional[str] = None


class ReviewCreate(ReviewBase):
    author_id: int
    user_id: int
    listing_id: Optional[int] = None


class Review(ReviewBase):
    review_id: int
    author_id: int
    user_id: int
    listing_id: Optional[int] = None
    created_date: datetime

    class Config:
        from_attributes = True


# Favorite schemas
class FavoriteBase(BaseModel):
    note: Optional[str] = None


class FavoriteCreate(FavoriteBase):
    user_id: int
    listing_id: int


class Favorite(FavoriteBase):
    favorite_id: int
    user_id: int
    listing_id: int
    added_date: datetime

    class Config:
        from_attributes = True


# Analytics schemas
class SalesAnalytics(BaseModel):
    total_listings: int
    active_listings: int
    sold_listings: int
    total_revenue: Decimal
    average_price: float
    average_days_on_market: float
    conversion_rate: float


class ListingPerformanceSchema(BaseModel):
    listing_id: int
    title: str
    total_views: int
    unique_views: int
    contacts_opened: int
    favorites_added: int
    ctr: float
    conversion_rate: float
    calculation_date: date


class DailyStats(BaseModel):
    date: date
    views: int
    unique_visitors: int
    listings_added: int
    conversions: int
    revenue: Decimal


class PriceAnalytics(BaseModel):
    property_type: str
    avg_price: float
    min_price: float
    max_price: float
    median_price: float
    listings_count: int


class UserActivitySchema(BaseModel):
    user_id: int
    user_name: str
    total_sessions: int
    avg_session_duration: float
    total_searches: int
    total_views: int
    last_activity: Optional[datetime]


class SearchAnalytics(BaseModel):
    popular_queries: List[dict]
    avg_results_count: float
    avg_search_time: float
    filters_usage: dict


# Response schemas
class DashboardSummary(BaseModel):
    total_users: int
    active_listings: int
    today_views: int
    today_conversions: int
    total_revenue: Decimal
    recent_activities: List[dict]
    top_performing_listings: List[ListingPerformanceSchema]

# Для поиска
class SearchFilters(BaseModel):
    deal_type: Optional[str] = None
    property_type: Optional[str] = None
    rooms: Optional[int] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    min_area: Optional[float] = None
    max_area: Optional[float] = None
    city: Optional[str] = None
    district: Optional[str] = None
    metro: Optional[str] = None

# Для подписок
class SubscriptionCreate(BaseModel):
    user_id: int
    name: str
    filters: SearchFilters
    email_notifications: bool = True

# Для контактов
class ContactInfo(BaseModel):
    phone: str
    person: Optional[str] = None
    show_phone: bool = True


# Для поиска
class SearchFilters(BaseModel):
    deal_type: Optional[str] = None
    property_type: Optional[str] = None
    rooms: Optional[int] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    min_area: Optional[float] = None
    max_area: Optional[float] = None
    city: Optional[str] = None
    district: Optional[str] = None
    metro: Optional[str] = None


# Для подписок
class SubscriptionBase(BaseModel):
    name: str
    filters: SearchFilters
    email_notifications: bool = True


class SubscriptionCreate(SubscriptionBase):
    user_id: int


class SearchSubscription(SubscriptionBase):
    subscription_id: int
    user_id: int
    created_date: datetime
    last_sent_date: Optional[datetime] = None
    active: bool = True

    class Config:
        from_attributes = True


# Для контактов
class ContactInfo(BaseModel):
    phone: str
    person: Optional[str] = None
    show_phone: bool = True


# Для просмотров
class ViewCreate(BaseModel):
    user_id: Optional[int] = None
    ip_address: Optional[str] = None
    device: Optional[str] = None


# Для отзывов
class ReviewCreate(BaseModel):
    author_id: int
    user_id: int
    rating: int = Field(ge=1, le=5)
    content: Optional[str] = None


# Для статистики района
class DistrictStats(BaseModel):
    district: str
    total_listings: int
    avg_price: float
    avg_price_per_m2: float
    min_price: float
    max_price: float
    popular_property_types: List[dict]


# Для динамики цен
class PriceTrend(BaseModel):
    month: str
    avg_price: float
    listings_count: int
    change_percent: float