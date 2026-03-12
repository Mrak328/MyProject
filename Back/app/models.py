from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, DECIMAL, JSON, Time, Date
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime


class Role(Base):
    __tablename__ = "role"

    role_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    role_code = Column(String(20), unique=True)
    description = Column(String(255))

    users = relationship("Users", back_populates="role")


class PropertyType(Base):
    __tablename__ = "property_type"

    property_type_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    parent_type_id = Column(Integer, ForeignKey("property_type.property_type_id"))

    listings = relationship("Listing", back_populates="property_type")
    parent = relationship("PropertyType", remote_side=[property_type_id])


class DealType(Base):
    __tablename__ = "deal_type"

    deal_type_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    rental_term = Column(String(20))

    listings = relationship("Listing", back_populates="deal_type")


class RenovationCondition(Base):
    __tablename__ = "renovation_condition"

    renovation_condition_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)

    listings = relationship("Listing", back_populates="renovation_condition")


class ListingStatus(Base):
    __tablename__ = "listing_status"

    listing_status_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(30), nullable=False)
    status_code = Column(String(20), unique=True)

    listings = relationship("Listing", back_populates="status")


class Users(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    password = Column(String(256), nullable=False)
    phone_number = Column(String(20), unique=True, nullable=False)
    email = Column(String(100), unique=True)
    role_id = Column(Integer, ForeignKey("role.role_id"), nullable=False, default=3)
    registration_date = Column(DateTime, default=datetime.now)
    last_activity = Column(DateTime)
    phone_confirmed = Column(Boolean, default=False)
    email_confirmed = Column(Boolean, default=False)
    rating = Column(DECIMAL(3, 2), default=0)
    reviews_count = Column(Integer, default=0)
    status = Column(String(20), default='active')
    avatar_url = Column(String(500))

    role = relationship("Role", back_populates="users")
    listings = relationship("Listing", back_populates="user", foreign_keys="Listing.user_id")
    moderated_listings = relationship("Listing", back_populates="moderator", foreign_keys="Listing.moderator_id")
    reviews_given = relationship("Review", back_populates="author", foreign_keys="Review.author_id")
    reviews_received = relationship("Review", back_populates="user", foreign_keys="Review.user_id")
    comments = relationship("Comment", back_populates="user")
    favorites = relationship("Favorite", back_populates="user")
    complaints = relationship("Complaint", foreign_keys="Complaint.complainant_user_id", back_populates="complainant")
    complaints_against = relationship("Complaint", foreign_keys="Complaint.violator_user_id", back_populates="violator")
    moderated_complaints = relationship("Complaint", foreign_keys="Complaint.moderator_id", back_populates="moderator")
    violations = relationship("BlocksAndViolations",
                              foreign_keys="BlocksAndViolations.user_id",
                              back_populates="user")
    violations_moderated = relationship("BlocksAndViolations",
                                        foreign_keys="BlocksAndViolations.blocked_by_admin",
                                        back_populates="admin")
    search_history = relationship("SearchHistory", back_populates="user")
    search_subscriptions = relationship("SearchSubscription", back_populates="user")
    activity_logs = relationship("ActionLog", back_populates="user")


class Listing(Base):
    __tablename__ = "listing"

    listing_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    listing_status_id = Column(Integer, ForeignKey("listing_status.listing_status_id"), nullable=False, default=1)
    publication_date = Column(DateTime, default=datetime.now)
    update_date = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    expiration_date = Column(DateTime)
    views = Column(Integer, default=0)
    property_type_id = Column(Integer, ForeignKey("property_type.property_type_id"), nullable=False)
    deal_type_id = Column(Integer, ForeignKey("deal_type.deal_type_id"), nullable=False)
    address = Column(String(500), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    total_area = Column(DECIMAL(10, 2))
    renovation_condition_id = Column(Integer, ForeignKey("renovation_condition.renovation_condition_id"))
    price = Column(DECIMAL(12, 2), nullable=False)
    currency = Column(String(3), default='RUB')
    utilities_included = Column(Boolean, default=False)
    deposit = Column(DECIMAL(12, 2))
    mortgage_available = Column(Boolean, default=False)
    contact_person = Column(String(100))
    contact_phone = Column(String(20))
    moderated = Column(Boolean, default=False)
    moderator_id = Column(Integer, ForeignKey("users.user_id"))
    moderation_date = Column(DateTime)

    user = relationship("Users", back_populates="listings", foreign_keys=[user_id])
    moderator = relationship("Users", back_populates="moderated_listings", foreign_keys=[moderator_id])
    status = relationship("ListingStatus", back_populates="listings")
    property_type = relationship("PropertyType", back_populates="listings")
    deal_type = relationship("DealType", back_populates="listings")
    renovation_condition = relationship("RenovationCondition", back_populates="listings")
    photos = relationship("Photo", back_populates="listing")
    reviews = relationship("Review", back_populates="listing")
    favorites = relationship("Favorite", back_populates="listing")
    complaints = relationship("Complaint", back_populates="listing")
    view_statistics = relationship("ListingViewStatistics", back_populates="listing")
    target_conversions = relationship("TargetConversions", back_populates="listing")
    performance = relationship("ListingPerformance", back_populates="listing")
    violations = relationship("BlocksAndViolations",
                              foreign_keys="BlocksAndViolations.listing_id",
                              back_populates="listing")


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


class Review(Base):
    __tablename__ = "review"

    review_id = Column(Integer, primary_key=True, index=True)
    author_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    listing_id = Column(Integer, ForeignKey("listing.listing_id"))
    rating = Column(Integer, nullable=False)
    content = Column(String(1000))
    created_date = Column(DateTime, default=datetime.now)

    author = relationship("Users", foreign_keys=[author_id], back_populates="reviews_given")
    user = relationship("Users", foreign_keys=[user_id], back_populates="reviews_received")
    listing = relationship("Listing", back_populates="reviews")
    responses = relationship("ReviewResponse", back_populates="review")
    comments = relationship("Comment", back_populates="review")


class ReviewResponse(Base):
    __tablename__ = "review_response"

    response_id = Column(Integer, primary_key=True, index=True)
    review_id = Column(Integer, ForeignKey("review.review_id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    content = Column(String(500), nullable=False)
    response_date = Column(DateTime, default=datetime.now)

    review = relationship("Review", back_populates="responses")
    user = relationship("Users")


class Comment(Base):
    __tablename__ = "comment"

    comment_id = Column(Integer, primary_key=True, index=True)
    review_id = Column(Integer, ForeignKey("review.review_id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    content = Column(String(500), nullable=False)
    created_date = Column(DateTime, default=datetime.now)

    review = relationship("Review", back_populates="comments")
    user = relationship("Users", back_populates="comments")


class Favorite(Base):
    __tablename__ = "favorite"

    favorite_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    listing_id = Column(Integer, ForeignKey("listing.listing_id", ondelete="CASCADE"), nullable=False)
    added_date = Column(DateTime, default=datetime.now)
    note = Column(String(255))

    user = relationship("Users", back_populates="favorites")
    listing = relationship("Listing", back_populates="favorites")


class Complaint(Base):
    __tablename__ = "complaint"

    complaint_id = Column(Integer, primary_key=True, index=True)
    complainant_user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    listing_id = Column(Integer, ForeignKey("listing.listing_id"))
    violator_user_id = Column(Integer, ForeignKey("users.user_id"))
    complaint_type = Column(String(50), nullable=False)
    description = Column(String(500))
    processing_status = Column(String(20), default='new')
    created_date = Column(DateTime, default=datetime.now)
    processing_date = Column(DateTime)
    moderator_id = Column(Integer, ForeignKey("users.user_id"))
    resolution = Column(String(500))

    complainant = relationship("Users", foreign_keys=[complainant_user_id], back_populates="complaints")
    violator = relationship("Users", foreign_keys=[violator_user_id], back_populates="complaints_against")
    moderator = relationship("Users", foreign_keys=[moderator_id], back_populates="moderated_complaints")
    listing = relationship("Listing", back_populates="complaints")


class ListingViewStatistics(Base):
    __tablename__ = "listing_view_statistics"

    record_id = Column(Integer, primary_key=True, index=True)
    listing_id = Column(Integer, ForeignKey("listing.listing_id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    view_date = Column(Date, nullable=False)
    view_time = Column(Time, nullable=False)
    ip_address = Column(String(45))
    device = Column(String(50))
    browser = Column(String(100))
    referrer_source = Column(String(255))
    view_depth_seconds = Column(Integer)
    contacts_opened = Column(Boolean, default=False)

    listing = relationship("Listing", back_populates="view_statistics")
    user = relationship("Users")


class TargetConversions(Base):
    __tablename__ = "target_conversions"

    conversion_id = Column(Integer, primary_key=True, index=True)
    listing_id = Column(Integer, ForeignKey("listing.listing_id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    conversion_type = Column(String(50), nullable=False)
    event_datetime = Column(DateTime, default=datetime.now)
    source = Column(String(100))
    successful = Column(Boolean, default=True)

    listing = relationship("Listing", back_populates="target_conversions")
    user = relationship("Users")


class SearchStatistics(Base):
    __tablename__ = "search_statistics"

    record_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"))
    search_query = Column(String(500))
    filters_json = Column(JSON)
    results_count = Column(Integer)
    search_datetime = Column(DateTime, default=datetime.now)  # Изменено с search_date_time
    execution_time_seconds = Column(Float)
    selected_listing_id = Column(Integer, ForeignKey("listing.listing_id"))

    user = relationship("Users")
    selected_listing = relationship("Listing")


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
    device_type = Column(String(50))

    user = relationship("Users")


class ListingPerformance(Base):
    __tablename__ = "listing_performance"

    record_id = Column(Integer, primary_key=True, index=True)
    listing_id = Column(Integer, ForeignKey("listing.listing_id", ondelete="CASCADE"), nullable=False)
    calculation_date = Column(Date, nullable=False)
    total_views = Column(Integer, default=0)
    unique_views = Column(Integer, default=0)
    contacts_opened = Column(Integer, default=0)
    calls = Column(Integer, default=0)
    favorites_added = Column(Integer, default=0)
    ctr = Column(Float)
    call_conversion_rate = Column(Float)
    average_search_position = Column(Integer)

    listing = relationship("Listing", back_populates="performance")


class BlocksAndViolations(Base):
    __tablename__ = "blocks_and_violations"

    block_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    violation_type = Column(String(100), nullable=False)
    description = Column(String(500))
    listing_id = Column(Integer, ForeignKey("listing.listing_id"))
    block_date = Column(DateTime, default=datetime.now)
    unblock_date = Column(DateTime)
    blocked_by_admin = Column(Integer, ForeignKey("users.user_id"))
    status = Column(String(20), default='active')

    user = relationship("Users", foreign_keys=[user_id], back_populates="violations")
    admin = relationship("Users", foreign_keys=[blocked_by_admin], back_populates="violations_moderated")
    listing = relationship("Listing", foreign_keys=[listing_id], back_populates="violations")


class SearchHistory(Base):
    __tablename__ = "search_history"

    history_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    search_query = Column(String(500))
    filter_parameters = Column(JSON)
    search_date = Column(DateTime, default=datetime.now)
    results_count = Column(Integer)

    user = relationship("Users", back_populates="search_history")


class SearchSubscription(Base):
    __tablename__ = "search_subscriptions"

    subscription_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100))
    filter_parameters = Column(JSON, nullable=False)
    email_notifications = Column(Boolean, default=True)
    created_date = Column(DateTime, default=datetime.now)
    last_sent_date = Column(DateTime)
    active = Column(Boolean, default=True)

    user = relationship("Users", back_populates="search_subscriptions")


class ActionLog(Base):
    __tablename__ = "action_log"

    log_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    action = Column(String(100), nullable=False)
    listing_id = Column(Integer, ForeignKey("listing.listing_id"))
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    action_datetime = Column(DateTime, default=datetime.now)  # Изменено с action_date_time
    details = Column(JSON)

    user = relationship("Users", back_populates="activity_logs")
    listing = relationship("Listing")