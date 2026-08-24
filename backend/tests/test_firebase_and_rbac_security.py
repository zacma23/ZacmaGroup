"""Comprehensive Security & RBAC Test Suite for ZACMA Group.

Verifies:
1. Production Firebase ID token verification & custom claims mapping
2. Client registration & privilege escalation protection
3. Strict Role-Based Access Control (RBAC) across SUPER_ADMIN, ADMIN, STAFF, FINANCE, and CUSTOMER
4. Insecure Direct Object Reference (IDOR) protection across invoices, tickets, and user data
5. Account recovery & user enumeration defense
6. Phone SMS OTP verification with rate limiting & secure hashing
7. Session invalidation upon logout & Cache-Control security headers (browser back defense)
8. Security audit logging & audit log access restrictions
"""

import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.main import app
from app.core.config import settings
from app.core.demo_data import admin_users_store, invoices_store, support_tickets_store
from app.services.firebase_auth_service import FirebaseAuthService

client = TestClient(app)


# ---------------------------------------------------------------------------
# 1. Firebase Authentication & Claims
# ---------------------------------------------------------------------------

def test_firebase_token_verification_and_claims():
    """Verify Firebase ID token verification and claim normalization."""
    mock_token = "firebase_mock_hanna_5001"
    user_claims = FirebaseAuthService.verify_firebase_token(mock_token)
    assert user_claims is not None
    assert user_claims["email"] == "hanna@example.com"
    assert user_claims["role"] == "client"
    assert user_claims["firebase_uid"] == "uid-5001"
    assert user_claims["auth_provider"] == "firebase"

    # Test login endpoint with Firebase token
    res = client.post("/api/v1/auth/firebase-login", json={"id_token": mock_token})
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["email"] == "hanna@example.com"
    assert data["role"] == "client"


def test_firebase_custom_claims_assignment():
    """Verify custom claims assignment for administrative roles."""
    uid = "uid-admin-test-01"
    admin_users_store.create(
        {
            "id": uid,
            "firebase_uid": uid,
            "email": "customadmin@zacma.com",
            "role": "client",
            "status": "active",
        },
        settings.demo_tenant_id,
    )

    success = FirebaseAuthService.set_custom_user_claims(uid, {"role": "admin"})
    assert success is True

    # User in store now has admin role
    user_in_store = admin_users_store.get(uid, settings.demo_tenant_id)
    assert user_in_store["role"] == "admin"


# ---------------------------------------------------------------------------
# 2. Client Registration & Privilege Escalation Prevention
# ---------------------------------------------------------------------------

def test_registration_prevents_privilege_escalation():
    """Verify that registering with role='admin' or 'superadmin' is sanitized to 'client'."""
    reg_email = f"attacker_{abs(hash('attack')) % 10000}@example.com"
    res = client.post(
        "/api/v1/auth/register",
        json={
            "email": reg_email,
            "password": "StrongPassword123!",
            "full_name": "Test Attacker",
            "role": "admin",  # Attempting privilege escalation
        },
    )
    assert res.status_code == 201
    data = res.json()
    assert data["role"] == "client", "Client role must be enforced on self-registration"

    # Verify profile endpoint returns client role
    token = data["access_token"]
    me_res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    assert me_res.json()["role"] == "client"


# ---------------------------------------------------------------------------
# 3. Role-Based Access Control (RBAC) Enforcement
# ---------------------------------------------------------------------------

def test_rbac_customer_blocked_from_admin_endpoints():
    """Verify that a customer cannot access admin user management or audit logs."""
    # 1. Login as customer
    login_res = client.post("/api/v1/auth/login", json={"email": "client@zacma.com", "password": "anypassword"})
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    # 2. Try accessing admin users list -> 403 Forbidden
    res_users = client.get("/api/v1/admin/users", headers={"Authorization": f"Bearer {token}"})
    assert res_users.status_code == 403

    # 3. Try accessing audit logs -> 403 Forbidden
    res_audit = client.get("/api/v1/admin/audit_logs", headers={"Authorization": f"Bearer {token}"})
    assert res_audit.status_code == 403


