import os
import secrets
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
DEFAULT_DB_FILE = BACKEND_DIR / "homeserve.db"
DEFAULT_DB_URL = f"sqlite:///{DEFAULT_DB_FILE.as_posix()}"

# Read strictly from environment variable. If not set, generate a cryptographically strong
# ephemeral 256-bit random key at runtime to eliminate hardcoded secrets in the codebase.
_env_secret = os.getenv("SECRET_KEY") or os.getenv("JWT_SECRET_KEY")
ACTIVE_SECRET_KEY = _env_secret if _env_secret else secrets.token_hex(32)

class Settings(BaseSettings):
    PROJECT_NAME: str = "HomeServe Technologies SaaS Platform"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = ACTIVE_SECRET_KEY
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours (Strict OWASP standard)

    # Database: Supports Cloud MySQL (Aiven, TiDB, Render, Supabase, PlanetScale) or local SQLite fallback
    # e.g., mysql+pymysql://user:pass@host:3306/dbname
    DATABASE_URL: str = os.getenv("DATABASE_URL", DEFAULT_DB_URL)

    # Payment Integration (Razorpay Test Mode or simulated fallback)
    RAZORPAY_KEY_ID: str = os.getenv("RAZORPAY_KEY_ID", "rzp_test_placeholder_key")
    RAZORPAY_KEY_SECRET: str = os.getenv("RAZORPAY_KEY_SECRET", "rzp_test_placeholder_secret")

    # SMTP Email Configuration for Password Reset & Transactional Notifications
    SMTP_HOST: str = os.getenv("SMTP_HOST", "")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    EMAILS_FROM_EMAIL: str = os.getenv("EMAILS_FROM_EMAIL", "noreply@homeserve.com")
    EMAILS_FROM_NAME: str = os.getenv("EMAILS_FROM_NAME", "HomeServe Platform")

    # Platform default commission percentage
    DEFAULT_COMMISSION_PERCENTAGE: float = 15.0

    # CORS origins: Explicit production domain & local environments
    BACKEND_CORS_ORIGINS: List[str] = [
        "https://homeservicebooking.netlify.app",
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:4173",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000"
    ]

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
