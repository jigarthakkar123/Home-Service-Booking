from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import Coupon, User
from app.schemas.schemas import CouponCreate, CouponOut
from app.api.deps import require_admin, get_current_active_user

router = APIRouter()

@router.get("", response_model=List[CouponOut])
def get_active_coupons(db: Session = Depends(get_db)):
    return db.query(Coupon).filter(Coupon.is_active == True).all()

@router.get("/admin/all", response_model=List[CouponOut])
def get_all_coupons_admin(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    return db.query(Coupon).all()

@router.post("", response_model=CouponOut)
def create_coupon(
    coupon_in: CouponCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    existing = db.query(Coupon).filter(Coupon.code == coupon_in.code.upper()).first()
    if existing:
        raise HTTPException(status_code=400, detail="Coupon code already exists")

    coupon = Coupon(
        code=coupon_in.code.upper(),
        description=coupon_in.description,
        discount_type=coupon_in.discount_type,
        discount_value=coupon_in.discount_value,
        min_booking_amount=coupon_in.min_booking_amount,
        max_discount=coupon_in.max_discount,
        usage_limit=coupon_in.usage_limit,
        is_active=coupon_in.is_active
    )
    db.add(coupon)
    db.commit()
    db.refresh(coupon)
    return coupon

@router.get("/validate/{code}")
def validate_coupon(code: str, amount: float = 0.0, db: Session = Depends(get_db)):
    coupon = db.query(Coupon).filter(Coupon.code == code.upper(), Coupon.is_active == True).first()
    if not coupon:
        raise HTTPException(status_code=404, detail="Invalid coupon code")
    
    if amount < coupon.min_booking_amount:
        raise HTTPException(
            status_code=400,
            detail=f"Minimum booking amount for this coupon is ₹{coupon.min_booking_amount}"
        )
    
    if coupon.discount_type == "percentage":
        discount = round((amount * coupon.discount_value) / 100.0, 2)
        if coupon.max_discount and discount > coupon.max_discount:
            discount = coupon.max_discount
    else:
        discount = min(coupon.discount_value, amount)

    return {
        "valid": True,
        "code": coupon.code,
        "discount_amount": discount,
        "final_amount": max(0.0, round(amount - discount, 2))
    }
