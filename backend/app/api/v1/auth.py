import secrets
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_password_hash, verify_password, create_access_token
from app.models.models import User, Customer, ServiceProvider, Technician, Notification
from app.schemas.schemas import (
    Token, UserRegister, UserLogin, UserOut,
    PasswordResetRequest, PasswordResetConfirm, PasswordChange
)
from app.api.deps import get_current_active_user

router = APIRouter()

@router.post("/register", response_model=Token)
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    # Check if email exists
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists."
        )
    
    # Create User
    new_user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        role=user_in.role.lower(),
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        phone=user_in.phone,
        is_active=True,
        is_verified=True if user_in.role != "provider" else False
    )
    db.add(new_user)
    db.flush()

    # Create role specific profile
    if new_user.role == "customer":
        customer = Customer(user_id=new_user.id)
        db.add(customer)
    elif new_user.role == "provider":
        provider = ServiceProvider(
            user_id=new_user.id,
            company_name=user_in.company_name or f"{new_user.first_name}'s Home Services",
            business_registration_no=user_in.business_registration_no,
            bio=user_in.bio or "Certified Home Service Professional",
            experience_years=user_in.experience_years or 2,
            verification_status="pending"
        )
        db.add(provider)
    elif new_user.role == "technician":
        tech = Technician(
            user_id=new_user.id,
            specialization="General Maintenance",
            experience_years=1
        )
        db.add(tech)

    # Welcome notification
    welcome_notif = Notification(
        user_id=new_user.id,
        title="Welcome to HomeServe!",
        message=f"Welcome {new_user.first_name}! Your account has been registered successfully as a {new_user.role.title()}.",
        notification_type="system"
    )
    db.add(welcome_notif)
    db.commit()
    db.refresh(new_user)

    token = create_access_token(
        subject=new_user.id,
        extra_claims={"role": new_user.role, "email": new_user.email}
    )
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": new_user.role,
        "user_id": new_user.id,
        "name": f"{new_user.first_name} {new_user.last_name}",
        "email": new_user.email
    }


@router.post("/login", response_model=Token)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Account is deactivated. Please contact support.")

    token = create_access_token(
        subject=user.id,
        extra_claims={"role": user.role, "email": user.email}
    )
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user.role,
        "user_id": user.id,
        "name": f"{user.first_name} {user.last_name}",
        "email": user.email
    }


@router.get("/me")
def get_current_profile(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    profile_data = {
        "id": current_user.id,
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "phone": current_user.phone,
        "role": current_user.role,
        "is_active": current_user.is_active,
        "is_verified": current_user.is_verified,
        "created_at": current_user.created_at
    }

    if current_user.role == "customer" and current_user.customer_profile:
        profile_data["customer"] = {
            "id": current_user.customer_profile.id,
            "loyalty_points": current_user.customer_profile.loyalty_points,
            "addresses": [
                {
                    "id": addr.id,
                    "title": addr.title,
                    "address_line": addr.address_line,
                    "city": addr.city,
                    "state": addr.state,
                    "postal_code": addr.postal_code,
                    "landmark": addr.landmark,
                    "is_default": addr.is_default
                }
                for addr in current_user.customer_profile.addresses
            ]
        }
    elif current_user.role == "provider" and current_user.provider_profile:
        p = current_user.provider_profile
        profile_data["provider"] = {
            "id": p.id,
            "company_name": p.company_name,
            "business_registration_no": p.business_registration_no,
            "bio": p.bio,
            "experience_years": p.experience_years,
            "verification_status": p.verification_status,
            "verification_notes": p.verification_notes,
            "commission_rate": p.commission_rate,
            "rating_avg": p.rating_avg,
            "rating_count": p.rating_count
        }
    elif current_user.role == "technician" and current_user.technician_profile:
        t = current_user.technician_profile
        profile_data["technician"] = {
            "id": t.id,
            "provider_id": t.provider_id,
            "specialization": t.specialization,
            "experience_years": t.experience_years,
            "status": t.status
        }

    return profile_data


@router.post("/forgot-password")
def forgot_password(request: PasswordResetRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        # Avoid user enumeration by returning standard success message
        return {"message": "If this email exists, a password reset code has been sent."}
    
    token = secrets.token_hex(4).upper()  # e.g., "A3F8B2D1"
    user.reset_token = token
    db.commit()
    
    # In production this sends an email; for competition demo, return token in response as well for instant testing!
    return {
        "message": "Password reset token generated successfully.",
        "demo_reset_token": token
    }


@router.post("/reset-password")
def reset_password(data: PasswordResetConfirm, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not user.reset_token or user.reset_token != data.reset_token:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token.")
    
    user.hashed_password = get_password_hash(data.new_password)
    user.reset_token = None
    db.commit()
    return {"message": "Password has been reset successfully. You can now log in."}


@router.post("/change-password")
def change_password(
    data: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if not verify_password(data.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect.")
    
    current_user.hashed_password = get_password_hash(data.new_password)
    db.commit()
    return {"message": "Password changed successfully."}