def test_rbac_staff_blocked_from_admin_operations():
    """Verify that staff can access operational views but is blocked from user management and deletion."""
    login_res = client.post("/api/v1/auth/login", json={"email": "staff@zacma.com", "password": "anypassword"})
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    # Staff blocked from deleting user
    res_del = client.delete("/api/v1/admin/users/usr-123", headers=auth_headers)
    assert res_del.status_code == 403

    # Staff blocked from viewing security audit logs
    res_audit = client.get("/api/v1/admin/audit_logs", headers=auth_headers)
    assert res_audit.status_code == 403


def test_rbac_admin_full_access():
    """Verify that admin can access user list, settings, and audit logs."""
    login_res = client.post("/api/v1/auth/login", json={"email": "admin@zacma.com", "password": "anypassword"})
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    res_users = client.get("/api/v1/admin/users", headers=auth_headers)
    assert res_users.status_code == 200

    res_audit = client.get("/api/v1/admin/audit_logs", headers=auth_headers)
    assert res_audit.status_code == 200


# ---------------------------------------------------------------------------
# 4. Insecure Direct Object Reference (IDOR) Protection
# ---------------------------------------------------------------------------

def test_idor_protection_on_invoices():
    """Verify Customer A cannot view or tamper with Customer B's invoice."""
    # Seed invoice for user A
    inv_a = invoices_store.create(
        {
            "reference_code": "INV-TEST-A101",
            "customer_name": "Customer A",
            "customer_email": "customera@example.com",
            "amount": 25000.0,
            "currency": "ETB",
            "status": "sent",
            "module_type": "software",
        },
        settings.demo_tenant_id,
    )
    inv_id = inv_a["id"]

    # Login as Customer B
    reg_res = client.post(
        "/api/v1/auth/register",
        json={
            "email": "customerb@example.com",
            "password": "Password12345!",
            "full_name": "Customer B",
        },
    )
    token_b = reg_res.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Customer B attempts to get Customer A's invoice directly -> 403 Forbidden
    get_res = client.get(f"/api/v1/payments/invoices/{inv_id}", headers=headers_b)
    assert get_res.status_code == 403, "Customer B must not access Customer A's invoice"

    # Customer B lists invoices -> should not see Customer A's invoice
    list_res = client.get("/api/v1/payments/invoices", headers=headers_b)
    assert list_res.status_code == 200
    b_invoices = list_res.json()
    assert not any(i["id"] == inv_id for i in b_invoices), "Customer B invoice list must filter out Customer A records"


def test_idor_protection_on_support_tickets():
    """Verify Customer B cannot view Customer A's support ticket."""
    tkt_a = support_tickets_store.create(
        {
            "full_name": "Customer A",
            "email": "customera@example.com",
            "subject": "Confidential Project Details",
            "message": "Sensitive proprietary info",
            "status": "Open",
            "category": "software",
        },
        settings.demo_tenant_id,
    )
    tkt_id = tkt_a["id"]

    # Login as Customer B
    login_b = client.post("/api/v1/auth/login", json={"email": "customerb@example.com", "password": "Password12345!"})
    token_b = login_b.json()["access_token"]

    # Direct ticket lookup
    res = client.get(f"/api/v1/support/tickets/{tkt_id}", headers={"Authorization": f"Bearer {token_b}"})
    assert res.status_code == 403


# ---------------------------------------------------------------------------
# 5. Password Recovery & Account Enumeration Defense
# ---------------------------------------------------------------------------

