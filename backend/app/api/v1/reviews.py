from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from app.core.database import get_db
from app.models.models import Review, Booking, Customer, ServiceProvider, User, Notification
from app.schemas.schemas import ReviewCreate, ReviewReply, ReviewOut
from app.api.deps import get_current_active_user, require_customer, require_provider, require_admin

router = APIRouter()

@router.post("", response_model=ReviewOut)
def create_review(
    review_in: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_customer)
):
    customer = db.query(Customer).filter(Customer.user_id == current_user.id).first()
    if not customer:
        raise HTTPException(status_code=400, detail="Customer profile not found")

    booking = db.query(Booking).filter(
        Booking.id == review_in.booking_id,
        Booking.customer_id == customer.id
    ).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found or does not belong to you")
    
    if booking.status != "completed":
        raise HTTPException(status_code=400, detail="You can only review completed service bookings")

    existing = db.query(Review).filter(Review.booking_id == booking.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="You have already submitted a review for this booking")

    review = Review(
        booking_id=booking.id,
        customer_id=customer.id,
        provider_id=booking.provider_id,
        rating=review_in.rating,
        comment=review_in.comment,
        is_moderated=True
    )
    db.add(review)

    # Re-calculate provider average rating
    provider = db.query(ServiceProvider).filter(ServiceProvider.id == booking.provider_id).first()
    if provider:
        all_ratings = [r.rating for r in db.query(Review).filter(Review.provider_id == provider.id).all()]
        all_ratings.append(review_in.rating)
        provider.rating_count = len(all_ratings)
        provider.rating_avg = round(sum(all_ratings) / len(all_ratings), 1)

        # Notify provider
        db.add(Notification(
            user_id=provider.user_id,
            title="New Customer Review",
            message=f"A customer gave you a {review_in.rating}-star review for booking {booking.booking_code}.",
            notification_type="booking",
            link="/provider/reviews"
        ))

    db.commit()
    db.refresh(review)
    return review


@router.get("/provider/{provider_id}", response_model=List[ReviewOut])
def get_provider_reviews(provider_id: int, db: Session = Depends(get_db)):
    reviews = db.query(Review).options(
        joinedload(Review.customer).joinedload(Customer.user)
    ).filter(
        Review.provider_id == provider_id,
        Review.is_moderated == True
    ).order_by(Review.created_at.desc()).all()
    return reviews


@router.put("/{review_id}/reply")
def reply_to_review(
    review_id: int,
    reply_in: ReviewReply,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_provider)
):
    provider = db.query(ServiceProvider).filter(ServiceProvider.user_id == current_user.id).first()
    if not provider:
        raise HTTPException(status_code=400, detail="Provider profile not found")

    review = db.query(Review).filter(
        Review.id == review_id,
        Review.provider_id == provider.id
    ).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    review.provider_reply = reply_in.reply
    db.commit()
    return {"message": "Reply posted successfully"}
