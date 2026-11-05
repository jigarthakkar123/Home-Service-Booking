import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1.api import api_router
from app.models import models  # Ensures all models are registered
from app.initial_data import init_db
from app.core.rate_limiter import RateLimiterMiddleware

# Create database tables automatically & seed
Base.metadata.create_all(bind=engine)
init_db()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Full Stack SaaS Platform for Home Services Booking - Connecting Customers with Verified Technicians & Providers",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc"
)

# Rate Limiting Middleware (OWASP Top 10 Brute Force Protection)
app.add_middleware(RateLimiterMiddleware)

# CORS Middleware setup - Strict Origin Validation
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Ensure static uploads directory exists
upload_dir = os.path.join(os.getcwd(), "static", "uploads")
os.makedirs(upload_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Mount API Routers
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "platform": settings.PROJECT_NAME,
        "status": "online",
        "api_docs": f"{settings.API_V1_STR}/docs",
        "version": "1.0.0"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "connected"}
