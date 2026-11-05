import secrets
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
from app.core.database import get_db
from app.models.models import (
    Booking, Customer, ServiceProvider, Service, Address, BookingAssignment,
    BookingImage, Coupon, ProviderEarning, Notification, User, Technician,
    ProviderService, AvailabilitySlot
)
from app.schemas.schemas import (
    BookingCreate, BookingOut, BookingReschedule, BookingStatusUpdate,
    TechnicianAssignRequest, AddressCreate
)
from app.api.deps import (
    get_current_active_user, require_customer, require_provider, require_admin
)

router = APIRouter()

def generate_booking_code(db: Session) -> str:
    count = db.query(Booking).count() + 1
    random_suffix = secrets.token_hex(2).upper()
    return f"HSB-2026-{count:04d}-{random_suffix}"


@router.post("", response_model=BookingOut)
def create_booking(
    booking_in: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_customer)
):
    customer = db.query(Customer).filter(Customer.user_id == current_user.id).first()
    if not customer:
        raise HTTPException(status_code=400, detail="Customer profile not found")
    
    # 1. Validate service
    service = db.query(Service).filter(Service.id == booking_in.service_id, Service.is_active == True).first()
    if not service:
        raise HTTPException(status_code=404, detail="Selected service is not available")
    
    # 2. Validate provider
    provider = db.query(ServiceProvider).filter(
        ServiceProvider.id == booking_in.provider_id,
        ServiceProvider.verification_status == "approved"
    ).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Selected service provider is not verified or available")

    # 3. Double Booking Prevention Logic with Pessimistic Concurrency Lock
    try:
        db.query(ServiceProvider).filter(ServiceProvider.id == provider.id).with_for_update().first()
    except Exception:
        pass  # SQLite uses transactional write locks

    # Count active bookings for this provider, date, and slot
    active_slot_bookings = db.query(Booking).filter(
        Booking.provider_id == provider.id,
        Booking.scheduled_date == booking_in.scheduled_date,
        Booking.scheduled_slot == booking_in.scheduled_slot,
        Booking.status.notin_(["cancelled", "rejected"])
    ).count()

    # Slot capacity default is 2
    max_capacity = 2
    if active_slot_bookings >= max_capacity:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"The selected slot '{booking_in.scheduled_slot}' on {booking_in.scheduled_date} is fully booked. Please choose another time slot."
        )

    # 4. Resolve address
    address_id = booking_in.address_id
    if not address_id and booking_in.new_address:
        new_addr = Address(
            customer_id=customer.id,
            title=booking_in.new_address.title,
            address_line=booking_in.new_address.address_line,
            city=booking_in.new_address.city,
            state=booking_in.new_address.state,
            postal_code=booking_in.new_address.postal_code,
            landmark=booking_in.new_address.landmark,
            is_default=booking_in.new_address.is_default
        )
        db.add(new_addr)
        db.flush()
        address_id = new_addr.id

    if not address_id:
        # Check if customer has any default address
        default_addr = db.query(Address).filter(Address.customer_id == customer.id).first()
        if default_addr:
            address_id = default_addr.id
        else:
            raise HTTPException(status_code=400, detail="Service address is required to place a booking")

    # 5. Pricing calculation
    # Check if provider has custom price
    ps = db.query(ProviderService).filter(
        ProviderService.provider_id == provider.id,
        ProviderService.service_id == service.id
    ).first()
    service_price = ps.custom_price if (ps and ps.custom_price) else service.base_price

    discount_amount = 0.0
    if booking_in.coupon_code:
        coupon = db.query(Coupon).filter(
            Coupon.code == booking_in.coupon_code.upper(),
            Coupon.is_active == True
        ).first()
        if coupon and service_price >= coupon.min_booking_amount:
            if coupon.discount_type == "percentage":
                discount_amount = round((service_price * coupon.discount_value) / 100.0, 2)
                if coupon.max_discount and discount_amount > coupon.max_discount:
                    discount_amount = coupon.max_discount
            else:
                discount_amount = min(coupon.discount_value, service_price)
            coupon.times_used += 1

    final_amount = max(0.0, round(service_price - discount_amount, 2))
    commission_rate = provider.commission_rate or 15.0
    platform_commission = round((final_amount * commission_rate) / 100.0, 2)

    # 6. Create booking
    booking = Booking(
        booking_code=generate_booking_code(db),
        customer_id=customer.id,
        provider_id=provider.id,
        service_id=service.id,
        address_id=address_id,
        scheduled_date=booking_in.scheduled_date,
        scheduled_slot=booking_in.scheduled_slot,
        status="pending",
        problem_description=booking_in.problem_description,
        service_price=service_price,
        discount_amount=discount_amount,
        platform_commission=platform_commission,
        final_amount=final_amount
    )
    db.add(booking)
    db.flush()

    # Save reference images if uploaded
    if booking_in.reference_images:
        for img_url in booking_in.reference_images:
            db.add(BookingImage(
                booking_id=booking.id,
                image_type="customer_issue",
                image_url=img_url,
                uploaded_by_role="customer"
            ))

    # Notifications to customer & provider
    db.add(Notification(
        user_id=customer.user_id,
        title="Booking Placed Successfully",
        message=f"Your booking {booking.booking_code} for {service.name} has been placed. Waiting for provider confirmation.",
        notification_type="booking",
        link=f"/bookings/{booking.id}"
    ))
    db.add(Notification(
        user_id=provider.user_id,
        title="New Booking Request!",
        message=f"New booking {booking.booking_code} received for {service.name} on {booking.scheduled_date} ({booking.scheduled_slot}).",
        notification_type="booking",
        link=f"/provider/bookings"
    ))

    db.commit()
    db.refresh(booking)
    return booking


