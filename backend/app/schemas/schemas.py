from typing import Optional, List, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

# ----------------- Auth & User Schemas -----------------
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: int
    name: str
    email: str

class TokenPayload(BaseModel):
    sub: Optional[str] = None
    role: Optional[str] = None

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    first_name: str
    last_name: str
    phone: Optional[str] = None
    role: str = "customer"  # customer, provider, technician, admin
    
    # Provider extra fields if registering as provider
    company_name: Optional[str] = None
    business_registration_no: Optional[str] = None
    bio: Optional[str] = None
    experience_years: Optional[int] = 1

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    email: EmailStr
    reset_token: str
    new_password: str = Field(..., min_length=6)

class PasswordChange(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=6)

class UserOut(BaseModel):
    id: int
    email: str
    role: str
    first_name: str
    last_name: str
    phone: Optional[str]
    is_active: bool
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True

# ----------------- Customer & Address Schemas -----------------
class AddressCreate(BaseModel):
    title: str = "Home"
    address_line: str
    city: str
    state: str
    postal_code: str
    landmark: Optional[str] = None
    is_default: bool = False

class AddressOut(AddressCreate):
    id: int
    customer_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class CustomerProfileOut(BaseModel):
    id: int
    user_id: int
    alternate_phone: Optional[str]
    profile_pic: Optional[str]
    loyalty_points: int
    addresses: List[AddressOut] = []
    user: Optional[UserOut]

    class Config:
        from_attributes = True

# ----------------- Service Provider Schemas -----------------
class ProviderServiceAreaCreate(BaseModel):
    city: str
    postal_code: str
    radius_km: float = 15.0

class ProviderServiceAreaOut(ProviderServiceAreaCreate):
    id: int
    provider_id: int

    class Config:
        from_attributes = True

class AvailabilitySlotCreate(BaseModel):
    day_of_week: int  # 0 to 6
    start_time: str   # e.g., "09:00"
    end_time: str     # e.g., "12:00"
    slot_capacity: int = 2

class AvailabilitySlotOut(AvailabilitySlotCreate):
    id: int
    provider_id: int
    is_active: bool

    class Config:
        from_attributes = True

class ProviderOut(BaseModel):
    id: int
    user_id: int
    company_name: str
    business_registration_no: Optional[str]
    bio: Optional[str]
    experience_years: int
    verification_status: str
    verification_notes: Optional[str]
    id_proof_url: Optional[str]
    business_proof_url: Optional[str]
    commission_rate: float
    rating_avg: float
    rating_count: int
    user: Optional[UserOut] = None

    class Config:
        from_attributes = True

class ProviderVerificationUpdate(BaseModel):
    status: str  # approved, rejected, pending
    notes: Optional[str] = None
    commission_rate: Optional[float] = None

# ----------------- Technician Schemas -----------------
class TechnicianCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    phone: Optional[str]
    specialization: Optional[str]
    experience_years: int = 1

class TechnicianOut(BaseModel):
    id: int
    user_id: int
    provider_id: Optional[int]
    specialization: Optional[str]
    experience_years: int
    status: str
    user: Optional[UserOut] = None

    class Config:
        from_attributes = True

# ----------------- Category & Service Schemas -----------------
class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None
    icon: Optional[str] = "Wrench"
    image_url: Optional[str] = None
    sort_order: int = 0

class CategoryOut(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str]
    icon: Optional[str]
    image_url: Optional[str]
    is_active: bool
    sort_order: int
    created_at: datetime

    class Config:
        from_attributes = True

class ServiceCreate(BaseModel):
    category_id: int
    name: str
    short_description: Optional[str] = None
    full_description: Optional[str] = None
    base_price: float
    duration_minutes: int = 60
    image_url: Optional[str] = None

class ServiceOut(BaseModel):
    id: int
    category_id: int
    name: str
    slug: str
    short_description: Optional[str]
    full_description: Optional[str]
    base_price: float
    duration_minutes: int
    image_url: Optional[str]
    is_active: bool
    category: Optional[CategoryOut] = None

    class Config:
        from_attributes = True

# ----------------- Booking Schemas -----------------
class BookingCreate(BaseModel):
    service_id: int
    provider_id: int
    address_id: Optional[int] = None
    # In case address is submitted inline:
    new_address: Optional[AddressCreate] = None
    scheduled_date: str  # YYYY-MM-DD
    scheduled_slot: str  # e.g., "09:00 - 11:00"
    problem_description: Optional[str] = None
    reference_images: Optional[List[str]] = []
    coupon_code: Optional[str] = None

class BookingReschedule(BaseModel):
    scheduled_date: str
    scheduled_slot: str

