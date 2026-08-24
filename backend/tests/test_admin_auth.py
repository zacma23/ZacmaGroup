"""Comprehensive test suite for admin-only authentication, authorization, token revocation, and route protection."""

import pytest
from datetime import timedelta
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings
from app.core.auth import create_access_token, decode_access_token, login_tracker


@pytest.fixture
def client():
    # Reset any lockout state before running tests
    login_tracker._attempts.clear()
    login_tracker._lockouts.clear()
    return TestClient(app)


def test_admin_login_success(client):
    """Test successful authentication with configured administrator credentials."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "zacma@admin",
            "password": "zacma@11",
            "remember_me": True,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["role"] == "admin"
    assert data["email"] == "zacma@admin"
    assert data["full_name"] == "Zacma Administrator"
    assert data["tenant_id"] == settings.demo_tenant_id

    # Verify session cookie was set
    assert settings.session_cookie_name in response.cookies


def test_admin_login_invalid_password(client):
    """Test administrator login rejection on wrong password."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "zacma@admin",
            "password": "wrongpassword123",
            "remember_me": False,
        },
    )
    assert response.status_code == 401
    data = response.json()
    assert "Invalid" in data["detail"]


def test_admin_login_brute_force_lockout(client):
    """Test sliding-window rate limit lockout for repeated failed login attempts."""
    rate_key = "testclient:zacma@admin"
    login_tracker._attempts.clear()
    login_tracker._lockouts.clear()

    # Fail max_attempts times
    for _ in range(5):
        res = client.post(
            "/api/v1/auth/login",
            json={"email": "zacma@admin", "password": "wrong_pass"},
        )
        assert res.status_code == 401

    # 6th attempt must be locked out with 429
    locked_res = client.post(
        "/api/v1/auth/login",
        json={"email": "zacma@admin", "password": "wrong_pass"},
    )
    assert locked_res.status_code == 429
    assert "Too many failed login attempts" in locked_res.json()["detail"]

    # Cleanup
    login_tracker._attempts.clear()
    login_tracker._lockouts.clear()


def test_unauthenticated_admin_endpoints_blocked(client):
    """Test that all admin API endpoints return 401 without authentication."""
    endpoints = [
        ("GET", "/api/v1/admin/users"),
        ("GET", "/api/v1/admin/stats"),
        ("GET", "/api/v1/admin/settings"),
        ("GET", "/api/v1/admin/tenants"),
        ("GET", "/api/v1/admin/audit_logs"),
        ("GET", "/api/v1/admin/reviews/queue"),
        ("GET", "/api/v1/dashboard/overview"),
        ("POST", "/api/v1/admin/modules"),
        ("POST", "/api/v1/submissions/custom/sub-001/approve"),
    ]

    for method, path in endpoints:
        if method == "GET":
            res = client.get(path)
        else:
            res = client.post(path, json={})
        assert res.status_code in [401, 403], f"Endpoint {path} was not protected (Status: {res.status_code})"


def test_client_role_cannot_access_admin_endpoints(client):
    """Test that an authenticated user with 'client' role is forbidden from admin endpoints (403)."""
    client_token = create_access_token(
        {
            "sub": "usr-client-001",
            "email": "client@example.com",
            "role": "client",
            "tenant_id": settings.demo_tenant_id,
            "full_name": "Client User",
        }
    )
    headers = {"Authorization": f"Bearer {client_token}"}

    res_users = client.get("/api/v1/admin/users", headers=headers)
    assert res_users.status_code == 403
    assert "Insufficient permissions" in res_users.json()["detail"]

    res_stats = client.get("/api/v1/admin/stats", headers=headers)
    assert res_stats.status_code == 403

    res_reviews = client.get("/api/v1/admin/reviews/queue", headers=headers)
    assert res_reviews.status_code == 403


