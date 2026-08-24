"""Automated tests for Client Authentication, Security, Service Requests,
Payment Receipts, AI Generation, Admin Review, and Ownership Isolation.
"""

import pytest
from fastapi.testclient import TestClient

from app.core.auth import login_tracker
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_client_registration_and_profile(client):
    """Test registering a new client and accessing their profile."""
    reg_data = {
        "email": "solomon.client@example.com",
        "password": "SecurePassword123!",
        "full_name": "Solomon Client",
        "phone": "+251911998877",
        "address": "Bole, Addis Ababa",
        "education_level": "Bachelor's Degree",
    }
    res = client.post("/api/v1/auth/register", json=reg_data)
    assert res.status_code == 201
    data = res.json()
    assert data["email"] == "solomon.client@example.com"
    assert data["role"] == "client"
    token = data["access_token"]

    # Retrieve profile with Bearer token
    me_res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    me = me_res.json()
    assert me["full_name"] == "Solomon Client"
    assert me["phone"] == "+251911998877"

    # Update profile
    up_res = client.put(
        "/api/v1/auth/me",
        json={"address": "Kazanchis, Addis Ababa", "education_level": "Master's Degree"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert up_res.status_code == 200
    assert up_res.json()["address"] == "Kazanchis, Addis Ababa"


def test_brute_force_lockout_protection(client):
    """Test that 5 consecutive failed logins trigger rate limit lockout."""
    email = "target.user@example.com"
    # Reset tracker for this email
    login_tracker._attempts.clear()
    login_tracker._lockouts.clear()

    # Register first
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "CorrectPassword123!", "full_name": "Target User"},
    )

    # 5 failed attempts
    for _ in range(5):
        client.post("/api/v1/auth/login", json={"email": email, "password": "WrongPassword"})

    # 6th attempt should return HTTP 429 Too Many Requests
    blocked_res = client.post("/api/v1/auth/login", json={"email": email, "password": "WrongPassword"})
    assert blocked_res.status_code == 429
    assert "Too many failed login attempts" in blocked_res.json()["detail"]

    # Clear tracker for other tests
    login_tracker.record_success(f"127.0.0.1:{email}")


def test_password_reset_flow(client):
    """Test password reset request and confirm lifecycle."""
    email = "reset.user@example.com"
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "OldPassword123!", "full_name": "Reset User"},
    )

    # 1. Request reset
    req_res = client.post("/api/v1/auth/password-reset-request", json={"email": email})
    assert req_res.status_code == 200
    reset_token = req_res.json()["reset_token"]
    assert reset_token is not None

    # 2. Confirm reset
    conf_res = client.post(
        "/api/v1/auth/password-reset-confirm",
        json={"token": reset_token, "new_password": "NewPassword456!"},
    )
    assert conf_res.status_code == 200

    # 3. Login with new password
    login_res = client.post("/api/v1/auth/login", json={"email": email, "password": "NewPassword456!"})
    assert login_res.status_code == 200
    assert "access_token" in login_res.json()