class BookingStatusUpdate(BaseModel):
    status: str
    reason: Optional[str] = None

class TechnicianAssignRequest(BaseModel):
    technician_id: int
    notes: Optional[str] = None

class JobStatusUpdateRequest(BaseModel):
    status: str  # arrived, in_progress, completed
    remarks: Optional[str] = None
    completion_images: Optional[List[str]] = []

# ----------------- Payment & Invoice Schemas -----------------
class PaymentCalculationRequest(BaseModel):
    service_id: int
    provider_id: Optional[int] = None
    coupon_code: Optional[str] = None

class PaymentCalculationOut(BaseModel):
    service_price: float
    discount_amount: float
    platform_commission: float
    final_amount: float
    coupon_applied: Optional[str] = None

class PaymentProcessRequest(BaseModel):
    booking_id: int
    payment_gateway: str = "mock_sandbox"  # razorpay, stripe, cod, mock_sandbox
    razorpay_payment_id: Optional[str] = None
    razorpay_order_id: Optional[str] = None
    razorpay_signature: Optional[str] = None

class PaymentOut(BaseModel):
    id: int
    booking_id: int
    transaction_id: str
    payment_gateway: str
    amount: float
    currency: str
    status: str
    payment_method: str
    paid_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

class InvoiceOut(BaseModel):
    id: int
    invoice_number: str
    booking_id: int
    customer_name: str
    customer_email: str
    provider_name: str
    service_name: str
    subtotal: float
    tax_amount: float
    discount_amount: float
    platform_fee: float
    total_amount: float
    invoice_date: datetime

    class Config:
        from_attributes = True

# ----------------- Booking Schemas -----------------
class BookingAssignmentOut(BaseModel):
    id: int
    booking_id: int
    technician_id: int
    status: str
    assigned_at: Optional[datetime] = None
    arrival_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    technician_notes: Optional[str] = None
    technician: Optional[TechnicianOut] = None

    class Config:
        from_attributes = True

class BookingImageOut(BaseModel):
    id: int
    booking_id: int
    image_type: str
    image_url: str
    uploaded_by_role: str
    created_at: datetime

    class Config:
        from_attributes = True

class BookingOut(BaseModel):
    id: int
    booking_code: str
    customer_id: int
    provider_id: int
    service_id: int
    address_id: Optional[int] = None
    scheduled_date: str
    scheduled_slot: str
    status: str
    problem_description: Optional[str] = None
    cancellation_reason: Optional[str] = None
    service_price: float
    discount_amount: float
    platform_commission: float
    final_amount: float
    created_at: datetime
    updated_at: datetime
    
    # Nested info
    service: Optional[ServiceOut] = None
    provider: Optional[ProviderOut] = None
    customer: Optional[CustomerProfileOut] = None
    address: Optional[AddressOut] = None
    assignments: List[BookingAssignmentOut] = []
    images: List[BookingImageOut] = []
    payment: Optional[PaymentOut] = None
    invoice: Optional[InvoiceOut] = None

    class Config:
        from_attributes = True

# ----------------- Coupon Schemas -----------------
class CouponCreate(BaseModel):
    code: str
    description: Optional[str] = None
    discount_type: str = "percentage"  # percentage, fixed
    discount_value: float
    min_booking_amount: float = 0.0
    max_discount: Optional[float] = None
    usage_limit: int = 100
    is_active: bool = True

class CouponOut(CouponCreate):
    id: int
    times_used: int
    created_at: datetime

    class Config:
        from_attributes = True

# ----------------- Review & Complaint Schemas -----------------
class ReviewCreate(BaseModel):
    booking_id: int
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None

class ReviewReply(BaseModel):
    reply: str

class ReviewOut(BaseModel):
    id: int
    booking_id: int
    customer_id: int
    provider_id: int
    rating: int
    comment: Optional[str]
    provider_reply: Optional[str]
    created_at: datetime
    customer: Optional[CustomerProfileOut] = None

    class Config:
        from_attributes = True

class ComplaintCreate(BaseModel):
    booking_id: int
    subject: str
    description: str
    priority: str = "medium"

class ComplaintResolution(BaseModel):
    status: str  # resolved, closed, under_review
    resolution_notes: str

class ComplaintOut(BaseModel):
    id: int
    booking_id: int
    customer_id: int
    provider_id: int
    subject: str
    description: str
    priority: str
    status: str
    resolution_notes: Optional[str]
    resolved_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True

# ----------------- Notification Schemas -----------------
class NotificationOut(BaseModel):
    id: int
    user_id: int
    title: str
    message: str
    notification_type: str
    link: Optional[str]
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True
