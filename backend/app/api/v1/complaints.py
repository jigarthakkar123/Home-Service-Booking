from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from app.core.database import get_db
from app.models.models import Complaint, Booking, Customer, User, Notification
from app.schemas.schemas import ComplaintCreate, ComplaintResolution, ComplaintOut
from app.api.deps import get_current_active_user, require_customer, require_admin

router = APIRouter()

@router.post("", response_model=ComplaintOut)
def raise_complaint(
    comp_in: ComplaintCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_customer)
):
    customer = db.query(Customer).filter(Customer.user_id == current_user.id).first()
    if not customer:
        raise HTTPException(status_code=400, detail="Customer profile not found")

    booking = db.query(Booking).filter(
        Booking.id == comp_in.booking_id,
        Booking.customer_id == customer.id
    ).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    complaint = Complaint(
        booking_id=booking.id,
        customer_id=customer.id,
        provider_id=booking.provider_id,
        subject=comp_in.subject,
        description=comp_in.description,
        priority=comp_in.priority,
        status="open"
    )
    db.add(complaint)

    # In-app notification
    db.add(Notification(
        user_id=customer.user_id,
        title="Support Ticket Raised",
        message=f"Complaint regarding booking {booking.booking_code} received. Ticket #{complaint.id} opened.",
        notification_type="complaint"
    ))

    db.commit()
    db.refresh(complaint)
    return complaint


@router.get("", response_model=List[ComplaintOut])
def get_complaints(
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(Complaint)
    if current_user.role == "customer":
        customer = db.query(Customer).filter(Customer.user_id == current_user.id).first()
        if not customer:
            return []
        query = query.filter(Complaint.customer_id == customer.id)
    elif current_user.role == "provider":
        provider = current_user.provider_profile
        if not provider:
            return []
        query = query.filter(Complaint.provider_id == provider.id)

    if status_filter:
        query = query.filter(Complaint.status == status_filter)

    return query.order_by(Complaint.created_at.desc()).all()


@router.put("/admin/{complaint_id}/resolve")
def resolve_complaint(
    complaint_id: int,
    res_in: ComplaintResolution,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    comp = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not comp:
        raise HTTPException(status_code=404, detail="Complaint not found")

    comp.status = res_in.status
    comp.resolution_notes = res_in.resolution_notes
    if res_in.status in ["resolved", "closed"]:
        comp.resolved_at = datetime.now(timezone.utc)

    # Notify customer
    customer = db.query(Customer).filter(Customer.id == comp.customer_id).first()
    if customer and customer.user:
        db.add(Notification(
            user_id=customer.user.id,
            title=f"Complaint #{comp.id} {res_in.status.title()}",
            message=f"Your complaint regarding booking #{comp.booking_id} was updated: {res_in.resolution_notes}",
            notification_type="complaint"
        ))

    db.commit()
    return {"message": f"Complaint status updated to {res_in.status}"}
