import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
DEFAULT_DB_FILE = BACKEND_DIR / "homeserve.db"
DEFAULT_DB_URL = f"sqlite:///{DEFAULT_DB_FILE.as_posix()}"

class Settings(BaseSettings):
    PROJECT_NAME: str = "HomeServe Technologies SaaS Platform"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-jwt-key-for-homeserve-saas-platform-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Database: Supports Cloud MySQL (Aiven, TiDB, Render, Supabase, PlanetScale) or local SQLite fallback
    # e.g., mysql+pymysql://user:pass@host:3306/dbname
    DATABASE_URL: str = os.getenv("DATABASE_URL", DEFAULT_DB_URL)

    # Payment Integration (Razorpay Test Mode or simulated fallback)
    RAZORPAY_KEY_ID: str = os.getenv("RAZORPAY_KEY_ID", "rzp_test_placeholder_key")
    RAZORPAY_KEY_SECRET: str = os.getenv("RAZORPAY_KEY_SECRET", "rzp_test_placeholder_secret")

    # Platform default commission percentage
    DEFAULT_COMMISSION_PERCENTAGE: float = 15.0

    # CORS origins
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:4173",
        "http://127.0.0.1:5173",
        "https://*.netlify.app",
        "https://*.onrender.com",
        "*"
    ]

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
