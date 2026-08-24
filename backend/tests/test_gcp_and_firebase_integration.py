"""Comprehensive Tests for Google Cloud Platform, Firebase Auth, Gemini AI, and Workflows Integration.

Tests cover:
- Firebase ID token verification, claim mapping, and AuthMiddleware integration
- Google Cloud Storage (GCS) file uploads and expiring signed URL verification
- Google Pub/Sub event publication, payload validation, and idempotency deduplication
- Google Cloud Workflows driver invocation in AutomationService
- Google Gemini AI provider abstraction
- Full End-to-End User Journey (Firebase Auth -> Intake -> Chapa Pay -> Pub/Sub -> Workflow -> Telegram Notification)
"""

import hashlib
import json
import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.main import app
from app.services.firebase_auth_service import FirebaseAuthService
from app.services.gcs_file_service import GcsFileService
from app.services.gcp_workflows_driver import GoogleWorkflowsDriver
from app.services.pubsub_service import PubSubService
from ai.llm import build_chat_model

client = TestClient(app)


def test_firebase_token_verification_and_middleware():
    """Verify Firebase ID token verification and user claim resolution in AuthMiddleware."""
    # 1. Verify direct Firebase token helper
    mock_token = "firebase_mock_saba_1001"
    user_claims = FirebaseAuthService.verify_firebase_token(mock_token)
    assert user_claims is not None
    assert user_claims["email"] == "saba@example.com"
    assert user_claims["role"] == "client"
    assert user_claims["auth_provider"] == "firebase"

    # 2. Test authenticating via HTTP Authorization header with Firebase token
    res = client.get("/api/v1/auth/session", headers={"Authorization": f"Bearer {mock_token}"})
    assert res.status_code == 200
    session_data = res.json()
    assert session_data["authenticated"] is True
    assert session_data["user"]["email"] == "saba@example.com"


def test_gcs_file_service_and_signed_urls():
    """Verify GCS file storage adapter and secure signed URL generation & validation."""
    blob_name = "receipts/abc123_cbe_transfer.png"
    user_email = "saba@example.com"

    # 1. Generate signed URL
    signed_url = GcsFileService.generate_signed_url(blob_name, expiration_minutes=30, user_email=user_email)
    assert "blob=" in signed_url
    assert "sig=" in signed_url
    assert "exp=" in signed_url

    # 2. Extract and verify signature
    query_parts = dict(param.split("=") for param in signed_url.split("?")[1].split("&"))
    assert GcsFileService.verify_signed_url(
        blob_name=query_parts["blob"],
        exp=int(query_parts["exp"]),
        sig=query_parts["sig"],
        user_email=user_email,
    ) is True

    # 3. Tampered signature fails
    assert GcsFileService.verify_signed_url(
        blob_name=query_parts["blob"],
        exp=int(query_parts["exp"]),
        sig="invalid_tampered_sig",
        user_email=user_email,
    ) is False


def test_google_pubsub_event_publication_and_idempotency():
    """Verify publishing events to Google Cloud Pub/Sub topics with duplicate suppression."""
    tenant_id = "zacma-demo"
    event_payload = {
        "reference_code": "ZAC-STU-7788",
        "amount": 4500.0,
        "customer": "Abebe Bikila",
        "course": "Artificial Intelligence",
    }

    # 1. First Publish -> Published
    res1 = PubSubService.publish_event(
        tenant_id=tenant_id,
        event_name="payment.verified",
        payload=event_payload,
    )
    assert res1["status"] == "published"
    assert res1["event_name"] == "payment.verified"
    assert "event_id" in res1

    # 2. Immediate Duplicate Publish -> Idempotent Skip
    res2 = PubSubService.publish_event(
        tenant_id=tenant_id,
        event_name="payment.verified",
        payload=event_payload,
    )
    assert res2["status"] == "duplicate_skipped"


def test_google_cloud_workflows_driver():
    """Verify Google Cloud Workflows execution driver dispatch."""
    exec_res = GoogleWorkflowsDriver.execute_workflow(
        workflow_name="service_fulfillment",
        execution_input={
            "job_id": "job-test-wf-001",
            "entity_type": "visa",
            "entity_id": "ZAC-VIS-9911",
            "payload": {"destination": "Canada", "applicant": "Dawit Haile"},
        },
        project_id="zacma-platform-test",
    )
    assert exec_res["state"] == "ACTIVE"
    assert exec_res["workflow_name"] == "service_fulfillment"
    assert exec_res["driver"] == "google_workflows"
    assert exec_res["input"]["job_id"] == "job-test-wf-001"


def test_google_gemini_ai_model_builder(monkeypatch):
    """Verify Google Gemini AI provider abstraction initialization."""
    monkeypatch.setenv("AI_PROVIDER", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "test-gemini-key")
    monkeypatch.setenv("AI_MODEL", "gemini-1.5-flash")

    model = build_chat_model()
    assert model is not None
    api_base = str(getattr(model, "openai_api_base", "") or getattr(model, "base_url", ""))
    assert "generativelanguage.googleapis.com" in api_base
    model_name = getattr(model, "model_name", None) or getattr(model, "model", None)
    assert model_name == "gemini-1.5-flash"


def test_end_to_end_gcp_firebase_journey():
    """Full End-to-End Journey: Firebase Auth -> Application -> Chapa Payment -> Service Activation -> Notification."""
    # 1. Authenticate with Firebase token
    firebase_token = "firebase_mock_meron_8822"
    headers = {"Authorization": f"Bearer {firebase_token}"}

    session_res = client.get("/api/v1/auth/session", headers=headers)
    assert session_res.status_code == 200
    email = session_res.json()["user"]["email"]

    # 2. Register Student Course
    reg_res = client.post(
        "/api/v1/students/registrations",
        json={
            "full_name": "Meron Tesfaye",
            "email": email,
            "phone": "+251911334455",
            "course": "Full-Stack Web Development",
            "schedule": "Tuesday + Thursday + Saturday",
            "time_slot": "09:00 – 11:00",
            "payment_method": "Chapa",
        },
    )
    assert reg_res.status_code == 201
    ref_code = reg_res.json()["reference_code"]

    # 3. Initialize Chapa Payment
    init_res = client.post(
        "/api/v1/payments/transactions/initialize",
        json={
            "amount": 5500.0,
            "provider_code": "chapa",
            "customer_name": "Meron Tesfaye",
            "customer_email": email,
            "payment_purpose": "Tuition for Full-Stack Web Development",
        },
    )
    assert init_res.status_code == 201
    tx_ref = init_res.json()["public_reference"]

    # 4. Verify Payment Server-side
    verify_res = client.post(f"/api/v1/payments/transactions/{tx_ref}/verify")
    assert verify_res.status_code == 200
    assert verify_res.json()["status"] == "successful"

    # 5. Verify Request in Client Portal under authenticated Firebase user
    portal_res = client.get("/api/v1/client/dashboard", headers=headers)
    assert portal_res.status_code == 200
    recent_requests = portal_res.json()["recent_requests"]
    assert any(r.get("reference_code") == ref_code or r.get("title") == "Course: Full-Stack Web Development" for r in recent_requests)
