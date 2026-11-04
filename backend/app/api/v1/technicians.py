from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from app.core.database import get_db
from app.core.security import get_password_hash
from app.models.models import (
    Technician, User, ServiceProvider, BookingAssignment, Booking,
    BookingImage, Notification
)
from app.schemas.schemas import (
    TechnicianCreate, TechnicianOut, JobStatusUpdateRequest
)
from app.api.deps import require_provider, require_technician, get_current_active_user

router = APIRouter()

@router.get("", response_model=List[TechnicianOut])
def get_technicians_for_provider(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_provider)
):
    provider = db.query(ServiceProvider).filter(ServiceProvider.user_id == current_user.id).first()
    if not provider and current_user.role != "admin":
        raise HTTPException(status_code=400, detail="Provider profile not found")
    
    query = db.query(Technician).options(joinedload(Technician.user))
    if provider:
        query = query.filter(Technician.provider_id == provider.id)
    return query.all()


@router.post("", response_model=TechnicianOut)
def create_technician(
    tech_in: TechnicianCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_provider)
):
    provider = db.query(ServiceProvider).filter(ServiceProvider.user_id == current_user.id).first()
    if not provider:
        raise HTTPException(status_code=400, detail="Provider profile not found")
    
    existing = db.query(User).filter(User.email == tech_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        email=tech_in.email,
        hashed_password=get_password_hash(tech_in.password),
        role="technician",
        first_name=tech_in.first_name,
        last_name=tech_in.last_name,
        phone=tech_in.phone,
        is_active=True,
        is_verified=True
    )
    db.add(new_user)
    db.flush()

    new_tech = Technician(
        user_id=new_user.id,
        provider_id=provider.id,
        specialization=tech_in.specialization,
        experience_years=tech_in.experience_years,
        status="available"
    )
    db.add(new_tech)
    db.commit()
    db.refresh(new_tech)
    return new_tech


@router.get("/me/jobs")
def get_assigned_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_technician)
):
    tech = db.query(Technician).filter(Technician.user_id == current_user.id).first()
    if not tech:
        raise HTTPException(status_code=400, detail="Technician profile not found")
    
    assignments = db.query(BookingAssignment).options(
        joinedload(BookingAssignment.booking).joinedload(Booking.service),
        joinedload(BookingAssignment.booking).joinedload(Booking.address),
        joinedload(BookingAssignment.booking).joinedload(Booking.customer).joinedload(Customer.user)
    ).filter(BookingAssignment.technician_id == tech.id).order_by(BookingAssignment.assigned_at.desc()).all()

    jobs = []
    for a in assignments:
        b = a.booking
        jobs.append({
            "assignment_id": a.id,
            "assignment_status": a.status,
            "assigned_at": a.assigned_at,
            "arrival_at": a.arrival_at,
            "completed_at": a.completed_at,
            "technician_notes": a.technician_notes,
            "booking": {
                "id": b.id,
                "booking_code": b.booking_code,
                "status": b.status,
                "scheduled_date": b.scheduled_date,
                "scheduled_slot": b.scheduled_slot,
                "problem_description": b.problem_description,
                "service_name": b.service.name if b.service else None,
                "customer_name": f"{b.customer.user.first_name} {b.customer.user.last_name}" if b.customer and b.customer.user else "Customer",
                "customer_phone": b.customer.user.phone if b.customer and b.customer.user else None,
                "address": {
                    "line": b.address.address_line,
                    "city": b.address.city,
                    "state": b.address.state,
                    "postal_code": b.address.postal_code,
                    "landmark": b.address.landmark
                } if b.address else None
            }
        })
    return jobs


@router.put("/me/jobs/{assignment_id}/status")
def update_job_status(
    assignment_id: int,
    status_in: JobStatusUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_technician)
):
    tech = db.query(Technician).filter(Technician.user_id == current_user.id).first()
    if not tech:
        raise HTTPException(status_code=400, detail="Technician profile not found")
    
    assignment = db.query(BookingAssignment).filter(
        BookingAssignment.id == assignment_id,
        BookingAssignment.technician_id == tech.id
    ).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Job assignment not found")
    
    booking = assignment.booking
    now = datetime.now(timezone.utc)
    
    assignment.status = status_in.status
    if status_in.remarks:
        assignment.technician_notes = status_in.remarks

    if status_in.status == "arrived":
        assignment.arrival_at = now
        booking.status = "in_progress"
    elif status_in.status == "in_progress":
        booking.status = "in_progress"
    elif status_in.status == "completed":
        assignment.completed_at = now
        booking.status = "completed"
        tech.status = "available"

    # Save any completion images
    if status_in.completion_images:
        for img_url in status_in.completion_images:
            img = BookingImage(
                booking_id=booking.id,
                image_type="completion_proof",
                image_url=img_url,
                uploaded_by_role="technician"
            )
            db.add(img)

    # Notify customer & provider
    if booking.customer and booking.customer.user:
        notif = Notification(
            user_id=booking.customer.user.id,
            title=f"Service Update: {booking.booking_code}",
            message=f"Technician {current_user.first_name} marked status as '{status_in.status.upper()}'.",
            notification_type="booking",
            link=f"/bookings/{booking.id}"
        )
        db.add(notif)

    db.commit()
    return {"message": f"Job status updated to {status_in.status}"}
