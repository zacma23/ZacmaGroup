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

def test_dynamic_module_lifecycle(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. SuperAdmin creates a new business module (e.g. Health Insurance)
    new_module_payload = {
        "name": "Health Insurance Agency",
        "key": "health_insurance",
        "description": "Medical and health policy underwriting intake",
        "requires_payment": True,
        "base_amount": 2500.0,
        "fields": [
            {
                "id": "f-01",
                "field_name": "coverage_type",
                "label": "Coverage Plan",
                "field_type": "dropdown",
                "is_required": True,
                "options": ["Individual", "Family", "Corporate Group"],
                "order": 1
            },
            {
                "id": "f-02",
                "field_name": "pre_existing_conditions",
                "label": "Pre-existing Conditions",
                "field_type": "textarea",
                "is_required": False,
                "order": 2
            }
        ]
    }
    create_mod_res = client.post("/api/v1/admin/modules", json=new_module_payload, headers=headers)
    assert create_mod_res.status_code == 201
    mod = create_mod_res.json()
    assert mod["key"] == "health_insurance"
    assert len(mod["fields"]) == 2

    # 2. Client submits dynamic intake form to /submissions/health_insurance
    submission_payload = {
        "full_name": "Almaz Ayana",
        "email": "almaz.a@test.com",
        "phone": "+251911002233",
        "payment_method": "TeleBirr",
        "data_json": {
            "coverage_type": "Family",
            "pre_existing_conditions": "None"
        }
    }
    sub_res = client.post("/api/v1/submissions/health_insurance", json=submission_payload)
    assert sub_res.status_code == 201
    sub = sub_res.json()
    sub_id = sub["id"]

    # Verify Auto CRM Contact Sync
    assert sub["linked_crm_contact_id"] is not None

    # Verify Auto Invoice Generation (requires_payment=True)
    assert sub["linked_invoice_id"] is not None

    # 3. Check Invoice
    inv_id = sub["linked_invoice_id"]
    inv_res = client.get(f"/api/v1/payments/invoices/{inv_id}")
    assert inv_res.status_code == 200
    inv = inv_res.json()
    assert inv["amount"] == 2500.0
    assert inv["receiving_account"] is not None

    # 4. Admin Approves Dynamic Submission
    app_res = client.post(
        f"/api/v1/submissions/health_insurance/{sub_id}/approve",
        json={"comment": "Policy terms accepted"},
        headers=headers
    )
    assert app_res.status_code == 200
    assert app_res.json()["status"] == "success"

    # Verify status changed to Approved
    get_sub = client.get(f"/api/v1/submissions/health_insurance/{sub_id}")
    assert get_sub.json()["status"] == "Approved"
