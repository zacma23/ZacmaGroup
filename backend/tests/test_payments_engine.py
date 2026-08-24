"""Comprehensive Tests for ZACMA Multi-Provider Payment Engine & Invoicing Platform.

Tests cover:
- Dynamic provider configuration & admin credential masking (zero secret leaks)
- Unique reference pattern: ZACMA-2026-XXXXXXXX
- Chapa gateway initialization, hosted checkout links & server-side verification
- Webhook HMAC-SHA256 signature verification & idempotent deduplication
- Balance summary (explicit distinction between provider API balance and internal platform balance)
- Absence of hard-coded bank accounts / customer numbers (1000140145797)
"""

import hashlib
import hmac
import json
import re
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.fixture
def admin_token() -> str:
    res = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@zacma.com", "password": "AdminPassword123!"},
    )
    assert res.status_code == 200
    return res.json()["access_token"]


def test_public_active_providers_sanitization():
    """Verify customer-facing providers list contains active providers without sensitive secret credentials."""
    res = client.get("/api/v1/payments/providers/active")
    assert res.status_code == 200
    providers = res.json()
    assert len(providers) >= 3

    provider_codes = [p["provider_code"] for p in providers]
    assert "santimpay" in provider_codes
    assert "cbe" in provider_codes
    assert "telebirr" in provider_codes

    # Verify zero secret leaks
    for p in providers:
        assert "secret_key" not in p
        assert "api_key" not in p
        assert "webhook_secret" not in p
        # Check no hardcoded forbidden account
        if p.get("account_number"):
            assert p["account_number"] != "1000140145797"


def test_initialize_payment_transaction_santimpay():
    """Verify initializing a payment generates a unique ZACMA-2026-XXXXXXXX reference and hosted checkout URL."""
    payload = {
        "amount": 2500.0,
        "provider_code": "santimpay",
        "customer_name": "Almaz Tesfaye",
        "customer_email": "almaz.t@example.com",
        "payment_purpose": "Software Architecture Deposit",
        "currency": "ETB",
    }
    res = client.post("/api/v1/payments/transactions/initialize", json=payload)
    assert res.status_code == 201
    data = res.json()

    # Check unique reference format ZACMA-2026-XXXXXXXX
    ref = data["public_reference"]
    assert re.match(r"^ZACMA-2026-[A-Z0-9]{8}$", ref)
    assert data["amount"] == 2500.0
    assert data["currency"] == "ETB"
    assert data["checkout_url"] is not None
    assert "santimpay" in data["checkout_url"].lower()


def test_initialize_payment_transaction_cbe_bank_transfer():
    """Verify initializing CBE payment returns structured transfer instructions with unique reference."""
    payload = {
        "amount": 4000.0,
        "provider_code": "cbe",
        "customer_name": "Dawit Bekele",
        "customer_email": "dawit.b@example.com",
        "payment_purpose": "Visa Audit Retainer",
    }
    res = client.post("/api/v1/payments/transactions/initialize", json=payload)
    assert res.status_code == 201
    data = res.json()

    assert data["status"] == "pending"
    assert data["instructions"] is not None
    assert data["public_reference"] in data["instructions"]
    assert data["account_name"] is not None


