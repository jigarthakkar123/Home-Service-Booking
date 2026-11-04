import secrets
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import (
    Payment, Invoice, Booking, Service, ServiceProvider, Coupon, User, Customer, Notification
)
from app.schemas.schemas import (
    PaymentCalculationRequest, PaymentCalculationOut, PaymentProcessRequest,
    PaymentOut, InvoiceOut
)
from app.api.deps import get_current_active_user, require_customer

router = APIRouter()

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


@router.post("/process", response_model=PaymentOut)
def process_payment(
    pay_in: PaymentProcessRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    booking = db.query(Booking).filter(Booking.id == pay_in.booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

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
        message=f"Payment of ₹{booking.final_amount} for booking {booking.booking_code} was successful. Invoice #{invoice.invoice_number} is ready.",
        notification_type="payment",
        link=f"/bookings/{booking.id}"
    ))

    db.commit()
    db.refresh(payment)
    return payment


@router.get("/invoices/{booking_id}", response_model=InvoiceOut)
def get_invoice_for_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    invoice = db.query(Invoice).filter(Invoice.booking_id == booking_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not generated for this booking yet.")
    return invoice
