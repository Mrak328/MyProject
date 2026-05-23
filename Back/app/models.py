from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, DECIMAL, JSON, Time, Date
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime


# ============================================
# 0. СПРАВОЧНИКИ
# ============================================

class PropertyType(Base):
    __tablename__ = "property_type"
    property_type_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    listings = relationship("Listing", back_populates="property_type")


class DealType(Base):
    __tablename__ = "deal_type"
    deal_type_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    listings = relationship("Listing", back_populates="deal_type")


class ListingStatus(Base):
    __tablename__ = "listing_status"
    listing_status_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(30), nullable=False)
    listings = relationship("Listing", back_populates="listing_status")


class RenovationCondition(Base):
    __tablename__ = "renovation_condition"
    renovation_condition_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    listings = relationship("Listing", back_populates="renovation_condition")


class ComplaintType(Base):
    __tablename__ = "complaint_type"
    complaint_type_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    complaints = relationship("Complaint", back_populates="complaint_type")


class ViolationType(Base):
    __tablename__ = "violation_type"
    violation_type_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    violations = relationship("BlocksAndViolations", back_populates="violation_type")


class DeviceType(Base):
    __tablename__ = "device_type"
    device_type_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    view_statistics = relationship("ListingViewStatistics", back_populates="device_type")
    user_activities = relationship("UserActivity", back_populates="device_type")


class BrowserType(Base):
    __tablename__ = "browser_type"
    browser_type_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    view_statistics = relationship("ListingViewStatistics", back_populates="browser_type")


class SourceType(Base):
    __tablename__ = "source_type"
    source_type_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    view_statistics = relationship("ListingViewStatistics", back_populates="source_type")


class ActionType(Base):
    __tablename__ = "action_type"
    action_type_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    action_logs = relationship("ActionLog", back_populates="action_type")


class MarketType(Base):
    __tablename__ = "market_type"
    market_type_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    listings = relationship("Listing", back_populates="market_type")


class BlockStatus(Base):
    __tablename__ = "block_status"
    block_status_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    blocks = relationship("BlocksAndViolations", back_populates="block_status")


# ============================================
# 1. ПОЛЬЗОВАТЕЛИ И РОЛИ
# ============================================

class Role(Base):
    __tablename__ = "role"
    role_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    users = relationship("Users", back_populates="role")