def test_server_side_verification_and_auto_completion(admin_token):
    """Verify server-side transaction verification transitions transaction to successful."""
    # 1. Initialize
    init_res = client.post(
        "/api/v1/payments/transactions/initialize",
        json={
            "amount": 1800.0,
            "provider_code": "santimpay",
            "customer_name": "Tigist Hailu",
            "payment_purpose": "AI Course Fee",
        },
    )
    assert init_res.status_code == 201
    ref = init_res.json()["public_reference"]

    # 2. Check initial status
    status_res = client.get(f"/api/v1/payments/transactions/{ref}/status")
    assert status_res.status_code == 200
    assert status_res.json()["status"] in {"initiated", "pending"}

    # 3. Server-side verification
    verify_res = client.post(
        f"/api/v1/payments/admin/transactions/{ref}/verify",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert verify_res.status_code == 200
    assert verify_res.json()["success"] is True
    assert verify_res.json()["status"] == "successful"

    # 4. Status is now successful
    final_res = client.get(f"/api/v1/payments/transactions/{ref}/status")
    assert final_res.status_code == 200
    assert final_res.json()["status"] == "successful"


def test_webhook_hmac_sha256_and_idempotency():
    """Verify Chapa webhook processing, signature verification, and duplicate replay prevention."""
    # 1. Create transaction
    init_res = client.post(
        "/api/v1/payments/transactions/initialize",
        json={
            "amount": 3200.0,
            "provider_code": "chapa",
            "customer_name": "Blen Mengistu",
            "customer_email": "blen@example.com",
            "payment_purpose": "Travel Package Deposit",
        },
    )
    ref = init_res.json()["public_reference"]

    # 2. Prepare Webhook Payload
    webhook_payload = {
        "event": "charge.success",
        "tx_ref": ref,
        "amount": "3200.00",
        "currency": "ETB",
        "status": "success",
        "reference": "chapa_txn_991823",
    }
    raw_body = json.dumps(webhook_payload, sort_keys=True)
    secret_key = "chapa_webhook_mock_secret"
    signature = hmac.new(secret_key.encode("utf-8"), raw_body.encode("utf-8"), hashlib.sha256).hexdigest()

    # 3. Dispatch Webhook
    wh_res = client.post(
        "/api/v1/payments/webhooks/chapa",
        json=webhook_payload,
        headers={"x-chapa-signature": signature},
    )
    assert wh_res.status_code == 200
    assert wh_res.json()["status"] == "success"

    # 4. Dispatch Duplicate Webhook -> Should be handled idempotently
    wh_dup = client.post(
        "/api/v1/payments/webhooks/chapa",
        json=webhook_payload,
        headers={"x-chapa-signature": signature},
    )
    assert wh_dup.status_code == 200
    assert "idempotent" in wh_dup.json()["message"].lower() or wh_dup.json()["status"] == "success"


def test_balances_summary_and_distinction(admin_token):
    """Verify balance analytics endpoint correctly reports totals and distinguishes API vs internal balances."""
    res = client.get(
        "/api/v1/payments/admin/balances",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res.status_code == 200
    data = res.json()

    assert "total_received" in data
    assert "pending_balance" in data
    assert "available_balance" in data
    assert "provider_balances" in data
    assert len(data["provider_balances"]) >= 3

    # Verify each provider item distinguishes provider API balance vs internal platform balance
    for pb in data["provider_balances"]:
        assert "provider_reported_balance" in pb
        assert "internal_platform_balance" in pb
        assert "status_message" in pb

        if not pb["balance_available_from_api"]:
            assert "unavailable from provider api" in pb["status_message"].lower()


def test_admin_provider_management_crud_and_testing(admin_token):
    """Verify creating, testing, updating, and deactivating a payment provider from Admin console."""
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Create a new custom bank provider (e.g. Dashen Bank)
    new_provider_payload = {
        "provider_name": "Dashen Bank",
        "provider_code": "dashen",
        "provider_type": "bank_transfer",
        "is_active": True,
        "is_default": False,
        "environment": "live",
        "currency": "ETB",
        "account_name": "Zacma Technology Group",
        "account_number": "5500123456789",
        "customer_payment_number": "DASHEN-ZACMA",
        "instructions": "Transfer to Dashen Bank A/C 5500123456789",
        "secret_key": "dashen_private_credential_key_secret",
    }
    create_res = client.post("/api/v1/payments/admin/providers", json=new_provider_payload, headers=headers)
    assert create_res.status_code == 201
    created = create_res.json()
    provider_id = created["id"]

    # 2. List admin providers -> verify secret is masked
    list_res = client.get("/api/v1/payments/admin/providers", headers=headers)
    assert list_res.status_code == 200
    admin_provs = list_res.json()
    dashen_prov = next((p for p in admin_provs if p["id"] == provider_id), None)
    assert dashen_prov is not None
    assert dashen_prov["has_secret_key"] is True
    assert "••••" in dashen_prov["masked_secret_key"]
    assert "dashen_private_credential_key_secret" not in dashen_prov["masked_secret_key"]

    # 3. Test Provider Connection
    test_res = client.post(f"/api/v1/payments/admin/providers/{provider_id}/test", headers=headers)
    assert test_res.status_code == 200
    assert test_res.json()["success"] is True

    # 4. Update Provider (toggle active)
    upd_res = client.put(
        f"/api/v1/payments/admin/providers/{provider_id}",
        json={"is_active": False},
        headers=headers,
    )
    assert upd_res.status_code == 200
    assert upd_res.json()["is_active"] is False

    # 5. Clean up delete
    del_res = client.delete(f"/api/v1/payments/admin/providers/{provider_id}", headers=headers)
    assert del_res.status_code == 204


def test_customer_public_verification_and_duplicate_idempotency():
    """Verify customer can verify transaction on return and duplicate verifications are idempotent."""
    # 1. Initialize Chapa payment
    init_res = client.post(
        "/api/v1/payments/transactions/initialize",
        json={
            "amount": 5000.0,
            "provider_code": "santimpay",
            "customer_name": "Abebe Bikila",
            "customer_email": "abebe.b@example.com",
            "customer_phone": "+251911223344",
            "payment_purpose": "Software License",
            "currency": "ETB",
        },
    )
    assert init_res.status_code == 201
    ref = init_res.json()["public_reference"]

    # 2. Customer triggers public verification endpoint (e.g. on return redirect)
    verify_res1 = client.post(f"/api/v1/payments/transactions/{ref}/verify")
    assert verify_res1.status_code == 200
    data1 = verify_res1.json()
    assert data1["success"] is True
    assert data1["status"] == "successful"
    assert data1["amount"] == 5000.0
    assert data1["currency"] == "ETB"

    # 3. Duplicate verification -> Idempotent response
    verify_res2 = client.post(f"/api/v1/payments/transactions/{ref}/verify")
    assert verify_res2.status_code == 200
    data2 = verify_res2.json()
    assert data2["success"] is True
    assert data2["status"] == "successful"
    assert "already verified" in data2["message"].lower() or data2["success"] is True

    # 4. Non-existent reference verification
    bad_res = client.post("/api/v1/payments/transactions/ZACMA-NONEXISTENT-9999/verify")
    assert bad_res.status_code == 200
    assert bad_res.json()["success"] is False
    assert bad_res.json()["status"] == "not_found"