def test_authenticated_admin_can_access_admin_endpoints(client):
    """Test that an authenticated admin token allows access to protected admin endpoints (200)."""
    admin_token = create_access_token(
        {
            "sub": "usr-admin-root",
            "email": "zacma@admin",
            "role": "admin",
            "tenant_id": settings.demo_tenant_id,
            "full_name": "Zacma Administrator",
        }
    )
    headers = {"Authorization": f"Bearer {admin_token}"}

    res_users = client.get("/api/v1/admin/users", headers=headers)
    assert res_users.status_code == 200

    res_stats = client.get("/api/v1/admin/stats", headers=headers)
    assert res_stats.status_code == 200
    assert "overview" in res_stats.json()

    res_settings = client.get("/api/v1/admin/settings", headers=headers)
    assert res_settings.status_code == 200

    res_reviews = client.get("/api/v1/admin/reviews/queue", headers=headers)
    assert res_reviews.status_code == 200

    res_overview = client.get("/api/v1/dashboard/overview", headers=headers)
    assert res_overview.status_code == 200


def test_admin_logout_revokes_token(client):
    """Test that logout explicitly revokes the JWT token, preventing any further access."""
    # 1. Login as admin
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "zacma@admin", "password": "zacma@11"},
    )
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Verify access works
    check_before = client.get("/api/v1/admin/users", headers=headers)
    assert check_before.status_code == 200

    # 3. Perform logout
    logout_res = client.post("/api/v1/auth/logout", headers=headers)
    assert logout_res.status_code == 200
    assert logout_res.json()["status"] == "success"

    # 4. Verify that the revoked token is immediately rejected on subsequent requests
    check_after = client.get("/api/v1/admin/users", headers=headers)
    assert check_after.status_code == 401


def test_expired_or_invalid_token_rejected(client):
    """Test that expired or tampered JWT tokens return 401 Unauthorized."""
    # Malformed token
    res_malformed = client.get(
        "/api/v1/admin/users",
        headers={"Authorization": "Bearer not.a.valid.jwt.token"},
    )
    assert res_malformed.status_code == 401

    # Expired token
    expired_token = create_access_token(
        {
            "sub": "usr-admin-root",
            "email": "zacma@admin",
            "role": "admin",
            "tenant_id": settings.demo_tenant_id,
        },
        expires_delta=timedelta(seconds=-10),  # expired in the past
    )
    res_expired = client.get(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert res_expired.status_code == 401


def test_admin_password_not_exposed(client):
    """Verify that the admin password is never returned in API profiles or user lists."""
    admin_token = create_access_token(
        {
            "sub": "usr-admin-root",
            "email": "zacma@admin",
            "role": "admin",
            "tenant_id": settings.demo_tenant_id,
        }
    )
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Check /auth/me
    me_res = client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200
    me_json = me_res.json()
    assert "password" not in me_json
    assert "password_hash" not in me_json
    assert "zacma@11" not in str(me_json)

    # Check /admin/users list
    users_res = client.get("/api/v1/admin/users", headers=headers)
    assert users_res.status_code == 200
    users_str = str(users_res.json())
    assert "password_hash" not in users_str
    assert "zacma@11" not in users_str


def test_existing_users_preserved(client):
    """Verify that existing users and client registration flows remain fully functional."""
    # Test client demo login
    res = client.post(
        "/api/v1/auth/login",
        json={"email": "client@zacma.com", "password": "any"},
    )
    assert res.status_code == 200
    assert res.json()["role"] == "client"

    # Test client registration
    unique_email = "new_client_test@example.com"
    reg_res = client.post(
        "/api/v1/auth/register",
        json={
            "email": unique_email,
            "password": "StrongPassword123!",
            "full_name": "Test Client User",
            "phone": "+251911998877",
            "role": "client",
        },
    )
    assert reg_res.status_code in [201, 409]
    if reg_res.status_code == 201:
        assert reg_res.json()["role"] == "client"
        assert reg_res.json()["email"] == unique_email
