from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import ServiceCategory, Service
from app.schemas.schemas import CategoryCreate, CategoryOut
from app.api.deps import require_admin, get_current_active_user

router = APIRouter()

@router.get("", response_model=List[CategoryOut])
def get_categories(db: Session = Depends(get_db)):
    categories = db.query(ServiceCategory).filter(ServiceCategory.is_active == True).order_by(ServiceCategory.sort_order).all()
    return categories

@router.get("/all", response_model=List[CategoryOut])
def get_all_categories_admin(db: Session = Depends(get_db), current_user=Depends(require_admin)):
    categories = db.query(ServiceCategory).order_by(ServiceCategory.sort_order).all()
    return categories

@router.post("", response_model=CategoryOut)
def create_category(
    category_in: CategoryCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    slug = category_in.name.lower().replace(" ", "-").replace("&", "and")
    existing = db.query(ServiceCategory).filter(ServiceCategory.slug == slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="A category with this name already exists.")

    new_cat = ServiceCategory(
        name=category_in.name,
        slug=slug,
        description=category_in.description,
        icon=category_in.icon or "Wrench",
        image_url=category_in.image_url,
        sort_order=category_in.sort_order,
        is_active=True
    )
    db.add(new_cat)
    db.commit()
    db.refresh(new_cat)
    return new_cat

@router.put("/{cat_id}", response_model=CategoryOut)
def update_category(
    cat_id: int,
    category_in: CategoryCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    cat = db.query(ServiceCategory).filter(ServiceCategory.id == cat_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found.")
    
    cat.name = category_in.name
    cat.slug = category_in.name.lower().replace(" ", "-").replace("&", "and")
    cat.description = category_in.description
    cat.icon = category_in.icon
    cat.image_url = category_in.image_url
    cat.sort_order = category_in.sort_order
    db.commit()
    db.refresh(cat)
    return cat

@router.delete("/{cat_id}")
def delete_category(
    cat_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    cat = db.query(ServiceCategory).filter(ServiceCategory.id == cat_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found.")
    
    db.delete(cat)
    db.commit()
    return {"message": "Category deleted successfully"}
