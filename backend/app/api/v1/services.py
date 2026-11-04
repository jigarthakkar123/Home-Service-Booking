from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
from app.core.database import get_db
from app.models.models import Service, ServiceCategory, ProviderService, ServiceProvider
from app.schemas.schemas import ServiceCreate, ServiceOut
from app.api.deps import require_admin, get_current_active_user

router = APIRouter()

@router.get("", response_model=List[ServiceOut])
def get_services(
    category_id: Optional[int] = None,
    category_slug: Optional[str] = None,
    search: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    query = db.query(Service).options(joinedload(Service.category)).filter(Service.is_active == True)
    
    if category_id:
        query = query.filter(Service.category_id == category_id)
    if category_slug:
        query = query.join(ServiceCategory).filter(ServiceCategory.slug == category_slug)
    if search:
        search_fmt = f"%{search}%"
        query = query.filter(
            (Service.name.ilike(search_fmt)) | 
            (Service.short_description.ilike(search_fmt)) |
            (Service.full_description.ilike(search_fmt))
        )
    if min_price is not None:
        query = query.filter(Service.base_price >= min_price)
    if max_price is not None:
        query = query.filter(Service.base_price <= max_price)

    return query.offset(skip).limit(limit).all()


@router.get("/{service_id_or_slug}")
def get_service_detail(service_id_or_slug: str, db: Session = Depends(get_db)):
    if service_id_or_slug.isdigit():
        service = db.query(Service).options(joinedload(Service.category)).filter(Service.id == int(service_id_or_slug)).first()
    else:
        service = db.query(Service).options(joinedload(Service.category)).filter(Service.slug == service_id_or_slug).first()

    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    # Also fetch providers offering this service
    provider_links = db.query(ProviderService).options(
        joinedload(ProviderService.provider).joinedload(ServiceProvider.user)
    ).filter(
        ProviderService.service_id == service.id,
        ProviderService.is_available == True
    ).all()

    providers_data = []
    for pl in provider_links:
        p = pl.provider
        if p and p.verification_status == "approved" and p.user and p.user.is_active:
            providers_data.append({
                "provider_id": p.id,
                "company_name": p.company_name,
                "rating_avg": p.rating_avg,
                "rating_count": p.rating_count,
                "experience_years": p.experience_years,
                "price": pl.custom_price if pl.custom_price else service.base_price
            })

    return {
        "id": service.id,
        "name": service.name,
        "slug": service.slug,
        "short_description": service.short_description,
        "full_description": service.full_description,
        "base_price": service.base_price,
        "duration_minutes": service.duration_minutes,
        "image_url": service.image_url,
        "category": {
            "id": service.category.id,
            "name": service.category.name,
            "slug": service.category.slug,
            "icon": service.category.icon
        } if service.category else None,
        "available_providers": providers_data
    }


@router.post("", response_model=ServiceOut)
def create_service(
    service_in: ServiceCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    slug = service_in.name.lower().replace(" ", "-").replace("&", "and")
    existing = db.query(Service).filter(Service.slug == slug).first()
    if existing:
        slug = f"{slug}-{service_in.category_id}"

    new_service = Service(
        category_id=service_in.category_id,
        name=service_in.name,
        slug=slug,
        short_description=service_in.short_description,
        full_description=service_in.full_description,
        base_price=service_in.base_price,
        duration_minutes=service_in.duration_minutes,
        image_url=service_in.image_url,
        is_active=True
    )
    db.add(new_service)
    db.commit()
    db.refresh(new_service)
    return new_service


@router.put("/{service_id}", response_model=ServiceOut)
def update_service(
    service_id: int,
    service_in: ServiceCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    service.category_id = service_in.category_id
    service.name = service_in.name
    service.short_description = service_in.short_description
    service.full_description = service_in.full_description
    service.base_price = service_in.base_price
    service.duration_minutes = service_in.duration_minutes
    if service_in.image_url:
        service.image_url = service_in.image_url
    
    db.commit()
    db.refresh(service)
    return service


@router.delete("/{service_id}")
def delete_service(
    service_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    db.delete(service)
    db.commit()
    return {"message": "Service deleted successfully"}
