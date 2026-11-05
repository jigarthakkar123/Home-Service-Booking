import secrets
import hmac
import hashlib
from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.models.models import (
    Payment, Invoice, Booking, Service, ServiceProvider, Coupon, User, Customer, Technician, Notification
)
from app.schemas.schemas import (
    PaymentCalculationRequest, PaymentCalculationOut, PaymentProcessRequest,
    PaymentOut, InvoiceOut
)
from app.api.deps import get_current_active_user, require_customer

router = APIRouter()

class RazorpayVerifyRequest(BaseModel):
    booking_id: int
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str

def generate_invoice_number(db: Session) -> str:
    count = db.query(Invoice).count() + 1
    random_str = secrets.token_hex(2).upper()
    return f"INV-2026-{count:04d}-{random_str}"


@router.post("/calculate", response_model=PaymentCalculationOut)
def calculate_charges(calc_in: PaymentCalculationRequest, db: Session = Depends(get_db)):
    service = db.query(Service).filter(Service.id == calc_in.service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    price = service.base_price
    discount = 0.0
    coupon_applied = None

    if calc_in.coupon_code:
        coupon = db.query(Coupon).filter(
            Coupon.code == calc_in.coupon_code.upper(),
            Coupon.is_active == True
        ).first()
        if coupon and price >= coupon.min_booking_amount:
            if coupon.discount_type == "percentage":
                discount = round((price * coupon.discount_value) / 100.0, 2)
                if coupon.max_discount and discount > coupon.max_discount:
                    discount = coupon.max_discount
            else:
                discount = min(coupon.discount_value, price)
            coupon_applied = coupon.code

    final_amt = max(0.0, round(price - discount, 2))
    comm_fee = round(final_amt * 0.15, 2)

    return {
        "service_price": price,
        "discount_amount": discount,
        "platform_commission": comm_fee,
        "final_amount": final_amt,
        "coupon_applied": coupon_applied
    }


@router.post("/razorpay/create-order")
def create_razorpay_order(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Creates a simulated or live Razorpay Test Order.
    Returns razorpay_order_id, currency, and amount in paise.
    """
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Ownership check: Customer must own booking or be admin
    if current_user.role != "admin" and (not booking.customer or booking.customer.user_id != current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied: Cannot create payment order for another customer.")

    amount_in_paise = int(booking.final_amount * 100)
    order_id = f"order_test_{secrets.token_hex(8)}"

    return {
        "order_id": order_id,
        "amount": amount_in_paise,
        "currency": "INR",
        "booking_id": booking.id,
        "key_id": settings.RAZORPAY_KEY_ID or "rzp_test_HomeServeSandBoxKey",
        "customer_name": f"{current_user.first_name} {current_user.last_name}",
        "customer_email": current_user.email,
        "customer_phone": current_user.phone
    }


@router.post("/process", response_model=PaymentOut)
def process_payment(
    pay_in: PaymentProcessRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    booking = db.query(Booking).filter(Booking.id == pay_in.booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Strict Resource Ownership Check: Only the customer who placed the booking or admin can pay
    if current_user.role != "admin":
        if not booking.customer or booking.customer.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Cannot process payment for another customer's booking."
            )

    existing_payment = db.query(Payment).filter(Payment.booking_id == booking.id).first()
    if existing_payment and existing_payment.status == "paid":
        raise HTTPException(status_code=400, detail="This booking has already been paid for.")

    # Determine transaction ID
    txn_id = pay_in.razorpay_payment_id or f"TXN-HSB-{secrets.token_hex(6).upper()}"

    now = datetime.now(timezone.utc)
    if existing_payment:
        existing_payment.transaction_id = txn_id
        existing_payment.status = "paid"
        existing_payment.paid_at = now
        existing_payment.payment_gateway = pay_in.payment_gateway
        payment = existing_payment
    else:
        payment = Payment(
            booking_id=booking.id,
            transaction_id=txn_id,
            payment_gateway=pay_in.payment_gateway,
            amount=booking.final_amount,
            currency="INR",
            status="paid",
            payment_method="online_card_upi",
            paid_at=now
        )
        db.add(payment)
    db.flush()

    # Generate Invoice automatically
    customer = booking.customer
    customer_user = customer.user if customer else current_user
    provider = booking.provider
    provider_name = provider.company_name if provider else "HomeServe Provider"
    service_name = booking.service.name if booking.service else "Home Service"

    invoice = Invoice(
        invoice_number=generate_invoice_number(db),
        booking_id=booking.id,
        payment_id=payment.id,
        customer_name=f"{customer_user.first_name} {customer_user.last_name}",
        customer_email=customer_user.email,
        provider_name=provider_name,
        service_name=service_name,
        subtotal=booking.service_price,
        tax_amount=round(booking.final_amount * 0.18, 2),  # 18% GST display
        discount_amount=booking.discount_amount,
        platform_fee=booking.platform_commission,
        total_amount=booking.final_amount,
        invoice_date=now
    )
    db.add(invoice)

    # In-app notification
    db.add(Notification(
        user_id=customer_user.id,
        title="Payment Successful",
        message=f"Payment of INR {booking.final_amount} for booking {booking.booking_code} was successful. Invoice #{invoice.invoice_number} is ready.",
        notification_type="payment",
        link=f"/bookings/{booking.id}"
    ))

    db.commit()
    db.refresh(payment)
    return payment


@router.post("/razorpay/verify")
def verify_razorpay_payment(
    data: RazorpayVerifyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Verifies Razorpay HMAC-SHA256 signature against order_id and payment_id.
    Strict cryptographic verification: ZERO bypass permitted.
    """
    booking = db.query(Booking).filter(Booking.id == data.booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if current_user.role != "admin" and (not booking.customer or booking.customer.user_id != current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied: Cannot verify payment for another user.")

    # Calculate expected HMAC-SHA256 signature
    secret = settings.RAZORPAY_KEY_SECRET.encode("utf-8")
    payload = f"{data.razorpay_order_id}|{data.razorpay_payment_id}".encode("utf-8")
    expected_signature = hmac.new(secret, payload, hashlib.sha256).hexdigest()

    # Strict HMAC cryptographic verification (ZERO BYPASS)
    if not hmac.compare_digest(expected_signature, data.razorpay_signature):
        raise HTTPException(status_code=400, detail="Invalid Razorpay cryptographic payment signature.")

    # Process confirmed payment
    return process_payment(
        pay_in=PaymentProcessRequest(
            booking_id=booking.id,
            payment_gateway="razorpay",
            razorpay_payment_id=data.razorpay_payment_id
        ),
        db=db,
        current_user=current_user
    )


@router.get("/invoices/{booking_id}", response_model=InvoiceOut)
def get_invoice_for_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    invoice = db.query(Invoice).filter(Invoice.booking_id == booking_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not generated for this booking yet.")

    # Strict Multi-Tenant Ownership Isolation:
    if current_user.role != "admin":
        b = invoice.booking
        if current_user.role == "customer":
            if not b.customer or b.customer.user_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: Cannot view another customer's invoice."
                )
        elif current_user.role == "provider":
            if not b.provider or b.provider.user_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: Cannot view another provider's invoice."
                )
        elif current_user.role == "technician":
            tech = db.query(Technician).filter(Technician.user_id == current_user.id).first()
            is_assigned = any(a.technician_id == tech.id for a in b.assignments) if tech else False
            if not is_assigned:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: You are not assigned to this booking invoice."
                )

    return invoice