class Users(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    password = Column(String(256), nullable=False)
    phone_number = Column(String(20), unique=True, nullable=False)
    email = Column(String(100), unique=True)
    role_id = Column(Integer, ForeignKey("role.role_id"), default=3)
    registration_date = Column(DateTime, default=datetime.now)
    last_activity = Column(DateTime)
    avatar_url = Column(String(500))

    role = relationship("Role", back_populates="users")
    listings = relationship("Listing", back_populates="user")
    favorites = relationship("Favorite", back_populates="user")

    # Comments
    comments_authored = relationship("Comment", back_populates="author", foreign_keys="Comment.author_id")
    comments_received = relationship("Comment", back_populates="profile_user", foreign_keys="Comment.profile_user_id")

    # Complaints
    complaints_filed = relationship("Complaint", back_populates="complainant", foreign_keys="Complaint.complainant_user_id")
    complaints_against = relationship("Complaint", back_populates="violator", foreign_keys="Complaint.violator_user_id")
    moderated_complaints = relationship("Complaint", back_populates="moderator", foreign_keys="Complaint.moderator_id")

    # Agent
    agent_profile = relationship("AgentProfile", back_populates="user", uselist=False)
    chats_as_user = relationship("Chat", back_populates="user", foreign_keys="Chat.user_id")
    messages = relationship("Message", back_populates="sender")
    search_requests = relationship("SearchRequest", back_populates="user")

    # Statistics
    view_statistics = relationship("ListingViewStatistics", back_populates="user")
    search_statistics = relationship("SearchStatistics", back_populates="user")
    user_activities = relationship("UserActivity", back_populates="user")
    action_logs = relationship("ActionLog", back_populates="user")
    violations = relationship("BlocksAndViolations", back_populates="user", foreign_keys="BlocksAndViolations.user_id")
    moderated_violations = relationship("BlocksAndViolations", back_populates="blocked_by_admin_user", foreign_keys="BlocksAndViolations.blocked_by_admin")
    search_history = relationship("SearchHistory", back_populates="user")


# ============================================
# 2. ГЕОГРАФИЯ
# ============================================

class Country(Base):
    __tablename__ = "country"
    country_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    regions = relationship("Region", back_populates="country")
    addresses = relationship("Address", back_populates="country")


class Region(Base):
    __tablename__ = "region"
    region_id = Column(Integer, primary_key=True, index=True)
    country_id = Column(Integer, ForeignKey("country.country_id"))
    name = Column(String(100), nullable=False)
    country = relationship("Country", back_populates="regions")
    cities = relationship("City", back_populates="region")
    addresses = relationship("Address", back_populates="region")


class City(Base):
    __tablename__ = "city"
    city_id = Column(Integer, primary_key=True, index=True)
    region_id = Column(Integer, ForeignKey("region.region_id"))
    name = Column(String(100), nullable=False)
    region = relationship("Region", back_populates="cities")
    districts = relationship("District", back_populates="city")
    streets = relationship("Street", back_populates="city")
    addresses = relationship("Address", back_populates="city")


class District(Base):
    __tablename__ = "district"
    district_id = Column(Integer, primary_key=True, index=True)
    city_id = Column(Integer, ForeignKey("city.city_id"))
    name = Column(String(100), nullable=False)
    city = relationship("City", back_populates="districts")
    streets = relationship("Street", back_populates="district")
    addresses = relationship("Address", back_populates="district")


class Street(Base):
    __tablename__ = "street"
    street_id = Column(Integer, primary_key=True, index=True)
    city_id = Column(Integer, ForeignKey("city.city_id"))
    district_id = Column(Integer, ForeignKey("district.district_id"))
    name = Column(String(200), nullable=False)
    city = relationship("City", back_populates="streets")
    district = relationship("District", back_populates="streets")
    houses = relationship("House", back_populates="street")
    addresses = relationship("Address", back_populates="street")


class House(Base):
    __tablename__ = "house"
    house_id = Column(Integer, primary_key=True, index=True)
    street_id = Column(Integer, ForeignKey("street.street_id"))
    number = Column(String(20), nullable=False)
    street = relationship("Street", back_populates="houses")
    apartments = relationship("Apartment", back_populates="house")
    addresses = relationship("Address", back_populates="house")


class Apartment(Base):
    __tablename__ = "apartment"
    apartment_id = Column(Integer, primary_key=True, index=True)
    house_id = Column(Integer, ForeignKey("house.house_id"))
    number = Column(String(20), nullable=False)
    house = relationship("House", back_populates="apartments")
    addresses = relationship("Address", back_populates="apartment")


class Address(Base):
    __tablename__ = "address"
    address_id = Column(Integer, primary_key=True, index=True)
    country_id = Column(Integer, ForeignKey("country.country_id"))
    region_id = Column(Integer, ForeignKey("region.region_id"))
    city_id = Column(Integer, ForeignKey("city.city_id"))
    district_id = Column(Integer, ForeignKey("district.district_id"))
    street_id = Column(Integer, ForeignKey("street.street_id"))
    house_id = Column(Integer, ForeignKey("house.house_id"))
    apartment_id = Column(Integer, ForeignKey("apartment.apartment_id"))
    country = relationship("Country", back_populates="addresses")
    region = relationship("Region", back_populates="addresses")
    city = relationship("City", back_populates="addresses")
    district = relationship("District", back_populates="addresses")
    street = relationship("Street", back_populates="addresses")
    house = relationship("House", back_populates="addresses")
    apartment = relationship("Apartment", back_populates="addresses")
    listings = relationship("Listing", back_populates="address")


# ============================================
# 3. ОБЪЯВЛЕНИЯ
# ============================================

class Listing(Base):
    __tablename__ = "listing"
    listing_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    address_id = Column(Integer, ForeignKey("address.address_id"))
    listing_status_id = Column(Integer, ForeignKey("listing_status.listing_status_id"), default=1)
    property_type_id = Column(Integer, ForeignKey("property_type.property_type_id"))
    deal_type_id = Column(Integer, ForeignKey("deal_type.deal_type_id"))
    renovation_condition_id = Column(Integer, ForeignKey("renovation_condition.renovation_condition_id"))
    title = Column(String(200), nullable=False)
    description = Column(Text)
    price = Column(DECIMAL(12, 2), nullable=False)
    total_area = Column(DECIMAL(10, 2))
    rooms = Column(Integer)
    floor = Column(Integer)
    max_floor = Column(Integer)
    views = Column(Integer, default=0)
    moderated = Column(Boolean, default=False)
    publication_date = Column(DateTime, default=datetime.now)
    update_date = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    contact_person = Column(String(100))
    contact_phone = Column(String(20))
    market_type_id = Column(Integer, ForeignKey("market_type.market_type_id"))
    developer_name = Column(String(200))

    user = relationship("Users", back_populates="listings")
    address = relationship("Address", back_populates="listings")
    listing_status = relationship("ListingStatus", back_populates="listings")
    property_type = relationship("PropertyType", back_populates="listings")
    deal_type = relationship("DealType", back_populates="listings")
    renovation_condition = relationship("RenovationCondition", back_populates="listings")
    market_type = relationship("MarketType", back_populates="listings")

    photos = relationship("Photo", back_populates="listing")
    favorites = relationship("Favorite", back_populates="listing")
    complaints = relationship("Complaint", back_populates="listing")

    view_statistics = relationship("ListingViewStatistics", back_populates="listing")
    search_appearances = relationship("SearchStatistics", back_populates="selected_listing")
    performance = relationship("ListingPerformance", back_populates="listing")
    action_logs = relationship("ActionLog", back_populates="listing")
    violations = relationship("BlocksAndViolations", back_populates="listing")


class Photo(Base):
    __tablename__ = "photo"
    photo_id = Column(Integer, primary_key=True, index=True)
    listing_id = Column(Integer, ForeignKey("listing.listing_id", ondelete="CASCADE"), nullable=False)
    file_url = Column(String(500), nullable=False)
    title = Column(String(200))
    upload_date = Column(DateTime, default=datetime.now)
    file_size = Column(Integer)
    width = Column(Integer)
    height = Column(Integer)
    listing = relationship("Listing", back_populates="photos")


# ============================================
# 4. ИЗБРАННОЕ И КОММЕНТАРИИ
# ============================================

class Favorite(Base):
    __tablename__ = "favorite"
    favorite_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    listing_id = Column(Integer, ForeignKey("listing.listing_id", ondelete="CASCADE"), nullable=False)
    added_date = Column(DateTime, default=datetime.now)
    user = relationship("Users", back_populates="favorites")
    listing = relationship("Listing", back_populates="favorites")


class Comment(Base):
    __tablename__ = "comment"
    comment_id = Column(Integer, primary_key=True, index=True)
    author_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    profile_user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    content = Column(String(500), nullable=False)
    created_date = Column(DateTime, default=datetime.now)

    author = relationship("Users", foreign_keys=[author_id], back_populates="comments_authored")
    profile_user = relationship("Users", foreign_keys=[profile_user_id], back_populates="comments_received")


# ============================================
# 5. ЖАЛОБЫ
# ============================================

class Complaint(Base):
    __tablename__ = "complaint"
    complaint_id = Column(Integer, primary_key=True, index=True)
    complainant_user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    listing_id = Column(Integer, ForeignKey("listing.listing_id"))
    violator_user_id = Column(Integer, ForeignKey("users.user_id"))
    complaint_type_id = Column(Integer, ForeignKey("complaint_type.complaint_type_id"))
    description = Column(String(500))
    created_date = Column(DateTime, default=datetime.now)
    processing_date = Column(DateTime)
    moderator_id = Column(Integer, ForeignKey("users.user_id"))
    resolution = Column(String(500))

    complainant = relationship("Users", back_populates="complaints_filed", foreign_keys=[complainant_user_id])
    violator = relationship("Users", back_populates="complaints_against", foreign_keys=[violator_user_id])
    moderator = relationship("Users", back_populates="moderated_complaints", foreign_keys=[moderator_id])
    listing = relationship("Listing", back_populates="complaints")
    complaint_type = relationship("ComplaintType", back_populates="complaints")


# ============================================
# 6. АГЕНТЫ И ЧАТЫ
# ============================================

class AgentProfile(Base):
    __tablename__ = "agent_profile"
    agent_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), unique=True, nullable=False)
    company_name = Column(String(200))
    license_number = Column(String(50))
    about = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    user = relationship("Users", back_populates="agent_profile")
    chats = relationship("Chat", back_populates="agent")
    search_requests = relationship("SearchRequest", back_populates="agent")


