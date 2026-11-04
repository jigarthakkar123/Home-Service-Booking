# Security Implementation & Checklist

## Overview
HomeServe Technologies implements defense-in-depth security principles across backend REST endpoints and frontend user experiences.

---

## Security Verification Checklist

| Security Requirement | Status | Implementation Details |
|----------------------|--------|------------------------|
| **Password Hashing** | ✅ Verified | Salted one-way hashing via `bcrypt` / `passlib`. Plain text passwords are never stored or logged. |
| **JWT Authentication** | ✅ Verified | Secure access tokens encoded using HMAC-SHA256 (`HS256`) with expiration and role claims. |
| **Role-Based Access Control (RBAC)** | ✅ Verified | Enforced via FastAPI dependencies (`require_admin`, `require_provider`, `require_technician`, `require_customer`). |
| **Resource Isolation** | ✅ Verified | Customers can only access their own bookings, invoices, and addresses. Providers can only view their assigned dispatches. |
| **Double Booking Prevention** | ✅ Verified | Capacity and slot locks checked within database transactions, rejecting conflicting reservations with HTTP 409 Conflict. |
| **SQL Injection Protection** | ✅ Verified | All queries executed using SQLAlchemy ORM parameterized statements. No raw string interpolation. |
| **CORS Restriction** | ✅ Verified | Configurable `BACKEND_CORS_ORIGINS` restricting authorized frontend domains in production. |
| **File Upload Validation** | ✅ Verified | Whitelisted file extensions (`.jpg`, `.jpeg`, `.png`, `.webp`, `.pdf`), maximum 10MB file limit, and cryptographically randomized storage filenames. |
| **Sensitive Configuration Security** | ✅ Verified | Secrets, database credentials, and payment API keys managed strictly via environment variables (`.env`). |
| **Error Masking** | ✅ Verified | Generic error messages returned to clients to prevent database or stack trace enumeration. |
| **Payment Verification** | ✅ Verified | Tamper-proof payment processing verifying transaction signatures and server-side payment state. |
| **Password Reset Tokenization** | ✅ Verified | Cryptographically secure pseudo-random hex tokens with single-use verification. |

---

## Testing RBAC Security
Automated unit tests in `tests/test_api.py` verify that attempting to access a privileged endpoint without adequate role credentials triggers an immediate `HTTP 403 Forbidden` response.
