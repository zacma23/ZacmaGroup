"""Comprehensive test suite for Supabase Authentication, database-backed RBAC, and role enforcement."""

import pytest
from datetime import timedelta
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings
from app.core.auth import create_access_token, decode_access_token, login_tracker
from app.services.supabase_auth_service import SupabaseAuthService


@pytest.fixture
def client():
    login_tracker._attempts.clear()
    login_tracker._lockouts.clear()
    return TestClient(app)


def test_supabase_service_admin_authenticate():
    """Test SupabaseAuthService authenticating administrator with database role 'admin'."""
    auth_data = SupabaseAuthService.authenticate(
        email="zacma@admin",
        password="zacma@11",
        remember_me=True,
    )
    assert auth_data is not None
    assert auth_data["role"] == "admin"
    assert auth_data["email"] == "zacma@admin"
    assert "access_token" in auth_data

    # Verify decoded token contains database role
    payload = decode_access_token(auth_data["access_token"])
    assert payload is not None
    assert payload["role"] == "admin"
    assert payload["email"] == "zacma@admin"


def test_supabase_service_admin_invalid_password():
    """Test SupabaseAuthService rejecting invalid administrator password with 401."""
    with pytest.raises(Exception) as exc_info:
        SupabaseAuthService.authenticate(
            email="zacma@admin",
            password="incorrect_password",
        )
    assert "401" in str(exc_info.value) or "Invalid" in str(exc_info.value)


def test_supabase_service_user_registration_and_privilege_escalation_defense():
    """Test SupabaseAuthService user registration and privilege escalation defense."""
    test_email = "supabase_client_test@zacma.com"
    reg_data = SupabaseAuthService.register(
        email=test_email,
        password="ValidPassword123!",
        full_name="Supabase Test Client",
        phone="+251911223344",
        role="admin",  # Attempt privilege escalation
    )

    assert reg_data is not None
    # Crucial security check: assigned role MUST be 'client', not 'admin'
    assert reg_data["role"] == "client"
    assert reg_data["email"] == test_email

    # Verify registered user can authenticate
    login_data = SupabaseAuthService.authenticate(
        email=test_email,
        password="ValidPassword123!",
    )
    assert login_data["role"] == "client"
    assert login_data["email"] == test_email


def test_supabase_auth_via_login_endpoint(client):
    """Test logging in through the /api/v1/auth/login endpoint."""
    res = client.post(
        "/api/v1/auth/login",
        json={
            "email": "zacma@admin",
            "password": "zacma@11",
            "remember_me": True,
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["role"] == "admin"
    assert data["email"] == "zacma@admin"
    assert "access_token" in data
    assert settings.session_cookie_name in res.cookies


def test_supabase_client_user_cannot_access_admin_apis(client):
    """Test that a user registered in Supabase with client role is strictly rejected from admin APIs."""
    # 1. Register client
    reg_res = client.post(
        "/api/v1/auth/register",
        json={
            "email": "customer_rbac_test@example.com",
            "password": "SecurePassword123!",
            "full_name": "Customer RBAC",
            "role": "client",
        },
    )
    assert reg_res.status_code in [201, 409]

    # 2. Login to obtain client token
    login_res = client.post(
        "/api/v1/auth/login",
        json={
            "email": "customer_rbac_test@example.com",
            "password": "SecurePassword123!",
        },
    )
    assert login_res.status_code == 200
    client_token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {client_token}"}

    # 3. Verify access to client profile works
    me_res = client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["role"] == "client"

    # 4. Verify access to admin endpoints is forbidden (403)
    admin_users_res = client.get("/api/v1/admin/users", headers=headers)
    assert admin_users_res.status_code == 403

    admin_stats_res = client.get("/api/v1/admin/stats", headers=headers)
    assert admin_stats_res.status_code == 403

    admin_reviews_res = client.get("/api/v1/admin/reviews/queue", headers=headers)
    assert admin_reviews_res.status_code == 403


def test_supabase_admin_user_can_access_admin_apis(client):
    """Test that authenticated administrator accesses protected admin endpoints."""
    login_res = client.post(
        "/api/v1/auth/login",
        json={
            "email": "zacma@admin",
            "password": "zacma@11",
        },
    )
    assert login_res.status_code == 200
    admin_token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {admin_token}"}

    res_users = client.get("/api/v1/admin/users", headers=headers)
    assert res_users.status_code == 200

    res_stats = client.get("/api/v1/admin/stats", headers=headers)
    assert res_stats.status_code == 200

    res_overview = client.get("/api/v1/dashboard/overview", headers=headers)
    assert res_overview.status_code == 200


def test_supabase_token_revocation_on_logout(client):
    """Test that logout revokes access immediately."""
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "zacma@admin", "password": "zacma@11"},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Verify active
    assert client.get("/api/v1/admin/users", headers=headers).status_code == 200

    # Logout
    logout_res = client.post("/api/v1/auth/logout", headers=headers)
    assert logout_res.status_code == 200

    # Verify rejected
    assert client.get("/api/v1/admin/users", headers=headers).status_code == 401


def test_supabase_token_verifier():
    """Test SupabaseAuthService.verify_supabase_token with mock Supabase JWT claims."""
    mock_supabase_token = create_access_token(
        {
            "sub": "sb-user-12345",
            "email": "sb_user@zacma.com",
            "role": "client",
            "tenant_id": settings.demo_tenant_id,
            "user_metadata": {
                "full_name": "Supabase User",
                "role": "client",
            }
        }
    )

    claims = SupabaseAuthService.verify_supabase_token(mock_supabase_token)
    assert claims is not None
    assert claims["sub"] == "sb-user-12345"
    assert claims["email"] == "sb_user@zacma.com"
    assert claims["role"] == "client"
