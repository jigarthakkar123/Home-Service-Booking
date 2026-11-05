from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Boolean, Float, Text, DateTime, ForeignKey, Enum, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship
from app.core.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(120), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="customer")  # admin, customer, provider, technician
    first_name = Column(String(60), nullable=False)
    last_name = Column(String(60), nullable=False)
    phone = Column(String(25), nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    reset_token = Column(String(255), nullable=True)
    reset_token_expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    # Relationships
    customer_profile = relationship("Customer", back_populates="user", uselist=False, cascade="all, delete-orphan")
    provider_profile = relationship("ServiceProvider", back_populates="user", uselist=False, cascade="all, delete-orphan")
    technician_profile = relationship("Technician", back_populates="user", uselist=False, cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    alternate_phone = Column(String(25), nullable=True)
    profile_pic = Column(String(255), nullable=True)
    loyalty_points = Column(Integer, default=0)
    created_at = Column(DateTime, default=utc_now)

    user = relationship("User", back_populates="customer_profile")
    addresses = relationship("Address", back_populates="customer", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="customer")
    reviews = relationship("Review", back_populates="customer")
    complaints = relationship("Complaint", back_populates="customer")


class ServiceProvider(Base):
    __tablename__ = "service_providers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    company_name = Column(String(120), nullable=False)
    business_registration_no = Column(String(60), nullable=True)
    bio = Column(Text, nullable=True)
    experience_years = Column(Integer, default=1)
    verification_status = Column(String(20), default="pending")  # pending, approved, rejected
    verification_notes = Column(Text, nullable=True)
    id_proof_url = Column(String(255), nullable=True)
    business_proof_url = Column(String(255), nullable=True)
    commission_rate = Column(Float, default=15.0)  # percentage
    rating_avg = Column(Float, default=5.0)
    rating_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=utc_now)

    user = relationship("User", back_populates="provider_profile")
    technicians = relationship("Technician", back_populates="provider")
    services = relationship("ProviderService", back_populates="provider", cascade="all, delete-orphan")
    service_areas = relationship("ServiceArea", back_populates="provider", cascade="all, delete-orphan")
    availability_slots = relationship("AvailabilitySlot", back_populates="provider", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="provider")
    earnings = relationship("ProviderEarning", back_populates="provider")


class Technician(Base):
    __tablename__ = "technicians"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    provider_id = Column(Integer, ForeignKey("service_providers.id", ondelete="SET NULL"), nullable=True)
    specialization = Column(String(100), nullable=True)
    experience_years = Column(Integer, default=1)
    status = Column(String(20), default="available")  # available, busy, offline
    created_at = Column(DateTime, default=utc_now)

    user = relationship("User", back_populates="technician_profile")
    provider = relationship("ServiceProvider", back_populates="technicians")
    assignments = relationship("BookingAssignment", back_populates="technician")


class Address(Base):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(50), default="Home")  # Home, Office, Other
    address_line = Column(String(255), nullable=False)
    city = Column(String(80), nullable=False)
    state = Column(String(80), nullable=False)
    postal_code = Column(String(20), nullable=False)
    landmark = Column(String(120), nullable=True)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utc_now)

    customer = relationship("Customer", back_populates="addresses")
    bookings = relationship("Booking", back_populates="address")


class ServiceCategory(Base):
    __tablename__ = "service_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    icon = Column(String(50), default="Wrench")
    image_url = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=utc_now)

    services = relationship("Service", back_populates="category", cascade="all, delete-orphan")


class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("service_categories.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(120), nullable=False)
    slug = Column(String(120), unique=True, index=True, nullable=False)
    short_description = Column(String(255), nullable=True)
    full_description = Column(Text, nullable=True)
    base_price = Column(Float, nullable=False, default=499.0)
    duration_minutes = Column(Integer, default=60)
    image_url = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utc_now)

    category = relationship("ServiceCategory", back_populates="services")
    provider_services = relationship("ProviderService", back_populates="service", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="service")


