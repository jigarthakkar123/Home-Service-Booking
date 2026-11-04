from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from app.core.database import get_db
from app.models.models import User, Customer, Address
from app.schemas.schemas import AddressCreate, AddressOut, UserOut
from app.api.deps import get_current_active_user, require_admin, require_customer

router = APIRouter()

@router.get("/admin/customers")
def get_all_customers_admin(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    customers = db.query(Customer).options(
        joinedload(Customer.user),
        joinedload(Customer.addresses),
        joinedload(Customer.bookings)
    ).all()
    
    results = []
    for c in customers:
        if c.user:
            results.append({
                "customer_id": c.id,
                "user_id": c.user.id,
                "name": f"{c.user.first_name} {c.user.last_name}",
                "email": c.user.email,
                "phone": c.user.phone,
                "is_active": c.user.is_active,
                "loyalty_points": c.loyalty_points,
                "total_bookings": len(c.bookings),
                "addresses_count": len(c.addresses),
                "created_at": c.created_at
            })
    return results


@router.put("/admin/{user_id}/status")
def toggle_user_status(
    user_id: int,
    is_active: bool,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot change your own account status")

    user.is_active = is_active
    db.commit()
    return {"message": f"User status set to {'active' if is_active else 'deactivated'}"}


@router.get("/addresses", response_model=List[AddressOut])
def get_my_addresses(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_customer)
):
    customer = db.query(Customer).filter(Customer.user_id == current_user.id).first()
    if not customer:
        return []
    return customer.addresses


@router.post("/addresses", response_model=AddressOut)
def add_address(
    addr_in: AddressCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_customer)
):
    customer = db.query(Customer).filter(Customer.user_id == current_user.id).first()
    if not customer:
        raise HTTPException(status_code=400, detail="Customer profile not found")

    if addr_in.is_default:
        # unset previous default
        db.query(Address).filter(Address.customer_id == customer.id).update({"is_default": False})

    new_addr = Address(
        customer_id=customer.id,
        title=addr_in.title,
        address_line=addr_in.address_line,
        city=addr_in.city,
        state=addr_in.state,
        postal_code=addr_in.postal_code,
        landmark=addr_in.landmark,
        is_default=addr_in.is_default
    )
    db.add(new_addr)
    db.commit()
    db.refresh(new_addr)
    return new_addr


@router.delete("/addresses/{address_id}")
def delete_address(
    address_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_customer)
):
    customer = db.query(Customer).filter(Customer.user_id == current_user.id).first()
    if not customer:
        raise HTTPException(status_code=400, detail="Customer profile not found")

    addr = db.query(Address).filter(Address.id == address_id, Address.customer_id == customer.id).first()
    if not addr:
        raise HTTPException(status_code=404, detail="Address not found")

    db.delete(addr)
    db.commit()
    return {"message": "Address deleted"}
