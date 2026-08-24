import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_crm_leads_crud():
    # 1. List leads
    res = client.get("/api/v1/crm/leads")
    assert res.status_code == 200
    leads = res.json()
    assert isinstance(leads, list)
    initial_count = len(leads)

    # 2. Create lead
    new_lead = {
        "name": "Integration Test Lead",
        "email": "lead@test.com",
        "company": "Test Co",
        "phone": "+1234567890",
        "source": "website",
        "status": "new",
        "notes": "Automated test lead"
    }
    create_res = client.post("/api/v1/crm/leads", json=new_lead)
    assert create_res.status_code == 201
    created_lead = create_res.json()
    lead_id = created_lead["id"]
    assert created_lead["name"] == new_lead["name"]
    assert created_lead["tenant_id"] == "zacma-demo"

    # 3. Get lead by ID
    get_res = client.get(f"/api/v1/crm/leads/{lead_id}")
    assert get_res.status_code == 200
    assert get_res.json()["email"] == "lead@test.com"

    # 4. Update lead
    update_res = client.put(f"/api/v1/crm/leads/{lead_id}", json={"status": "contacted", "name": "Updated Lead"})
    assert update_res.status_code == 200
    assert update_res.json()["status"] == "contacted"
    assert update_res.json()["name"] == "Updated Lead"

    # 5. Delete lead
    del_res = client.delete(f"/api/v1/crm/leads/{lead_id}")
    assert del_res.status_code == 204

    # 6. Verify deleted
    get_del = client.get(f"/api/v1/crm/leads/{lead_id}")
    assert get_del.status_code == 404