class ProviderService(Base):
    __tablename__ = "provider_services"

    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, ForeignKey("service_providers.id", ondelete="CASCADE"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id", ondelete="CASCADE"), nullable=False)
    custom_price = Column(Float, nullable=True)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utc_now)

    __table_args__ = (
        UniqueConstraint("provider_id", "service_id", name="uq_provider_service"),
    )

    provider = relationship("ServiceProvider", back_populates="services")
    service = relationship("Service", back_populates="provider_services")


class ServiceArea(Base):
    __tablename__ = "service_areas"

    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, ForeignKey("service_providers.id", ondelete="CASCADE"), nullable=False)
    city = Column(String(80), nullable=False)
    postal_code = Column(String(20), nullable=False)
    radius_km = Column(Float, default=15.0)
    created_at = Column(DateTime, default=utc_now)

    provider = relationship("ServiceProvider", back_populates="service_areas")


class AvailabilitySlot(Base):
    __tablename__ = "availability_slots"

    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, ForeignKey("service_providers.id", ondelete="CASCADE"), nullable=False)
    day_of_week = Column(Integer, nullable=False)  # 0=Monday, 6=Sunday
    start_time = Column(String(10), nullable=False)  # "09:00"
    end_time = Column(String(10), nullable=False)    # "12:00"
    slot_capacity = Column(Integer, default=2)       # Max bookings allowed per slot
    is_active = Column(Boolean, default=True)

    provider = relationship("ServiceProvider", back_populates="availability_slots")


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    booking_code = Column(String(30), unique=True, index=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    provider_id = Column(Integer, ForeignKey("service_providers.id", ondelete="CASCADE"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id", ondelete="CASCADE"), nullable=False)
    address_id = Column(Integer, ForeignKey("addresses.id", ondelete="SET NULL"), nullable=True)
    
    scheduled_date = Column(String(15), nullable=False)  # YYYY-MM-DD
    scheduled_slot = Column(String(30), nullable=False)  # e.g., "09:00 - 11:00"
    
    # Status: pending, confirmed, provider_assigned, in_progress, completed, cancelled, rejected
    status = Column(String(30), default="pending", nullable=False)
    problem_description = Column(Text, nullable=True)
    cancellation_reason = Column(Text, nullable=True)
    
    service_price = Column(Float, nullable=False, default=0.0)
    discount_amount = Column(Float, default=0.0)
    platform_commission = Column(Float, default=0.0)
    final_amount = Column(Float, nullable=False, default=0.0)
    
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    customer = relationship("Customer", back_populates="bookings")
    provider = relationship("ServiceProvider", back_populates="bookings")
    service = relationship("Service", back_populates="bookings")
    address = relationship("Address", back_populates="bookings")
    assignments = relationship("BookingAssignment", back_populates="booking", cascade="all, delete-orphan")
    images = relationship("BookingImage", back_populates="booking", cascade="all, delete-orphan")
    payment = relationship("Payment", back_populates="booking", uselist=False, cascade="all, delete-orphan")
    invoice = relationship("Invoice", back_populates="booking", uselist=False, cascade="all, delete-orphan")
    review = relationship("Review", back_populates="booking", uselist=False, cascade="all, delete-orphan")
    complaints = relationship("Complaint", back_populates="booking", cascade="all, delete-orphan")
    earning = relationship("ProviderEarning", back_populates="booking", uselist=False)

    __table_args__ = (
        Index("idx_provider_date_slot", "provider_id", "scheduled_date", "scheduled_slot"),
    )


class BookingAssignment(Base):
    __tablename__ = "booking_assignments"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False)
    technician_id = Column(Integer, ForeignKey("technicians.id", ondelete="CASCADE"), nullable=False)
    assigned_at = Column(DateTime, default=utc_now)
    arrival_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    status = Column(String(25), default="assigned")  # assigned, accepted, arrived, in_progress, completed
    technician_notes = Column(Text, nullable=True)

    booking = relationship("Booking", back_populates="assignments")
    technician = relationship("Technician", back_populates="assignments")


class BookingImage(Base):
    __tablename__ = "booking_images"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False)
    image_type = Column(String(30), default="customer_issue")  # customer_issue, work_before, work_after, completion_proof
    image_url = Column(String(500), nullable=False)
    uploaded_by_role = Column(String(20), default="customer")
    created_at = Column(DateTime, default=utc_now)

    booking = relationship("Booking", back_populates="images")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id", ondelete="CASCADE"), unique=True, nullable=False)
    transaction_id = Column(String(100), unique=True, index=True, nullable=False)
    payment_gateway = Column(String(30), default="razorpay")  # razorpay, stripe, cod, mock_sandbox
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="INR")
    status = Column(String(20), default="pending")  # pending, paid, failed, refunded
    payment_method = Column(String(30), default="online")
    payment_data_json = Column(Text, nullable=True)
    paid_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    booking = relationship("Booking", back_populates="payment")
    invoice = relationship("Invoice", back_populates="payment", uselist=False)


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(50), unique=True, index=True, nullable=False)
    booking_id = Column(Integer, ForeignKey("bookings.id", ondelete="CASCADE"), unique=True, nullable=False)
    payment_id = Column(Integer, ForeignKey("payments.id", ondelete="SET NULL"), nullable=True)
    
    customer_name = Column(String(120), nullable=False)
    customer_email = Column(String(120), nullable=False)
    provider_name = Column(String(120), nullable=False)
    service_name = Column(String(120), nullable=False)
    
    subtotal = Column(Float, nullable=False)
    tax_amount = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    platform_fee = Column(Float, default=0.0)
    total_amount = Column(Float, nullable=False)
    
    invoice_date = Column(DateTime, default=utc_now)
    created_at = Column(DateTime, default=utc_now)

    booking = relationship("Booking", back_populates="invoice")
    payment = relationship("Payment", back_populates="invoice")


