import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.auth import create_access_token
from app.core.config import settings

client = TestClient(app)

@pytest.fixture
def admin_token():
    return create_access_token({
        "sub": "admin-id",
        "email": "admin@zacma.com",
        "role": "admin",
        "tenant_id": settings.demo_tenant_id,
        "full_name": "Zacma Admin"
    })

@pytest.fixture
def client_token():
    return create_access_token({
        "sub": "client-id",
        "email": "client@zacma.com",
        "role": "client",
        "tenant_id": settings.demo_tenant_id,
        "full_name": "Demo Client"
    })

def test_admin_unauthorized():
    # No auth header -> 401
    res = client.get("/api/v1/admin/users")
    assert res.status_code == 401

def test_admin_forbidden_for_client(client_token):
    # Client role -> 403 Forbidden
    res = client.get("/api/v1/admin/users", headers={"Authorization": f"Bearer {client_token}"})
    assert res.status_code == 403

def test_admin_users_crud(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}

    # List users
    res = client.get("/api/v1/admin/users", headers=headers)
    assert res.status_code == 200
    assert isinstance(res.json(), list)

    # Create user
    new_user = {
        "email": "admincreated@zacma.com",
        "full_name": "Admin Created User",
        "role": "staff",
        "password": "Password123!"
    }
    create_res = client.post("/api/v1/admin/users", json=new_user, headers=headers)
    assert create_res.status_code == 201
    u_id = create_res.json()["id"]

    # Update user
    upd_res = client.put(f"/api/v1/admin/users/{u_id}", json={"role": "admin"}, headers=headers)
    assert upd_res.status_code == 200
    assert upd_res.json()["role"] == "admin"

    # Delete (deactivate) user
    del_res = client.delete(f"/api/v1/admin/users/{u_id}", headers=headers)
    assert del_res.status_code == 200
    assert "deactivated" in del_res.json()["detail"].lower()

def test_admin_tenants_and_audit(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Tenants
    t_res = client.get("/api/v1/admin/tenants", headers=headers)
    assert t_res.status_code == 200
    assert isinstance(t_res.json(), list)

    # Audit logs
    a_res = client.get("/api/v1/admin/audit_logs", headers=headers)
    assert a_res.status_code == 200
    assert isinstance(a_res.json(), list)

    # Stats
    s_res = client.get("/api/v1/admin/stats", headers=headers)
    assert s_res.status_code == 200
    data = s_res.json()
    assert "totals" in data
    assert "students" in data["totals"]
    assert "invoices" in data["totals"]