class Chat(Base):
    __tablename__ = "chat"
    chat_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    agent_id = Column(Integer, ForeignKey("agent_profile.agent_id"), nullable=True)
    title = Column(String(200))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    is_active = Column(Boolean, default=True)
    user = relationship("Users", back_populates="chats_as_user", foreign_keys=[user_id])
    agent = relationship("AgentProfile", back_populates="chats")
    messages = relationship("Message", back_populates="chat")


class Message(Base):
    __tablename__ = "message"
    message_id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chat.chat_id", ondelete="CASCADE"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    content = Column(Text)
    sent_at = Column(DateTime, default=datetime.now)
    is_read = Column(Boolean, default=False)
    attachment_url = Column(String(500))
    chat = relationship("Chat", back_populates="messages")
    sender = relationship("Users", back_populates="messages")


class SearchRequest(Base):
    __tablename__ = "search_request"
    request_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    agent_id = Column(Integer, ForeignKey("agent_profile.agent_id"))
    min_price = Column(DECIMAL(15, 2))
    max_price = Column(DECIMAL(15, 2))
    min_area = Column(DECIMAL(10, 2))
    max_area = Column(DECIMAL(10, 2))
    rooms = Column(Integer)
    country_id = Column(Integer, ForeignKey("country.country_id"))
    region_id = Column(Integer, ForeignKey("region.region_id"))
    city_id = Column(Integer, ForeignKey("city.city_id"))
    district_id = Column(Integer, ForeignKey("district.district_id"))
    street_id = Column(Integer, ForeignKey("street.street_id"))
    house_id = Column(Integer, ForeignKey("house.house_id"))
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    user = relationship("Users", back_populates="search_requests")
    agent = relationship("AgentProfile", back_populates="search_requests")
    country = relationship("Country")
    region = relationship("Region")
    city = relationship("City")
    district = relationship("District")
    street = relationship("Street")
    house = relationship("House")