class Coupon(Base):
    __tablename__ = "coupons"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(30), unique=True, index=True, nullable=False)
    description = Column(String(255), nullable=True)
    discount_type = Column(String(20), default="percentage")  # percentage, fixed
    discount_value = Column(Float, nullable=False)
    min_booking_amount = Column(Float, default=0.0)
    max_discount = Column(Float, nullable=True)
    valid_from = Column(DateTime, default=utc_now)
    valid_to = Column(DateTime, nullable=True)
    usage_limit = Column(Integer, default=100)
    times_used = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utc_now)


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id", ondelete="CASCADE"), unique=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    provider_id = Column(Integer, ForeignKey("service_providers.id", ondelete="CASCADE"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1 to 5
    comment = Column(Text, nullable=True)
    provider_reply = Column(Text, nullable=True)
    is_moderated = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utc_now)

    booking = relationship("Booking", back_populates="review")
    customer = relationship("Customer", back_populates="reviews")


class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    provider_id = Column(Integer, ForeignKey("service_providers.id", ondelete="CASCADE"), nullable=False)
    subject = Column(String(150), nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(String(20), default="medium")  # low, medium, high, critical
    status = Column(String(20), default="open")      # open, under_review, resolved, closed
    resolution_notes = Column(Text, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    booking = relationship("Booking", back_populates="complaints")
    customer = relationship("Customer", back_populates="complaints")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(150), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(30), default="system")  # booking, payment, assignment, complaint, system
    link = Column(String(255), nullable=True)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utc_now)

    user = relationship("User", back_populates="notifications")


class ProviderEarning(Base):
    __tablename__ = "provider_earnings"

    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, ForeignKey("service_providers.id", ondelete="CASCADE"), nullable=False)
    booking_id = Column(Integer, ForeignKey("bookings.id", ondelete="CASCADE"), unique=True, nullable=False)
    gross_amount = Column(Float, nullable=False)
    platform_commission_rate = Column(Float, default=15.0)
    platform_fee = Column(Float, nullable=False)
    net_earnings = Column(Float, nullable=False)
    payout_status = Column(String(20), default="pending")  # pending, processing, paid
    payout_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    provider = relationship("ServiceProvider", back_populates="earnings")
    booking = relationship("Booking", back_populates="earning")
