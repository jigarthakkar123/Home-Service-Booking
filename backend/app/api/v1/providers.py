from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from app.core.database import get_db
from app.models.models import (
    ServiceProvider, User, ProviderService, ServiceArea, AvailabilitySlot,
    Service, ProviderEarning, Notification
)
from app.schemas.schemas import (
    ProviderOut, ProviderVerificationUpdate, ProviderServiceAreaCreate,
    ProviderServiceAreaOut, AvailabilitySlotCreate, AvailabilitySlotOut
)
from app.api.deps import require_admin, require_provider, get_current_active_user

router = APIRouter()

@router.get("", response_model=List[ProviderOut])
def get_verified_providers(
    city: Optional[str] = None,
    service_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(ServiceProvider).options(joinedload(ServiceProvider.user)).filter(
        ServiceProvider.verification_status == "approved"
    )
    if city:
        query = query.join(ServiceArea).filter(ServiceArea.city.ilike(f"%{city}%"))
    if service_id:
        query = query.join(ProviderService).filter(
            ProviderService.service_id == service_id,
            ProviderService.is_available == True
        )
    return query.all()


@router.get("/admin/all")
def get_all_providers_admin(
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    query = db.query(ServiceProvider).options(joinedload(ServiceProvider.user))
    if status_filter:
        query = query.filter(ServiceProvider.verification_status == status_filter)
    
    providers = query.all()
    results = []
    for p in providers:
        results.append({
            "id": p.id,
            "user_id": p.user_id,
            "company_name": p.company_name,
            "business_registration_no": p.business_registration_no,
            "bio": p.bio,
            "experience_years": p.experience_years,
            "verification_status": p.verification_status,
            "verification_notes": p.verification_notes,
            "id_proof_url": p.id_proof_url,
            "business_proof_url": p.business_proof_url,
            "commission_rate": p.commission_rate,
            "rating_avg": p.rating_avg,
            "rating_count": p.rating_count,
            "user": {
                "id": p.user.id,
                "email": p.user.email,
                "first_name": p.user.first_name,
                "last_name": p.user.last_name,
                "phone": p.user.phone,
                "is_active": p.user.is_active
            } if p.user else None
        })
    return results


@router.get("/{provider_id}")
def get_provider_details(provider_id: int, db: Session = Depends(get_db)):
    provider = db.query(ServiceProvider).options(
        joinedload(ServiceProvider.user),
        joinedload(ServiceProvider.service_areas),
        joinedload(ServiceProvider.availability_slots),
        joinedload(ServiceProvider.services).joinedload(ProviderService.service)
    ).filter(ServiceProvider.id == provider_id).first()

    if not provider:
        raise HTTPException(status_code=404, detail="Service provider not found")
    
    return {
        "id": provider.id,
        "company_name": provider.company_name,
        "bio": provider.bio,
        "experience_years": provider.experience_years,
        "rating_avg": provider.rating_avg,
        "rating_count": provider.rating_count,
        "verification_status": provider.verification_status,
        "user": {
            "name": f"{provider.user.first_name} {provider.user.last_name}",
            "email": provider.user.email,
            "phone": provider.user.phone
        } if provider.user else None,
        "services": [
            {
                "service_id": ps.service.id,
                "name": ps.service.name,
                "base_price": ps.service.base_price,
                "custom_price": ps.custom_price,
                "is_available": ps.is_available
            } for ps in provider.services if ps.service
        ],
        "service_areas": [
            {"city": a.city, "postal_code": a.postal_code, "radius_km": a.radius_km}
            for a in provider.service_areas
        ],
        "availability_slots": [
            {
                "day_of_week": s.day_of_week,
                "start_time": s.start_time,
                "end_time": s.end_time,
                "slot_capacity": s.slot_capacity,
                "is_active": s.is_active
            } for s in provider.availability_slots if s.is_active
        ]
    }


@router.put("/admin/{provider_id}/verify")
def verify_provider(
    provider_id: int,
    verif_in: ProviderVerificationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    provider = db.query(ServiceProvider).filter(ServiceProvider.id == provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    provider.verification_status = verif_in.status
    if verif_in.notes:
        provider.verification_notes = verif_in.notes
    if verif_in.commission_rate is not None:
        provider.commission_rate = verif_in.commission_rate
    
    # Notify provider user
    notif = Notification(
        user_id=provider.user_id,
        title=f"Verification Update: {verif_in.status.upper()}",
        message=f"Your service provider account has been marked as '{verif_in.status}'. Notes: {verif_in.notes or 'No additional notes'}",
        notification_type="system"
    )
    db.add(notif)
    db.commit()
    return {"message": f"Provider status updated to {verif_in.status}"}


@router.post("/services/link")
def link_service_to_provider(
    service_id: int,
    custom_price: Optional[float] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_provider)
):
    provider = db.query(ServiceProvider).filter(ServiceProvider.user_id == current_user.id).first()
    if not provider:
        raise HTTPException(status_code=400, detail="Provider profile not found")
    
    existing = db.query(ProviderService).filter(
        ProviderService.provider_id == provider.id,
        ProviderService.service_id == service_id
    ).first()

    if existing:
        existing.custom_price = custom_price
        existing.is_available = True
    else:
        new_ps = ProviderService(
            provider_id=provider.id,
            service_id=service_id,
            custom_price=custom_price,
            is_available=True
        )
        db.add(new_ps)
    db.commit()
    return {"message": "Service linked successfully to your profile"}


@router.post("/slots")
def add_availability_slot(
    slot_in: AvailabilitySlotCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_provider)
):
    provider = db.query(ServiceProvider).filter(ServiceProvider.user_id == current_user.id).first()
    if not provider:
        raise HTTPException(status_code=400, detail="Provider profile not found")
    
    slot = AvailabilitySlot(
        provider_id=provider.id,
        day_of_week=slot_in.day_of_week,
        start_time=slot_in.start_time,
        end_time=slot_in.end_time,
        slot_capacity=slot_in.slot_capacity,
        is_active=True
    )
    db.add(slot)
    db.commit()
    db.refresh(slot)
    return slot


@router.post("/areas")
def add_service_area(
    area_in: ProviderServiceAreaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_provider)
):
    provider = db.query(ServiceProvider).filter(ServiceProvider.user_id == current_user.id).first()
    if not provider:
        raise HTTPException(status_code=400, detail="Provider profile not found")
    
    area = ServiceArea(
        provider_id=provider.id,
        city=area_in.city,
        postal_code=area_in.postal_code,
        radius_km=area_in.radius_km
    )
    db.add(area)
    db.commit()
    db.refresh(area)
    return area


@router.get("/me/earnings")
def get_my_earnings(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_provider)
):
    provider = db.query(ServiceProvider).filter(ServiceProvider.user_id == current_user.id).first()
    if not provider:
        raise HTTPException(status_code=400, detail="Provider profile not found")
    
    earnings = db.query(ProviderEarning).filter(ProviderEarning.provider_id == provider.id).all()
    total_gross = sum(e.gross_amount for e in earnings)
    total_commission = sum(e.platform_fee for e in earnings)
    total_net = sum(e.net_earnings for e in earnings)
    
    return {
        "provider_id": provider.id,
        "total_gross": round(total_gross, 2),
        "total_commission_paid": round(total_commission, 2),
        "total_net_earnings": round(total_net, 2),
        "records": [
            {
                "id": e.id,
                "booking_id": e.booking_id,
                "gross_amount": e.gross_amount,
                "platform_fee": e.platform_fee,
                "net_earnings": e.net_earnings,
                "payout_status": e.payout_status,
                "created_at": e.created_at
            } for e in earnings
        ]
    }
