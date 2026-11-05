import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.rate_limiter import rate_limiter

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_limiter_each_test():
    rate_limiter.reset()
    yield
    rate_limiter.reset()

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_login_admin():
    response = client.post("/api/v1/auth/login", json={
        "email": "admin@homeserve.com",
        "password": "Admin@123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["role"] == "admin"

def test_login_customer():
    response = client.post("/api/v1/auth/login", json={
        "email": "customer@homeserve.com",
        "password": "Customer@123"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "customer"

def test_login_provider():
    response = client.post("/api/v1/auth/login", json={
        "email": "provider@homeserve.com",
        "password": "Provider@123"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "provider"

def test_login_technician():
    response = client.post("/api/v1/auth/login", json={
        "email": "technician@homeserve.com",
        "password": "Technician@123"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "technician"

def test_invalid_login():
    response = client.post("/api/v1/auth/login", json={
        "email": "admin@homeserve.com",
        "password": "WrongPassword!"
    })
    assert response.status_code == 401

def test_get_categories():
    response = client.get("/api/v1/categories")
    assert response.status_code == 200
    categories = response.json()
    assert len(categories) >= 8
    slugs = [c["slug"] for c in categories]
    assert "electrical-services" in slugs
    assert "ac-repair-and-maintenance" in slugs

def test_get_services():
    response = client.get("/api/v1/services")
    assert response.status_code == 200
    services = response.json()
    assert len(services) > 0

def test_coupon_validation():
    # Test valid coupon
    response = client.get("/api/v1/coupons/validate/WELCOME50?amount=600")
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert data["discount_amount"] == 300.0  # 50% up to 300 cap

def test_coupon_minimum_amount_validation():
    # Test coupon with below minimum amount
    response = client.get("/api/v1/coupons/validate/WELCOME50?amount=200")
    assert response.status_code == 400

def test_customer_cannot_access_admin_metrics():
    # Login as customer
    login_resp = client.post("/api/v1/auth/login", json={
        "email": "customer@homeserve.com",
        "password": "Customer@123"
    })
    token = login_resp.json()["access_token"]
    
    # Try accessing admin analytics
    resp = client.get("/api/v1/analytics/admin", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 403

def test_admin_can_access_metrics():
    # Login as admin
    login_resp = client.post("/api/v1/auth/login", json={
        "email": "admin@homeserve.com",
        "password": "Admin@123"
    })
    token = login_resp.json()["access_token"]
    
    resp = client.get("/api/v1/analytics/admin", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert "kpis" in data
    assert "total_customers" in data["kpis"]

def test_booking_workflow_and_double_booking_prevention():
    import secrets
    # 1. Login as customer
    cust_login = client.post("/api/v1/auth/login", json={
        "email": "customer@homeserve.com",
        "password": "Customer@123"
    })
    cust_token = cust_login.json()["access_token"]
    cust_headers = {"Authorization": f"Bearer {cust_token}"}

    # 2. Get service and provider
    services_resp = client.get("/api/v1/services")
    service_id = services_resp.json()[0]["id"]
    providers_resp = client.get("/api/v1/providers")
    provider_id = providers_resp.json()[0]["id"]

    unique_run = secrets.token_hex(3)
    slot_date = f"2026-12-{unique_run}"
    slot_time = "10:00 - 12:00"

    # Create Booking 1
    resp1 = client.post("/api/v1/bookings", json={
        "service_id": service_id,
        "provider_id": provider_id,
        "scheduled_date": slot_date,
        "scheduled_slot": slot_time,
        "problem_description": "First test booking",
        "coupon_code": "WELCOME50"
    }, headers=cust_headers)
    assert resp1.status_code == 200
    booking1 = resp1.json()
    assert booking1["discount_amount"] > 0
    assert "HSB-2026-" in booking1["booking_code"]

    # Create Booking 2 (Same slot, capacity 2)
    resp2 = client.post("/api/v1/bookings", json={
        "service_id": service_id,
        "provider_id": provider_id,
        "scheduled_date": slot_date,
        "scheduled_slot": slot_time,
        "problem_description": "Second test booking"
    }, headers=cust_headers)
    assert resp2.status_code == 200

    # Create Booking 3 (Exceeds capacity of 2 -> Expect 409 Conflict)
    resp3 = client.post("/api/v1/bookings", json={
        "service_id": service_id,
        "provider_id": provider_id,
        "scheduled_date": slot_date,
        "scheduled_slot": slot_time,
        "problem_description": "Third booking - should be blocked"
    }, headers=cust_headers)
    assert resp3.status_code == 409
    assert "fully booked" in resp3.json()["detail"].lower()

def test_payment_and_invoice_generation():
    # Login as customer
    cust_login = client.post("/api/v1/auth/login", json={
        "email": "customer@homeserve.com",
        "password": "Customer@123"
    })
    cust_token = cust_login.json()["access_token"]
    cust_headers = {"Authorization": f"Bearer {cust_token}"}

    # Fetch customer bookings
    bookings_resp = client.get("/api/v1/bookings", headers=cust_headers)
    assert bookings_resp.status_code == 200
    bookings = bookings_resp.json()
    assert len(bookings) > 0
    test_booking = bookings[0]

    # Process Payment
    pay_resp = client.post("/api/v1/payments/process", json={
        "booking_id": test_booking["id"],
        "payment_gateway": "mock_sandbox"
    }, headers=cust_headers)
    assert pay_resp.status_code in [200, 400]  # 200 if fresh, 400 if already paid

    # Get Invoice
    inv_resp = client.get(f"/api/v1/payments/invoices/{test_booking['id']}", headers=cust_headers)
    assert inv_resp.status_code == 200
    inv = inv_resp.json()
    assert "INV-2026-" in inv["invoice_number"]
    assert inv["total_amount"] > 0

def test_technician_assigned_jobs_query():
    tech_login = client.post("/api/v1/auth/login", json={
        "email": "technician@homeserve.com",
        "password": "Technician@123"
    })
    token = tech_login.json()["access_token"]
    resp = client.get("/api/v1/technicians/me/jobs", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    jobs = resp.json()
    assert isinstance(jobs, list)

def test_provider_analytics_access():
    prov_login = client.post("/api/v1/auth/login", json={
        "email": "provider@homeserve.com",
        "password": "Provider@123"
    })
    token = prov_login.json()["access_token"]
    resp = client.get("/api/v1/analytics/provider", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert "total_bookings" in data

def test_user_profile_me():
    login_resp = client.post("/api/v1/auth/login", json={
        "email": "customer@homeserve.com",
        "password": "Customer@123"
    })
    token = login_resp.json()["access_token"]
    resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    profile = resp.json()
    assert profile["email"] == "customer@homeserve.com"
    assert profile["role"] == "customer"
    assert profile["is_active"] is True

def test_unauthenticated_request_rejected():
    resp = client.get("/api/v1/bookings")
    assert resp.status_code in [401, 403]

def test_service_detail_by_slug():
    resp = client.get("/api/v1/services/ac-deep-jet-servicing")
    assert resp.status_code == 200
    svc = resp.json()
    assert svc["slug"] == "ac-deep-jet-servicing"
    assert svc["base_price"] > 0

def test_customer_address_management():
    login_resp = client.post("/api/v1/auth/login", json={
        "email": "customer@homeserve.com",
        "password": "Customer@123"
    })
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Retrieve addresses
    resp = client.get("/api/v1/users/addresses", headers=headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

def test_review_retrieval():
    resp = client.get("/api/v1/reviews/provider/1")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

def test_complaints_retrieval():
    login_resp = client.post("/api/v1/auth/login", json={
        "email": "customer@homeserve.com",
        "password": "Customer@123"
    })
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.get("/api/v1/complaints", headers=headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

def test_notifications_retrieval():
    login_resp = client.post("/api/v1/auth/login", json={
        "email": "customer@homeserve.com",
        "password": "Customer@123"
    })
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.get("/api/v1/notifications", headers=headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

def test_razorpay_order_creation():
    login_resp = client.post("/api/v1/auth/login", json={
        "email": "customer@homeserve.com",
        "password": "Customer@123"
    })
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.post("/api/v1/payments/razorpay/create-order?booking_id=1", headers=headers)
    assert resp.status_code == 200
    order = resp.json()
    assert "order_id" in order
    assert order["currency"] == "INR"

def test_admin_export_csv():
    login_resp = client.post("/api/v1/auth/login", json={
        "email": "admin@homeserve.com",
        "password": "Admin@123"
    })
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.get("/api/v1/analytics/export/bookings/csv", headers=headers)
    assert resp.status_code == 200
    assert "text/csv" in resp.headers["content-type"]

def test_admin_registration_forbidden():
    # Attempt to register as admin must be blocked with HTTP 403
    resp = client.post("/api/v1/auth/register", json={
        "email": "hacker_admin@test.com",
        "password": "Password@123",
        "role": "admin",
        "first_name": "Malicious",
        "last_name": "Admin"
    })
    assert resp.status_code == 403
    assert "strictly prohibited" in resp.json()["detail"].lower()

def test_unauthenticated_upload_rejected():
    # Calling /api/v1/uploads without token must be blocked with HTTP 401
    import io
    file_content = b"fake image content"
    files = {"file": ("test.png", io.BytesIO(file_content), "image/png")}
    resp = client.post("/api/v1/uploads", files=files)
    assert resp.status_code == 401

def test_technician_cannot_alter_booking_status_directly():
    # Technician attempting to call PUT /api/v1/bookings/{id}/status must return HTTP 403
    tech_login = client.post("/api/v1/auth/login", json={
        "email": "technician@homeserve.com",
        "password": "Technician@123"
    })
    token = tech_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.put("/api/v1/bookings/1/status", json={"status": "completed"}, headers=headers)
    assert resp.status_code == 403

def test_forgot_password_does_not_leak_token():
    # Calling forgot-password must not return demo_reset_token in HTTP response
    resp = client.post("/api/v1/auth/forgot-password", json={"email": "customer@homeserve.com"})
    assert resp.status_code == 200
    data = resp.json()
    assert "demo_reset_token" not in data
    assert "expires_in_minutes" in data




import uuid
import hmac
import hashlib
from app.core.config import settings

def test_universal_demo_token_backdoor_rejected():
    # Attempting to use backdoor token "HSB-DEMO-2026" without a genuine reset request must be blocked with HTTP 400
    resp = client.post("/api/v1/auth/reset-password", json={
        "email": "admin@homeserve.com",
        "reset_token": "HSB-DEMO-2026",
        "new_password": "HackedPassword123!"
    })
    assert resp.status_code == 400
    assert "invalid or expired reset token" in resp.json()["detail"].lower()

def test_razorpay_signature_bypass_rejected():
    # Login as customer
    cust_login = client.post("/api/v1/auth/login", json={
        "email": "customer@homeserve.com",
        "password": "Customer@123"
    })
    token = cust_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Attempt verify with order_test_ and bogus signature -> must be strictly rejected with HTTP 400
    resp = client.post("/api/v1/payments/razorpay/verify", json={
        "booking_id": 1,
        "razorpay_order_id": "order_test_fake999",
        "razorpay_payment_id": "pay_fake123",
        "razorpay_signature": "invalid_garbage_signature"
    }, headers=headers)
    assert resp.status_code == 400
    assert "invalid razorpay cryptographic payment signature" in resp.json()["detail"].lower()

def test_cross_customer_invoice_access_forbidden():
    # Register an independent customer
    test_email = f"alice_{uuid.uuid4().hex[:6]}@example.com"
    reg_resp = client.post("/api/v1/auth/register", json={
        "first_name": "Alice",
        "last_name": "Tenant",
        "email": test_email,
        "password": "Password123!",
        "role": "customer"
    })
    assert reg_resp.status_code == 200
    alice_token = reg_resp.json()["access_token"]
    alice_headers = {"Authorization": f"Bearer {alice_token}"}

    # Attempt to fetch Booking 1 invoice (which belongs to customer@homeserve.com)
    inv_resp = client.get("/api/v1/payments/invoices/1", headers=alice_headers)
    assert inv_resp.status_code in [403, 404]

def test_rate_limiter_active_on_responses():
    # Verify rate limiter injects standard tracking headers
    resp = client.get("/api/v1/categories")
    assert resp.status_code == 200
    assert "X-RateLimit-Remaining" in resp.headers