# ============================================
# 7. СТАТИСТИКА И МОНИТОРИНГ
# ============================================

class ListingViewStatistics(Base):
    __tablename__ = "listing_view_statistics"
    record_id = Column(Integer, primary_key=True, index=True)
    listing_id = Column(Integer, ForeignKey("listing.listing_id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    view_date = Column(Date, nullable=False)
    view_time = Column(Time, nullable=False)
    ip_address = Column(String(45))
    device_type_id = Column(Integer, ForeignKey("device_type.device_type_id"))
    browser_type_id = Column(Integer, ForeignKey("browser_type.browser_type_id"))
    source_type_id = Column(Integer, ForeignKey("source_type.source_type_id"))
    view_depth_seconds = Column(Integer)
    contacts_opened = Column(Boolean, default=False)
    listing = relationship("Listing", back_populates="view_statistics")
    user = relationship("Users", back_populates="view_statistics")
    device_type = relationship("DeviceType", back_populates="view_statistics")
    browser_type = relationship("BrowserType", back_populates="view_statistics")
    source_type = relationship("SourceType", back_populates="view_statistics")


class SearchStatistics(Base):
    __tablename__ = "search_statistics"
    record_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"))
    search_query = Column(String(500))
    filters_json = Column(JSON)
    results_count = Column(Integer)
    search_datetime = Column(DateTime, default=datetime.now)
    execution_time_seconds = Column(Float)
    selected_listing_id = Column(Integer, ForeignKey("listing.listing_id"))
    user = relationship("Users", back_populates="search_statistics")
    selected_listing = relationship("Listing", back_populates="search_appearances")


class UserActivity(Base):
    __tablename__ = "user_activity"
    activity_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    activity_date = Column(Date, nullable=False)
    login_time = Column(Time)
    logout_time = Column(Time)
    session_duration_minutes = Column(Integer)
    views_count = Column(Integer, default=0)
    searches_count = Column(Integer, default=0)
    calls_count = Column(Integer, default=0)
    device_type_id = Column(Integer, ForeignKey("device_type.device_type_id"))
    user = relationship("Users", back_populates="user_activities")
    device_type = relationship("DeviceType", back_populates="user_activities")


class ListingPerformance(Base):
    __tablename__ = "listing_performance"
    record_id = Column(Integer, primary_key=True, index=True)
    listing_id = Column(Integer, ForeignKey("listing.listing_id", ondelete="CASCADE"), nullable=False)
    calculation_date = Column(Date, nullable=False)
    total_views = Column(Integer, default=0)
    unique_views = Column(Integer, default=0)
    contacts_opened = Column(Integer, default=0)
    favorites_added = Column(Integer, default=0)
    listing = relationship("Listing", back_populates="performance")


class ActionLog(Base):
    __tablename__ = "action_log"
    log_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    action_type_id = Column(Integer, ForeignKey("action_type.action_type_id"))
    listing_id = Column(Integer, ForeignKey("listing.listing_id"))
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    action_datetime = Column(DateTime, default=datetime.now)
    details = Column(JSON)
    user = relationship("Users", back_populates="action_logs")
    action_type = relationship("ActionType", back_populates="action_logs")
    listing = relationship("Listing", back_populates="action_logs")


class BlocksAndViolations(Base):
    __tablename__ = "blocks_and_violations"
    block_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    violation_type_id = Column(Integer, ForeignKey("violation_type.violation_type_id"))
    description = Column(String(500))
    listing_id = Column(Integer, ForeignKey("listing.listing_id"))
    block_date = Column(DateTime, default=datetime.now)
    unblock_date = Column(DateTime)
    blocked_by_admin = Column(Integer, ForeignKey("users.user_id"))
    block_status_id = Column(Integer, ForeignKey("block_status.block_status_id"))
    user = relationship("Users", back_populates="violations", foreign_keys=[user_id])
    violation_type = relationship("ViolationType", back_populates="violations")
    listing = relationship("Listing", back_populates="violations")
    blocked_by_admin_user = relationship("Users", back_populates="moderated_violations", foreign_keys=[blocked_by_admin])
    block_status = relationship("BlockStatus", back_populates="blocks")


class SearchHistory(Base):
    __tablename__ = "search_history"
    history_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    search_query = Column(String(500))
    filter_parameters = Column(JSON)
    search_date = Column(DateTime, default=datetime.now)
    results_count = Column(Integer)
    user = relationship("Users", back_populates="search_history")