def test_client_service_request_receipt_and_admin_ai_approval_flow(client):
    """Test the complete end-to-end client service and admin AI review workflow."""
    # 1. Register Client
    client_email = "applicant.beth@example.com"
    reg = client.post(
        "/api/v1/auth/register",
        json={"email": client_email, "password": "Password123!", "full_name": "Bethlehem Tadesse"},
    )
    client_token = reg.json()["access_token"]
    client_headers = {"Authorization": f"Bearer {client_token}"}

    # 2. Submit Visa Application
    visa_res = client.post(
        "/api/v1/visa/applications",
        json={
            "full_name": "Bethlehem Tadesse",
            "email": client_email,
            "phone": "+251911334455",
            "destination_country": "Germany",
            "visa_type": "Tourist",
            "passport_upload_url": "/uploads/passports/beth_passport.pdf",
            "advance_payment_method": "CBE",
            "advance_amount": 5000.0,
        },
        headers=client_headers,
    )
    assert visa_res.status_code == 201
    visa_data = visa_res.json()
    ref_code = visa_data["reference_code"]
    assert ref_code.startswith("ZAC-VIS-")

    # 3. Client checks Dashboard
    dash_res = client.get("/api/v1/client/dashboard", headers=client_headers)
    assert dash_res.status_code == 200
    dash_data = dash_res.json()
    assert dash_data["summary"]["total_requests"] >= 1

    # 4. Client uploads Payment Receipt
    receipt_res = client.post(
        f"/api/v1/client/requests/{ref_code}/receipt",
        json={
            "reference_code": ref_code,
            "payment_method": "CBE",
            "transaction_reference": "FT260823CBE991",
            "receipt_file_url": "/uploads/receipts/cbe_transfer_receipt.jpg",
            "amount": 5000.0,
            "notes": "Paid 5,000 ETB via CBE mobile banking.",
        },
        headers=client_headers,
    )
    assert receipt_res.status_code == 200
    assert receipt_res.json()["current_status"] == "PaymentUnderReview"

    # 5. Admin Logins & Views Review Queue
    admin_login = client.post("/api/v1/auth/login", json={"email": "admin@zacma.com", "password": "admin"})
    admin_token = admin_login.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    queue_res = client.get("/api/v1/admin/reviews/queue", headers=admin_headers)
    assert queue_res.status_code == 200
    queue = queue_res.json()
    target_in_queue = next((q for q in queue if q["reference_code"] == ref_code), None)
    assert target_in_queue is not None
    assert target_in_queue["has_receipt"] is True

    # 6. Admin Verifies Payment (Automatically triggers AI service generation)
    verify_res = client.post(
        f"/api/v1/admin/reviews/{ref_code}/verify-payment",
        json={"verified": True, "comment": "CBE transaction FT260823CBE991 confirmed."},
        headers=admin_headers,
    )
    assert verify_res.status_code == 200
    assert verify_res.json()["current_status"] == "PaymentApproved"
    assert verify_res.json()["ai_output_ready"] is True

    # 7. Admin Reviews & Approves Service Delivery with Feedback
    approve_res = client.post(
        f"/api/v1/admin/reviews/{ref_code}/approve-service",
        json={
            "status": "ServiceDelivered",
            "admin_response_message": "Visa strategy & official cover letter generated. Embassy appointment scheduled for Sept 15.",
        },
        headers=admin_headers,
    )
    assert approve_res.status_code == 200
    assert approve_res.json()["current_status"] == "ServiceDelivered"

    # 8. Client Fetches Request Detail & Reads AI Deliverable
    client_detail_res = client.get(f"/api/v1/client/requests/{ref_code}", headers=client_headers)
    assert client_detail_res.status_code == 200
    detail = client_detail_res.json()
    assert detail["status"] == "ServiceDelivered"
    assert detail["ai_generated_result"] is not None
    assert "cover_letter" in detail["ai_generated_result"]
    assert detail["admin_response"]["message"].startswith("Visa strategy & official cover letter")


def test_client_data_ownership_isolation(client):
    """Test that Client A cannot access Client B's private request records."""
    # Register Client A
    a_res = client.post(
        "/api/v1/auth/register",
        json={"email": "client.a@example.com", "password": "Password123!", "full_name": "Client A"},
    )
    token_a = a_res.json()["access_token"]

    # Register Client B
    b_res = client.post(
        "/api/v1/auth/register",
        json={"email": "client.b@example.com", "password": "Password123!", "full_name": "Client B"},
    )
    token_b = b_res.json()["access_token"]

    # Client A creates a request
    req_a = client.post(
        "/api/v1/travel/requests",
        json={
            "full_name": "Client A",
            "email": "client.a@example.com",
            "phone": "+251911001122",
            "destination_country": "Zanzibar",
            "travel_date_preference": "November 2026",
            "budget": 8000.0,
            "advance_payment_method": "TeleBirr",
            "advance_amount": 8000.0,
        },
        headers={"Authorization": f"Bearer {token_a}"},
    )
    ref_a = req_a.json()["reference_code"]

    # Client B attempts to fetch Client A's private request
    forbidden_res = client.get(
        f"/api/v1/client/requests/{ref_a}",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert forbidden_res.status_code == 403
    assert "Unauthorized" in forbidden_res.json()["detail"]
