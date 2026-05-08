from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import date, datetime
from decimal import Decimal


# ============================================
# 1. DASHBOARD — главная страница аналитики
# ============================================

class DashboardResponse(BaseModel):
    total_listings: int
    active_today: int
    views_today: int
    new_listings_today: int

    # Дополнительные показатели
    total_users: int = 0
    new_users_today: int = 0
    searches_today: int = 0

    class Config:
        from_attributes = True


# ============================================
# 2. ПОПУЛЯРНЫЕ ОБЪЯВЛЕНИЯ
# ============================================

class PopularListingResponse(BaseModel):
    listing_id: int
    title: str
    price: Decimal
    address: Optional[str] = None  # собирается через JOIN: город, улица, дом
    views: int
    photo: Optional[str] = None  # первый url из photo

    # Аналитические метрики
    favorites_count: int = 0
    contacts_opened: int = 0
    ctr: Optional[float] = None  # (contacts_opened / views) * 100

    class Config:
        from_attributes = True


# ============================================
# 3. ЦЕНОВАЯ АНАЛИТИКА
# ============================================

class PriceByTypeItem(BaseModel):
    property_type: str
    deal_type: Optional[str] = None
    count: int
    avg_price: float
    avg_price_per_m2: Optional[float] = None
    min_price: float
    max_price: float
    median_price: Optional[float] = None


class PriceByCityItem(BaseModel):
    city: str
    count: int
    avg_price: float
    avg_price_per_m2: Optional[float] = None


class PriceByRoomsItem(BaseModel):
    rooms: int
    count: int
    avg_price: float


class PriceStatsResponse(BaseModel):
    total_active: int
    avg_price: float
    avg_price_per_m2: Optional[float] = None
    median_price: Optional[float] = None
    min_price: float
    max_price: float

    # Распределение по диапазонам
    price_ranges: Dict[str, int]  # {"0-1M": 150, "1M-3M": 320, ...}

    # Срезы
    by_property_type: List[PriceByTypeItem] = []
    by_deal_type: List[PriceByTypeItem] = []
    by_city: List[PriceByCityItem] = []
    by_rooms: List[PriceByRoomsItem] = []

    class Config:
        from_attributes = True


# ============================================
# 4. АНАЛИТИКА ПРОСМОТРОВ
# ============================================

class ViewsByDayItem(BaseModel):
    date: date
    views: int
    unique_visitors: int
    unique_listings: int = 0


class ViewsBySourceItem(BaseModel):
    source: str
    views: int
    percentage: float


class ViewsByDeviceItem(BaseModel):
    device: str
    views: int
    percentage: float


class ViewsStatsResponse(BaseModel):
    period: str  # "7d", "30d", "month", "quarter"
    date_from: date
    date_to: date

    # Основные метрики
    total_views: int
    unique_listings: int
    unique_visitors: int
    avg_view_depth_seconds: Optional[float] = None

    # Детализация
    views_by_day: List[ViewsByDayItem] = []
    views_by_source: List[ViewsBySourceItem] = []
    views_by_device: List[ViewsByDeviceItem] = []

    # Конверсии
    contacts_opened: int = 0
    conversion_rate: Optional[float] = None  # contacts_opened / total_views

    class Config:
        from_attributes = True


# ============================================
# 5. ПОИСКОВЫЕ ЗАПРОСЫ
# ============================================

class PopularQueryItem(BaseModel):
    query: str
    count: int
    avg_results: Optional[float] = None
    conversion_to_view: Optional[float] = None  # доля запросов, где было выбрано объявление


class SearchQueriesResponse(BaseModel):
    period: str
    total_searches: int
    unique_users: int = 0
    avg_execution_time_seconds: Optional[float] = None

    popular_queries: List[PopularQueryItem] = []

    # Доля пустых результатов
    empty_results_count: int = 0
    empty_results_percentage: Optional[float] = None

    class Config:
        from_attributes = True


# ============================================
# 6. ЗАКРЫТЫЕ СДЕЛКИ
#    (на основе объявлений в статусах «продано»/«сдано»)
# ============================================

class ClosedDealByTypeItem(BaseModel):
    property_type: str
    deal_type: Optional[str] = None
    count: int
    total_revenue: float
    avg_price: float
    avg_days_to_close: Optional[float] = None  # от publication_date до update_date


class ClosedDealByMonthItem(BaseModel):
    month: str  # "2025-01"
    count: int
    total_revenue: float


class ClosedDealsResponse(BaseModel):
    period: str
    date_from: date
    date_to: date

    total_closed: int
    total_revenue: float
    avg_price: float
    avg_days_to_close: Optional[float] = None

    by_type: List[ClosedDealByTypeItem] = []
    by_month: List[ClosedDealByMonthItem] = []

    class Config:
        from_attributes = True


# ============================================
# 7. ПОЛЬЗОВАТЕЛЬСКАЯ АКТИВНОСТЬ
# ============================================

class UserActivityByDayItem(BaseModel):
    date: date
    active_users: int
    new_registrations: int
    avg_session_minutes: Optional[float] = None


class UserActivityResponse(BaseModel):
    period: str

    # Основные метрики
    total_active_users: int
    new_registrations: int
    avg_session_duration_minutes: Optional[float] = None

    # По дням
    activity_by_day: List[UserActivityByDayItem] = []

    # По устройствам
    by_device: Dict[str, int] = {}  # {"mobile": 450, "desktop": 230, "tablet": 45}

    class Config:
        from_attributes = True


# ============================================
# 8. ЭФФЕКТИВНОСТЬ ОБЪЯВЛЕНИЙ (Listing Performance)
# ============================================

class ListingPerformanceItem(BaseModel):
    listing_id: int
    title: str
    publication_date: Optional[datetime] = None

    # Метрики
    total_views: int
    unique_views: int
    contacts_opened: int
    favorites_added: int

    # Расчётные
    ctr: Optional[float] = None  # contacts_opened / total_views
    favorites_rate: Optional[float] = None  # favorites_added / unique_views


class ListingPerformanceResponse(BaseModel):
    period: str
    total_listings_analyzed: int
    avg_ctr: Optional[float] = None
    avg_favorites_rate: Optional[float] = None

    top_performers: List[ListingPerformanceItem] = []  # топ-10 по просмотрам
    worst_performers: List[ListingPerformanceItem] = []  # худшие-10

    class Config:
        from_attributes = True


# ============================================
# 9. ЖАЛОБЫ И НАРУШЕНИЯ
# ============================================

class ComplaintsStatsResponse(BaseModel):
    period: str

    total_complaints: int
    resolved: int
    pending: int

    by_type: Dict[str, int] = {}  # {"spam": 12, "fake": 8, ...}

    avg_resolution_hours: Optional[float] = None

    class Config:
        from_attributes = True


# ============================================
# 10. СВОДНЫЙ ОТЧЁТ (полная выгрузка за период)
# ============================================

class SummaryReportResponse(BaseModel):
    period: str
    date_from: date
    date_to: date

    # Объявления
    new_listings: int
    total_active_listings: int
    closed_listings: int

    # Просмотры
    total_views: int
    unique_visitors: int

    # Поиск
    total_searches: int

    # Пользователи
    new_users: int
    active_users: int

    # Сделки
    total_closed_deals: int
    total_revenue: float

    # Жалобы
    complaints_filed: int

    class Config:
        from_attributes = True