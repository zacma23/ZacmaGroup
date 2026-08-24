import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_auth_login_and_me():
    # 1. Login with demo admin
    res = client.post("/api/v1/auth/login", json={
        "email": "admin@zacma.com",
        "password": "anypassword"
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["role"] == "admin"
    token = data["access_token"]

    # 2. Access /auth/me with Bearer token
    me_res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["email"] == "admin@zacma.com"
    assert me_data["role"] == "admin"

def test_auth_register():
    res = client.post("/api/v1/auth/register", json={
        "email": "newuser@test.com",
        "password": "securepassword123",
        "full_name": "New Test User",
        "role": "client"
    })
    assert res.status_code == 201
    data = res.json()
    assert "access_token" in data
    assert data["role"] == "client"

def test_auth_unauthorized():
    # Attempting to access /auth/me without token/cookie should return 401
    fresh_client = TestClient(app)
    me_res = fresh_client.get("/api/v1/auth/me")
    assert me_res.status_code == 401

def test_session_endpoint():
    res = client.get("/api/v1/auth/session")
    assert res.status_code == 200
    assert "authenticated" in res.json()

