import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

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

