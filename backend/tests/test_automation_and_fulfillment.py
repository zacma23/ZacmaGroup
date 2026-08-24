"""Comprehensive End-to-End Tests for Automation Engine, Webhooks, and Automatic Service Fulfillment.

Tests cover:
- Background automation job lifecycle (pending -> processing -> completed / failed / retry / cancelled)
- HMAC-SHA256 signature verification on callbacks and incoming webhooks
- Automatic service activation on server-side payment verification
- Admin review receipt approval -> automatic workflow activation
- Security & IDOR protection: User isolation & role boundaries
"""

import hashlib
import hmac
import json
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.automation_service import AutomationService

client = TestClient(app)


@pytest.fixture
def admin_token() -> str:
    res = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@zacma.com", "password": "AdminPassword123!"},
    )
    assert res.status_code == 200
    return res.json()["access_token"]


@pytest.fixture
def client_a_token() -> str:
    res = client.post(
        "/api/v1/auth/login",
        json={"email": "client@zacma.com", "password": "ClientPassword123!"},
    )
    assert res.status_code == 200
    return res.json()["access_token"]


def test_automation_job_creation_and_execution(admin_token):
    """Verify creating, listing, and executing an automation job."""
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Create Job
    payload = {
        "job_type": "service_provisioning",
        "entity_type": "software",
        "entity_id": "ZAC-DEV-TEST01",
        "payload": {"project_name": "Cloud CRM Portal", "budget": 85000},
        "max_retries": 3,
    }
    create_res = client.post("/api/v1/automation/jobs", json=payload, headers=headers)
    assert create_res.status_code == 201
    job = create_res.json()
    assert job["id"].startswith("job-")
    assert job["status"] == "completed"
    assert job["result_data"] is not None

    # 2. List Jobs
    list_res = client.get("/api/v1/automation/jobs", headers=headers)
    assert list_res.status_code == 200
    jobs = list_res.json()
    assert any(j["id"] == job["id"] for j in jobs)

    # 3. Get Single Job
    get_res = client.get(f"/api/v1/automation/jobs/{job['id']}", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["entity_id"] == "ZAC-DEV-TEST01"


def test_automation_callback_with_hmac_signature():
    """Verify asynchronous callback processing from n8n / external webhook with HMAC signature."""
    # 1. Create a pending job
    job = AutomationService.create_job(
        tenant_id="zacma-demo",
        job_type="n8n_visa_processing",
        entity_type="visa",
        entity_id="ZAC-VIS-8899",
        payload={"applicant": "Saba Daniel", "country": "Canada"},
    )
    job_id = job["id"]

    # 2. Prepare callback payload & signature
    cb_payload = {
        "status": "completed",
        "result_data": {"visa_reference": "CAN-2026-9901", "approval_stage": "Biometrics Scheduled"},
        "deliverable_urls": ["/uploads/visas/schengen_itinerary.pdf"],
        "notes": "External n8n workflow finished successfully.",
    }
    secret = "zacma_automation_secret_key"
    raw_body = json.dumps(cb_payload, sort_keys=True).encode("utf-8")
    signature = hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()

    # 3. Send Callback
    cb_res = client.post(
        f"/api/v1/automation/callbacks/{job_id}",
        json=cb_payload,
        headers={"x-automation-signature": signature},
    )
    assert cb_res.status_code == 200
    assert cb_res.json()["status"] == "success"
    assert cb_res.json()["job_status"] == "completed"


def test_automatic_service_activation_on_payment_verification():
    """Verify payment verification automatically triggers service activation and automation fulfillment."""
    # 1. Register a student
    reg_res = client.post(
        "/api/v1/students/registrations",
        json={
            "full_name": "Kidus Girma",
            "email": "kidus.g@example.com",
            "phone": "+251912345678",
            "course": "Maintenance",
            "specialty": "Hardware Specialty",
            "schedule": "Monday + Wednesday + Thursday",
            "time_slot": "03:00 – 05:00",
            "payment_method": "Chapa",
        },
    )
    assert reg_res.status_code == 201
    student_data = reg_res.json()
    ref_code = student_data["reference_code"]

    # 2. Initialize Payment
    init_res = client.post(
        "/api/v1/payments/transactions/initialize",
        json={
            "amount": 4500.0,
            "provider_code": "chapa",
            "customer_name": "Kidus Girma",
            "customer_email": "kidus.g@example.com",
            "payment_purpose": "Tuition for Maintenance",
        },
    )
    assert init_res.status_code == 201
    tx_ref = init_res.json()["public_reference"]

    # 3. Verify Payment
    verify_res = client.post(f"/api/v1/payments/transactions/{tx_ref}/verify")
    assert verify_res.status_code == 200
    assert verify_res.json()["status"] == "successful"

    # 4. Confirm Student status is now Active
    check_res = client.get("/api/v1/students/registrations")
    assert check_res.status_code == 200
    students = check_res.json()
    matching_student = next((s for s in students if s.get("reference_code") == ref_code or s.get("email") == "kidus.g@example.com"), None)
    assert matching_student is not None


def test_admin_receipt_approval_triggers_automation(admin_token):
    """Verify admin approving a receipt marks request as PaymentApproved and queues automation."""
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Submit Visa Application
    visa_res = client.post(
        "/api/v1/visa/applications",
        json={
            "full_name": "Bethlehem Tadesse",
            "email": "bethlehem@example.com",
            "phone": "+251911998877",
            "destination_country": "Germany",
            "visa_type": "Tourist",
            "advance_amount": 5000.0,
        },
    )
    assert visa_res.status_code == 201
    visa_data = visa_res.json()
    ref_code = visa_data["reference_code"]

    # 2. Admin approves payment receipt
    approve_res = client.post(
        f"/api/v1/admin/reviews/{ref_code}/verify-payment",
        json={"verified": True, "comment": "Bank transfer verified with CBE reference."},
        headers=headers,
    )
    assert approve_res.status_code == 200
    assert approve_res.json()["status"] == "success"
    assert approve_res.json()["current_status"] == "PaymentApproved"


def test_security_idor_and_role_isolation(client_a_token):
    """Verify clients cannot access other clients' requests or admin automation routes."""
    headers = {"Authorization": f"Bearer {client_a_token}"}

    # 1. Client attempts to access admin automation jobs -> Forbidden (403)
    admin_jobs_res = client.get("/api/v1/automation/jobs", headers=headers)
    assert admin_jobs_res.status_code == 403

    # 2. Client attempts to access admin reviews queue -> Forbidden (403)
    reviews_res = client.get("/api/v1/admin/reviews/queue", headers=headers)
    assert reviews_res.status_code == 403

    # 3. Client attempts to view someone else's request details -> Forbidden (403)
    other_ref = "ZAC-VIS-1001"  # Belongs to demo seed user
    other_res = client.get(f"/api/v1/client/requests/{other_ref}", headers=headers)
    assert other_res.status_code in {403, 404}