@router.get("", response_model=List[BookingOut])
def get_user_bookings(
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(Booking).options(
        joinedload(Booking.service),
        joinedload(Booking.provider).joinedload(ServiceProvider.user),
        joinedload(Booking.customer).joinedload(Customer.user),
        joinedload(Booking.address),
        joinedload(Booking.payment),
        joinedload(Booking.invoice),
        joinedload(Booking.assignments).joinedload(BookingAssignment.technician).joinedload(Technician.user)
    )

    if current_user.role == "customer":
        customer = db.query(Customer).filter(Customer.user_id == current_user.id).first()
        if not customer:
            return []
        query = query.filter(Booking.customer_id == customer.id)
    elif current_user.role == "provider":
        provider = db.query(ServiceProvider).filter(ServiceProvider.user_id == current_user.id).first()
        if not provider:
            return []
        query = query.filter(Booking.provider_id == provider.id)
    elif current_user.role == "technician":
        tech = db.query(Technician).filter(Technician.user_id == current_user.id).first()
        if not tech:
            return []
        query = query.join(BookingAssignment).filter(BookingAssignment.technician_id == tech.id)
    # Admin sees all bookings!

    if status_filter:
        query = query.filter(Booking.status == status_filter)

    return query.order_by(Booking.created_at.desc()).all()


@router.get("/{booking_id}", response_model=BookingOut)
def get_booking_detail(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    booking = db.query(Booking).options(
        joinedload(Booking.service),
        joinedload(Booking.provider).joinedload(ServiceProvider.user),
        joinedload(Booking.customer).joinedload(Customer.user),
        joinedload(Booking.address),
        joinedload(Booking.payment),
        joinedload(Booking.invoice),
        joinedload(Booking.images),
        joinedload(Booking.review),
        joinedload(Booking.assignments).joinedload(BookingAssignment.technician).joinedload(Technician.user)
    ).filter(Booking.id == booking_id).first()

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Access control verification
    if current_user.role == "customer":
        if not booking.customer or booking.customer.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied: Not authorized to view this booking")
    elif current_user.role == "provider":
        if not booking.provider or booking.provider.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied: Not authorized to view this booking")
    elif current_user.role == "technician":
        tech = db.query(Technician).filter(Technician.user_id == current_user.id).first()
        is_assigned = any(a.technician_id == tech.id for a in booking.assignments) if tech else False
        if not is_assigned:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied: You are not assigned to this booking")

    return booking


@router.put("/{booking_id}/status")
def update_booking_status(
    booking_id: int,
    status_update: BookingStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    new_status = status_update.status.lower()
    allowed_statuses = ["pending", "confirmed", "provider_assigned", "in_progress", "completed", "cancelled", "rejected"]
    if new_status not in allowed_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Allowed: {allowed_statuses}")

    # Strict Role & Resource Ownership Permissions
    if current_user.role == "customer":
        if not booking.customer or booking.customer.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied: Cannot cancel another customer's booking.")
        if new_status != "cancelled":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Customers can only cancel bookings.")
        if booking.status in ["in_progress", "completed"]:
            raise HTTPException(status_code=400, detail="Cannot cancel booking once it is in progress or completed.")
        booking.cancellation_reason = status_update.reason or "Cancelled by customer"
    elif current_user.role == "provider":
        if not booking.provider or booking.provider.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied: Cannot update booking status belonging to another provider.")
    elif current_user.role == "technician":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Technicians cannot alter booking status directly; please use /technicians/me/jobs/{assignment_id}/status."
        )

    booking.status = new_status
    booking.updated_at = datetime.now(timezone.utc)

    # If completed, generate provider earning record if not already generated
    if new_status == "completed":
        existing_earning = db.query(ProviderEarning).filter(ProviderEarning.booking_id == booking.id).first()
        if not existing_earning:
            provider = db.query(ServiceProvider).filter(ServiceProvider.id == booking.provider_id).first()
            comm_rate = provider.commission_rate if provider else 15.0
            platform_fee = round((booking.final_amount * comm_rate) / 100.0, 2)
            net = round(booking.final_amount - platform_fee, 2)
            
            earning = ProviderEarning(
                provider_id=booking.provider_id,
                booking_id=booking.id,
                gross_amount=booking.final_amount,
                platform_commission_rate=comm_rate,
                platform_fee=platform_fee,
                net_earnings=net,
                payout_status="pending"
            )
            db.add(earning)

    # Notifications
    if booking.customer and booking.customer.user:
        db.add(Notification(
            user_id=booking.customer.user.id,
            title=f"Booking Status: {new_status.replace('_', ' ').title()}",
            message=f"Your booking {booking.booking_code} status has been updated to {new_status.replace('_', ' ')}.",
            notification_type="booking",
            link=f"/bookings/{booking.id}"
        ))

    db.commit()
    return {"message": f"Booking status updated to {new_status}", "status": new_status}


@router.put("/{booking_id}/reschedule")
def reschedule_booking(
    booking_id: int,
    reschedule_data: BookingReschedule,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Resource Ownership Validation
    if current_user.role == "customer":
        if not booking.customer or booking.customer.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied: Cannot reschedule another customer's booking.")
    elif current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied: Only the customer who booked or an administrator can reschedule.")

    if booking.status in ["in_progress", "completed", "cancelled"]:
        raise HTTPException(status_code=400, detail="Cannot reschedule this booking at its current stage.")

    # Check double booking on target slot
    slot_count = db.query(Booking).filter(
        Booking.provider_id == booking.provider_id,
        Booking.scheduled_date == reschedule_data.scheduled_date,
        Booking.scheduled_slot == reschedule_data.scheduled_slot,
        Booking.id != booking.id,
        Booking.status.notin_(["cancelled", "rejected"])
    ).count()

    if slot_count >= 2:
        raise HTTPException(status_code=409, detail="Selected slot is fully booked. Please choose another slot.")

    booking.scheduled_date = reschedule_data.scheduled_date
    booking.scheduled_slot = reschedule_data.scheduled_slot
    booking.updated_at = datetime.now(timezone.utc)
    db.commit()

    return {"message": "Booking rescheduled successfully", "scheduled_date": booking.scheduled_date, "scheduled_slot": booking.scheduled_slot}


@router.post("/{booking_id}/assign-technician")
def assign_technician(
    booking_id: int,
    assign_in: TechnicianAssignRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_provider)
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Resource Ownership Validation: Provider must own this booking
    if current_user.role != "admin":
        if not booking.provider or booking.provider.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied: Cannot assign technicians to another provider's booking.")

    technician = db.query(Technician).filter(Technician.id == assign_in.technician_id).first()
    if not technician:
        raise HTTPException(status_code=404, detail="Technician not found")

    # Create assignment
    assignment = BookingAssignment(
        booking_id=booking.id,
        technician_id=technician.id,
        status="assigned",
        technician_notes=assign_in.notes
    )
    db.add(assignment)
    booking.status = "provider_assigned"
    technician.status = "busy"

    # Notify technician & customer
    if technician.user:
        db.add(Notification(
            user_id=technician.user.id,
            title="New Job Assignment",
            message=f"You have been assigned to booking {booking.booking_code} for {booking.scheduled_date}.",
            notification_type="assignment"
        ))

    db.commit()
    return {"message": "Technician assigned successfully to booking"}
