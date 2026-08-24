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

def test_crm_contacts_and_timeline(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. List contacts
    res = client.get("/api/v1/crm/contacts")
    assert res.status_code == 200
    contacts = res.json()
    assert isinstance(contacts, list)

    # 2. Create contact
    new_contact = {
        "full_name": "Test CRM Contact",
        "email": "crmcontact@test.com",
        "phone": "+251911445566",
        "address": "Addis Ababa",
        "source_module": "Student",
        "status": "Lead",
        "tags": ["Prospect", "Python"],
        "notes": "Met at career fair"
    }
    c_res = client.post("/api/v1/crm/contacts", json=new_contact)
    assert c_res.status_code == 201
    c_id = c_res.json()["id"]

    # 3. Add Admin Note
    note_res = client.post(
        f"/api/v1/crm/contacts/{c_id}/notes",
        json={"content": "Followed up via phone call"},
        headers=headers
    )
    assert note_res.status_code == 200
    assert note_res.json()["content"] == "Followed up via phone call"

    # 4. Check Timeline & Notes
    get_res = client.get(f"/api/v1/crm/contacts/{c_id}")
    assert get_res.status_code == 200
    assert len(get_res.json()["timeline"]) >= 1
    assert len(get_res.json()["notes_list"]) >= 1

def test_payment_engine_lifecycle(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Check Gateways
    gw_res = client.get("/api/v1/payments/gateways")
    assert gw_res.status_code == 200
    assert len(gw_res.json()["active_providers"]) >= 1
    assert any("Commercial Bank of Ethiopia" in opt for opt in gw_res.json()["bank_transfer_options"])

    # 2. Create Invoice
    inv_payload = {
        "customer_name": "Test Invoice Client",
        "customer_email": "client.pay@test.com",
        "amount": 3500.0,
        "currency": "ETB",
        "description": "Training Materials Fee",
        "payment_method": "CBE"
    }
    create_res = client.post("/api/v1/payments/invoices", json=inv_payload)
    assert create_res.status_code == 201
    inv = create_res.json()
    inv_id = inv["id"]
    assert inv["receiving_account"] is not None
    assert inv["status"] == "sent"

    # 3. Record Payment Attempt
    att_res = client.post(
        f"/api/v1/payments/invoices/{inv_id}/attempt",
        json={"gateway": "CBE", "reference_number": "FT262359988", "notes": "Paid via CBE Birr"}
    )
    assert att_res.status_code == 200
    assert att_res.json()["status"] == "paid"

    # 4. Admin Confirms Payment
    conf_res = client.post(
        f"/api/v1/payments/invoices/{inv_id}/confirm",
        json={"comment": "Transaction verified in bank statement"},
        headers=headers
    )
    assert conf_res.status_code == 200
    assert conf_res.json()["status"] == "confirmed"

    # 5. Resend Invoice
    resend_res = client.post(f"/api/v1/payments/invoices/{inv_id}/resend", headers=headers)
    assert resend_res.status_code == 200
    assert resend_res.json()["status"] == "success"

def test_admin_global_search_and_settings(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Global Search
    search_res = client.get("/api/v1/admin/search?q=Abebe", headers=headers)
    assert search_res.status_code == 200
    data = search_res.json()
    assert data["count"] >= 1
    assert any("Abebe" in r["title"] for r in data["results"])

    # 2. Get Settings
    settings_res = client.get("/api/v1/admin/settings", headers=headers)
    assert settings_res.status_code == 200

    # 3. Update Settings
    upd_res = client.put(
        "/api/v1/admin/settings",
        json={"default_payment_methods": ["Chapa", "CBE", "TeleBirr", "Awash", "Abyssinia"]},
        headers=headers
    )
    assert upd_res.status_code == 200