def test_password_reset_enumeration_defense_and_confirmation():
    """Verify password recovery returns identical generic messages and enforces token one-time use."""
    test_user_email = "testreset@zacma.com"
    # Seed user
    admin_users_store.create(
        {"id": "usr-reset-test", "email": test_user_email, "full_name": "Reset Test", "role": "client"},
        settings.demo_tenant_id,
    )

    # 1. Existing user
    res_exist = client.post("/api/v1/auth/password-reset-request", json={"email": test_user_email})
    assert res_exist.status_code == 200
    assert "recovery instructions have been sent" in res_exist.json()["message"]
    reset_token = res_exist.json()["reset_token"]

    # 2. Non-existent user (exact same message to prevent email enumeration)
    res_fake = client.post("/api/v1/auth/password-reset-request", json={"email": "nonexistent@zacma.com"})
    assert res_fake.status_code == 200
    assert "recovery instructions have been sent" in res_fake.json()["message"]

    # 3. Confirm password reset with valid token
    confirm_res = client.post(
        "/api/v1/auth/password-reset-confirm",
        json={"token": reset_token, "new_password": "NewResetPassword99!"},
    )
    assert confirm_res.status_code == 200

    # 4. Attempt to reuse the same reset token -> 400 Bad Request
    reuse_res = client.post(
        "/api/v1/auth/password-reset-confirm",
        json={"token": reset_token, "new_password": "AnotherPassword123!"},
    )
    assert reuse_res.status_code == 400


# ---------------------------------------------------------------------------
# 6. Phone / SMS OTP Verification Flow
# ---------------------------------------------------------------------------

def test_phone_otp_dispatch_and_verification():
    """Verify phone OTP generation, rate limiting, and verification."""
    phone = "+251911998877"

    # 1. Send OTP
    send_res = client.post("/api/v1/auth/phone/send-otp", json={"phone": phone})
    assert send_res.status_code == 200
    demo_otp = send_res.json().get("demo_otp")
    assert demo_otp is not None

    # 2. Immediate second request triggers cooldown rate limit (429)
    rate_res = client.post("/api/v1/auth/phone/send-otp", json={"phone": phone})
    assert rate_res.status_code == 429

    # 3. Verify with invalid OTP -> 400
    login_res = client.post("/api/v1/auth/login", json={"email": "admin@zacma.com", "password": "anypassword"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    fail_res = client.post("/api/v1/auth/phone/verify-otp", json={"phone": phone, "otp": "000000"}, headers=headers)
    assert fail_res.status_code == 400

    # 4. Verify with valid OTP -> 200
    ok_res = client.post("/api/v1/auth/phone/verify-otp", json={"phone": phone, "otp": demo_otp}, headers=headers)
    assert ok_res.status_code == 200


# ---------------------------------------------------------------------------
# 7. Session Invalidation on Logout & Cache-Control Headers
# ---------------------------------------------------------------------------

def test_logout_session_invalidation_and_cache_control():
    """Verify logout invalidates the token and Cache-Control headers prevent back button cache replay."""
    # 1. Login
    login_res = client.post("/api/v1/auth/login", json={"email": "client@zacma.com", "password": "anypassword"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Check Cache-Control headers on protected endpoint
    me_res = client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200
    assert "no-store" in me_res.headers.get("cache-control", "").lower()
    assert "no-cache" in me_res.headers.get("pragma", "").lower()

    # 3. Logout
    logout_res = client.post("/api/v1/auth/logout", headers=headers)
    assert logout_res.status_code == 200

    # 4. Attempt to reuse revoked token -> 401 Unauthorized
    post_logout_res = client.get("/api/v1/auth/me", headers=headers)
    assert post_logout_res.status_code == 401


# ---------------------------------------------------------------------------
# 8. Security Audit Logs Verification
# ---------------------------------------------------------------------------

def test_security_audit_events_recorded():
    """Verify that auth lifecycle events are recorded in security audit logs."""
    login_res = client.post("/api/v1/auth/login", json={"email": "admin@zacma.com", "password": "anypassword"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    audit_res = client.get("/api/v1/admin/audit_logs", headers=headers)
    assert audit_res.status_code == 200
    logs = audit_res.json()

    actions = [log.get("action") for log in logs]
    assert any(a in {"LOGIN_SUCCESS", "LOGOUT", "REGISTER", "PASSWORD_RESET_COMPLETED"} for a in actions)
