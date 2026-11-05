from fastapi import APIRouter
from app.api.v1 import (
    auth, users, categories, services, providers,
    technicians, bookings, payments, reviews, complaints,
    coupons, notifications, analytics, uploads, rag
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication & RBAC"])
api_router.include_router(users.router, prefix="/users", tags=["Customer & User Management"])
api_router.include_router(categories.router, prefix="/categories", tags=["Service Categories"])
api_router.include_router(services.router, prefix="/services", tags=["Services Catalog"])
api_router.include_router(providers.router, prefix="/providers", tags=["Service Providers"])
api_router.include_router(technicians.router, prefix="/technicians", tags=["Technicians"])
api_router.include_router(bookings.router, prefix="/bookings", tags=["Bookings & Appointments"])
api_router.include_router(payments.router, prefix="/payments", tags=["Payments & Invoices"])
api_router.include_router(reviews.router, prefix="/reviews", tags=["Reviews & Ratings"])
api_router.include_router(complaints.router, prefix="/complaints", tags=["Complaints & Disputes"])
api_router.include_router(coupons.router, prefix="/coupons", tags=["Coupons & Discounts"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["In-App Notifications"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics & Reports"])
api_router.include_router(uploads.router, prefix="/uploads", tags=["File Uploads"])
api_router.include_router(rag.router, prefix="/rag", tags=["AI Knowledge Base & RAG Assistant"])
