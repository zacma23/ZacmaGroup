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

def test_visa_application_flow(admin_token):
    # 1. Submit Visa Application
    visa_payload = {
        "full_name": "Mulugeta Bekele",
        "address": "Addis Ababa",
        "phone": "+251911334455",
        "email": "mulugeta.b@test.com",
        "country": "Ethiopia",
        "destination_country": "Germany",
        "visa_type": "Tourist",
        "passport_upload_url": "/uploads/passports/mulugeta.pdf",
        "supporting_document_urls": ["/uploads/docs/bank_stmt.pdf"],
        "advance_payment_method": "CBE",
        "advance_amount": 5000.0
    }
    create_res = client.post("/api/v1/visa/applications", json=visa_payload)
    assert create_res.status_code == 201
    visa_app = create_res.json()
    app_id = visa_app["id"]

    # Verify AI document check
    assert "summary" in visa_app["ai_document_check_summary"].lower() or "missing" in visa_app["ai_document_check_summary"].lower() or "present" in visa_app["ai_document_check_summary"].lower()

    # 2. Request More Info
    req_info_res = client.post(
        f"/api/v1/visa/applications/{app_id}/request-info",
        json={"message": "Please upload hotel booking confirmation", "requested_documents": ["hotel_booking"]},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert req_info_res.status_code == 200

    # Verify status changed to DocumentsRequested
    assert client.get(f"/api/v1/visa/applications/{app_id}").json()["status"] == "DocumentsRequested"

    # 3. Approve Visa Application
    app_res = client.post(
        f"/api/v1/visa/applications/{app_id}/approve",
        json={"comment": "Documents complete, submitting to embassy"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert app_res.status_code == 200
    assert client.get(f"/api/v1/visa/applications/{app_id}").json()["status"] == "Approved"

def test_travel_request_flow(admin_token):
    # 1. Submit Travel Request
    trv_payload = {
        "full_name": "Helina Tadesse",
        "address": "Bole, Addis Ababa",
        "phone": "+251922556677",
        "email": "helina.t@test.com",
        "destination_country": "Turkey (Istanbul)",
        "budget": 45000.0,
        "advance_payment_method": "Awash",
        "travel_date_preference": "November 2026"
    }
    create_res = client.post("/api/v1/travel/requests", json=trv_payload)
    assert create_res.status_code == 201
    trv = create_res.json()
    trv_id = trv["id"]

    # Verify AI Itinerary Generated
    assert trv["ai_itinerary_suggestion"] is not None

    # 2. Admin Approve
    app_res = client.post(
        f"/api/v1/travel/requests/{trv_id}/approve",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert app_res.status_code == 200
    assert client.get(f"/api/v1/travel/requests/{trv_id}").json()["status"] == "Approved"

def test_support_ticket_flow(admin_token):
    # 1. Create Support Ticket
    tkt_payload = {
        "full_name": "Solomon Girma",
        "email": "solomon.g@test.com",
        "phone": "+251933889900",
        "subject": "Question about CBE payment processing time",
        "message": "I transferred the invoice amount via CBE mobile app. How long until confirmation?",
        "category": "general"
    }
    create_res = client.post("/api/v1/support/tickets", json=tkt_payload)
    assert create_res.status_code == 201
    tkt = create_res.json()
    tkt_id = tkt["id"]

    # Verify AI suggested reply & auto-categorization
    assert tkt["ai_suggested_reply"] is not None
    assert tkt["category"] in ["Billing", "General"]

    # 2. Reply to Ticket
    reply_res = client.post(
        f"/api/v1/support/tickets/{tkt_id}/reply",
        json={"message": "CBE transfers are confirmed within 1 business hour.", "status_update": "Resolved"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert reply_res.status_code == 200
    assert reply_res.json()["status"] == "Resolved"
    assert len(reply_res.json()["thread"]) == 2

    # 3. Convert to CRM Lead
    conv_res = client.post(
        f"/api/v1/support/tickets/{tkt_id}/convert-lead",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert conv_res.status_code == 200
    assert conv_res.json()["status"] == "success"

def test_client_packages_and_tracking_flow():
    # 1. Test packages endpoint
    pkg_res = client.get("/api/v1/support/packages")
    assert pkg_res.status_code == 200
    packages = pkg_res.json()
    assert "visa" in packages and "travel" in packages and "training" in packages and "marketing" in packages
    assert len(packages["visa"]) >= 3

    # 2. Test request tracking
    track_res = client.get("/api/v1/support/track/visa-001")
    assert track_res.status_code == 200
    data = track_res.json()
    assert data["service_type"] == "Visa Assistant"
    assert data["customer_name"] == "Tigist Assefa"
    assert len(data["timeline"]) >= 1

    # 3. Test client thread messaging
    msg_res = client.post(
        "/api/v1/support/track/visa-001/message",
        json={"message": "What is the next step for my German visa?", "sender_name": "Tigist Assefa"}
    )
    assert msg_res.status_code == 200
    msg_data = msg_res.json()
    assert msg_data["status"] == "success"
    assert msg_data["ai_response"]["sender_type"] == "ai"

    # 4. Test Telegram bot webhook
    tg_res = client.post(
        "/api/v1/support/telegram",
        json={"message": {"text": "/courses", "chat": {"id": 12345}, "from": {"first_name": "TestUser"}}}
    )
    assert tg_res.status_code == 200
    assert tg_res.json()["ok"] is True
    assert "Zacma Training" in tg_res.json()["reply_text"]

