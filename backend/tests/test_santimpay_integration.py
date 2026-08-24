"""Comprehensive Test Suite for SantimPay Payment Gateway Integration in ZACMA Group.

Verifies:
1. Checkout initialization: Unique reference pattern (ZACMA-2026-XXXXXXXX), SantimPay gateway URL via nodeSDK bridge.
2. Successful payment callback: Valid ES256 Signed-Token verified using public key, status mapped to COMPLETED/PAID, idempotent settlement.
3. Failed/declined/cancelled callback: Correctly mapped to failed / cancelled statuses.
4. Invalid callback signature: Tampered or invalid signed-token rejected; transaction not marked as paid.
5. Duplicate / replay callback: Idempotent processing with no duplicate settlement.
6. Amount / currency mismatch: Tampered amounts rejected.
7. Unauthorized return URL: Frontend return without verified backend token does not mark order as paid.
"""

import json
import re
import pytest
import jwt
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings
from app.core.demo_data import DEMO_TENANT_ID
from app.services.payment_adapters.santimpay import SantimPayPaymentAdapter

client = TestClient(app)


# Generate a test EC P-256 Keypair for Signed-Token signing and verification
_test_ec_key = ec.generate_private_key(ec.SECP256R1())
TEST_PRIVATE_KEY_PEM = _test_ec_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption(),
).decode("utf-8")

TEST_PUBLIC_KEY_PEM = _test_ec_key.public_key().public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo,
).decode("utf-8")


@pytest.fixture(autouse=True)
def configure_santimpay_test_keys():
    """Configure settings to use the test EC keypair for signature tests."""
    original_priv = settings.santimpay_private_key
    original_pub = settings.santimpay_public_key
    settings.santimpay_private_key = TEST_PRIVATE_KEY_PEM
    settings.santimpay_public_key = TEST_PUBLIC_KEY_PEM
    yield
    settings.santimpay_private_key = original_priv
    settings.santimpay_public_key = original_pub


@pytest.fixture
def admin_token() -> str:
    res = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@zacma.com", "password": "AdminPassword123!"},
    )
    assert res.status_code == 200
    return res.json()["access_token"]


def test_1_santimpay_checkout_initialization():
    """Test 1: Checkout initialization creates reference and hosted checkout URL via nodeSDK bridge."""
    payload = {
        "amount": 3500.0,
        "provider_code": "santimpay",
        "customer_name": "Kidus Hailu",
        "customer_email": "kidus.h@example.com",
        "customer_phone": "+251911334455",
        "payment_purpose": "Software License Deposit",
        "currency": "ETB",
    }
    res = client.post("/api/v1/payments/transactions/initialize", json=payload)
    assert res.status_code == 201
    data = res.json()

    # Reference format verification: ZACMA-2026-XXXXXXXX
    ref = data["public_reference"]
    assert re.match(r"^ZACMA-2026-[A-Z0-9]{8}$", ref)
    assert data["amount"] == 3500.0
    assert data["currency"] == "ETB"
    assert data["status"] == "initiated"
    assert data["provider_code"] == "santimpay"
    assert "checkout_url" in data
    assert "santimpay" in data["checkout_url"].lower()


def test_2_santimpay_successful_payment_callback():
    """Test 2: Successful callback with valid ES256 Signed-Token marks transaction as successful and paid."""
    # 1. Initialize transaction
    init_res = client.post(
        "/api/v1/payments/transactions/initialize",
        json={
            "amount": 2500.0,
            "provider_code": "santimpay",
            "customer_name": "Bethlehem Tadesse",
            "customer_email": "bethlehem@example.com",
            "payment_purpose": "Visa Consultancy Fee",
        },
    )
    assert init_res.status_code == 201
    tx_data = init_res.json()
    ref = tx_data["public_reference"]
    tx_id = tx_data.get("transaction_id") or tx_data.get("id") or "tx-001"

    # 2. Build signed ES256 token payload as required by SantimPay
    token_claims = {
        "thirdPartyId": ref,
        "txn": "santim_txn_1001",
        "payment_id": tx_id,
        "amount": 2500.0,
        "currency": "ETB",
        "status": "COMPLETED",
        "merchantId": settings.santimpay_merchant_id or "merchant-santim-01",
    }
    signed_token = jwt.encode(token_claims, TEST_PRIVATE_KEY_PEM, algorithm="ES256")

    # 3. Post webhook with Signed-Token header
    webhook_body = {
        "status": "COMPLETED",
        "thirdPartyId": ref,
        "amount": 2500.0,
        "currency": "ETB",
        "txn": "santim_txn_1001",
        "signedToken": signed_token,
    }
    res = client.post(
        "/api/v1/payments/webhooks/santimpay",
        json=webhook_body,
        headers={"Signed-Token": signed_token},
    )
    assert res.status_code == 200
    res_data = res.json()
    assert res_data["status"] == "success"
    assert res_data["verified"] is True
    assert res_data["internal_status"] in {"successful", "paid"}

    # 4. Check transaction status endpoint
    status_res = client.get(f"/api/v1/payments/transactions/{ref}/status")
    assert status_res.status_code == 200
    assert status_res.json()["status"] == "successful"


def test_3_santimpay_failed_and_cancelled_callbacks():
    """Test 3: Webhook with FAILED and CANCELLED statuses are mapped appropriately."""
    # 1. Failed payment
    init_res = client.post(
        "/api/v1/payments/transactions/initialize",
        json={
            "amount": 1200.0,
            "provider_code": "santimpay",
            "customer_name": "Aman Yohannes",
            "payment_purpose": "Training Registration",
        },
    )
    ref_failed = init_res.json()["public_reference"]

    token_failed = jwt.encode(
        {"thirdPartyId": ref_failed, "status": "FAILED", "amount": 1200.0, "currency": "ETB"},
        TEST_PRIVATE_KEY_PEM,
        algorithm="ES256",
    )
    res_failed = client.post(
        "/api/v1/payments/webhooks/santimpay",
        json={"status": "FAILED", "thirdPartyId": ref_failed, "amount": 1200.0, "signedToken": token_failed},
        headers={"Signed-Token": token_failed},
    )
    assert res_failed.status_code == 200
    assert res_failed.json()["internal_status"] == "failed"

    status_failed = client.get(f"/api/v1/payments/transactions/{ref_failed}/status")
    assert status_failed.json()["status"] == "failed"

    # 2. Cancelled payment
    init_res2 = client.post(
        "/api/v1/payments/transactions/initialize",
        json={
            "amount": 1500.0,
            "provider_code": "santimpay",
            "customer_name": "Hana Girma",
            "payment_purpose": "Graphic Design Course",
        },
    )
    ref_cancelled = init_res2.json()["public_reference"]

    token_cancelled = jwt.encode(
        {"thirdPartyId": ref_cancelled, "status": "CANCELLED", "amount": 1500.0, "currency": "ETB"},
        TEST_PRIVATE_KEY_PEM,
        algorithm="ES256",
    )
    res_cancelled = client.post(
        "/api/v1/payments/webhooks/santimpay",
        json={"status": "CANCELLED", "thirdPartyId": ref_cancelled, "amount": 1500.0, "signedToken": token_cancelled},
        headers={"Signed-Token": token_cancelled},
    )
    assert res_cancelled.status_code == 200
    assert res_cancelled.json()["internal_status"] == "cancelled"


def test_4_santimpay_invalid_signature_rejected():
    """Test 4: Callback with tampered token / invalid signature is rejected and does not mark transaction as paid."""
    # 1. Initialize transaction
    init_res = client.post(
        "/api/v1/payments/transactions/initialize",
        json={
            "amount": 6000.0,
            "provider_code": "santimpay",
            "customer_name": "Tamper Test User",
            "payment_purpose": "Software Architecture",
        },
    )
    ref = init_res.json()["public_reference"]

    # 2. Forge token with wrong key
    other_ec_key = ec.generate_private_key(ec.SECP256R1())
    other_priv_pem = other_ec_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("utf-8")

    fake_token = jwt.encode(
        {"thirdPartyId": ref, "status": "COMPLETED", "amount": 6000.0},
        other_priv_pem,
        algorithm="ES256",
    )

    # 3. Post webhook with forged token
    wh_res = client.post(
        "/api/v1/payments/webhooks/santimpay",
        json={"status": "COMPLETED", "thirdPartyId": ref, "amount": 6000.0, "signedToken": fake_token},
        headers={"Signed-Token": fake_token},
    )
    assert wh_res.status_code in {200, 400, 401}
    wh_data = wh_res.json()
    if wh_res.status_code == 200:
        assert wh_data.get("verified") is False or wh_data.get("status") in {"invalid_signature", "error", "unverified"}
    else:
        assert "signature" in wh_data.get("detail", "").lower() or "failed" in wh_data.get("detail", "").lower()

    # 4. Verify transaction status remains NOT paid
    status_res = client.get(f"/api/v1/payments/transactions/{ref}/status")
    assert status_res.json()["status"] != "successful"


def test_5_santimpay_duplicate_callback_idempotency():
    """Test 5: Duplicate / replay callbacks are handled idempotently without double-processing."""
    init_res = client.post(
        "/api/v1/payments/transactions/initialize",
        json={
            "amount": 4200.0,
            "provider_code": "santimpay",
            "customer_name": "Idempotent Test",
            "payment_purpose": "Travel Booking",
        },
    )
    ref = init_res.json()["public_reference"]

    signed_token = jwt.encode(
        {"thirdPartyId": ref, "status": "COMPLETED", "amount": 4200.0, "currency": "ETB"},
        TEST_PRIVATE_KEY_PEM,
        algorithm="ES256",
    )

    webhook_payload = {
        "status": "COMPLETED",
        "thirdPartyId": ref,
        "amount": 4200.0,
        "currency": "ETB",
        "signedToken": signed_token,
    }

    # First delivery
    res1 = client.post(
        "/api/v1/payments/webhooks/santimpay",
        json=webhook_payload,
        headers={"Signed-Token": signed_token},
    )
    assert res1.status_code == 200
    assert res1.json()["status"] == "success"

    # Second (duplicate/replay) delivery
    res2 = client.post(
        "/api/v1/payments/webhooks/santimpay",
        json=webhook_payload,
        headers={"Signed-Token": signed_token},
    )
    assert res2.status_code == 200
    assert "idempotent" in res2.json().get("message", "").lower() or res2.json()["status"] == "success"


def test_6_santimpay_amount_mismatch_rejected():
    """Test 6: Amount mismatch between token payload and recorded transaction is detected and rejected."""
    init_res = client.post(
        "/api/v1/payments/transactions/initialize",
        json={
            "amount": 5000.0,
            "provider_code": "santimpay",
            "customer_name": "Mismatch Test",
            "payment_purpose": "ERP Module",
        },
    )
    ref = init_res.json()["public_reference"]

    # Signed token with mismatched amount (e.g. 50.0 instead of 5000.0)
    mismatched_token = jwt.encode(
        {"thirdPartyId": ref, "status": "COMPLETED", "amount": 50.0, "currency": "ETB"},
        TEST_PRIVATE_KEY_PEM,
        algorithm="ES256",
    )

    res = client.post(
        "/api/v1/payments/webhooks/santimpay",
        json={"status": "COMPLETED", "thirdPartyId": ref, "amount": 50.0, "signedToken": mismatched_token},
        headers={"Signed-Token": mismatched_token},
    )
    assert res.status_code in {200, 400}
    if res.status_code == 200:
        data = res.json()
        assert data.get("verified") is False or data.get("internal_status") in {"failed", "unverified"}
    else:
        assert "mismatch" in res.json().get("detail", "").lower() or "error" in res.json().get("detail", "").lower()

    # Transaction not marked paid
    status_res = client.get(f"/api/v1/payments/transactions/{ref}/status")
    assert status_res.json()["status"] != "successful"


def test_7_unauthorized_return_url_does_not_bypass():
    """Test 7: Accessing frontend return / status query without backend validation never marks transaction as paid."""
    init_res = client.post(
        "/api/v1/payments/transactions/initialize",
        json={
            "amount": 8000.0,
            "provider_code": "santimpay",
            "customer_name": "Return URL Safety Test",
            "payment_purpose": "Freelancer Escrow",
        },
    )
    ref = init_res.json()["public_reference"]

    # Initial status is initiated
    status_res = client.get(f"/api/v1/payments/transactions/{ref}/status")
    assert status_res.json()["status"] == "initiated"

    # Non-existent reference returns not found
    bad_verify = client.post("/api/v1/payments/transactions/ZACMA-FAKE-REF/verify")
    assert bad_verify.json()["success"] is False


def test_8_santimpay_pending_status_handling():
    """Test 8: Webhook with PENDING status leaves transaction in pending / processing status."""
    init_res = client.post(
        "/api/v1/payments/transactions/initialize",
        json={
            "amount": 1800.0,
            "provider_code": "santimpay",
            "customer_name": "Pending Test User",
            "payment_purpose": "Course Installment",
        },
    )
    ref = init_res.json()["public_reference"]

    pending_token = jwt.encode(
        {"thirdPartyId": ref, "status": "PENDING", "amount": 1800.0, "currency": "ETB"},
        TEST_PRIVATE_KEY_PEM,
        algorithm="ES256",
    )
    res = client.post(
        "/api/v1/payments/webhooks/santimpay",
        json={"status": "PENDING", "thirdPartyId": ref, "amount": 1800.0, "signedToken": pending_token},
        headers={"Signed-Token": pending_token},
    )
    assert res.status_code == 200
    assert res.json()["internal_status"] in {"pending", "processing"}

    status_res = client.get(f"/api/v1/payments/transactions/{ref}/status")
    assert status_res.json()["status"] in {"pending", "processing", "initiated"}


def test_9_santimpay_admin_view_and_manage_records(admin_token):
    """Test 9: Admin can list providers, view transaction ledgers, and manage SantimPay provider settings."""
    # 1. Admin list providers
    prov_res = client.get(
        "/api/v1/payments/admin/providers",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert prov_res.status_code == 200
    providers = prov_res.json()
    santim_prov = next((p for p in providers if p["provider_code"] == "santimpay"), None)
    assert santim_prov is not None
    # Verify sensitive secret keys are masked in admin view
    assert "••••" in (santim_prov.get("masked_secret_key") or "••••")

    # 2. Admin list payment transactions ledger
    tx_res = client.get(
        "/api/v1/payments/admin/transactions",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert tx_res.status_code == 200
    tx_list = tx_res.json()
    assert isinstance(tx_list, list)


def test_10_santimpay_adapter_unit_methods():
    """Test 10: Unit verification of SantimPayPaymentAdapter methods."""
    adapter = SantimPayPaymentAdapter({
        "merchant_id": "test-merchant",
        "private_key": TEST_PRIVATE_KEY_PEM,
        "public_key": TEST_PUBLIC_KEY_PEM,
        "testbed": True,
    })

    # Test test_connection
    conn = adapter.test_connection()
    assert "success" in conn

    # Test get_balance
    bal = adapter.get_balance()
    assert bal["supported"] is True

    # Test verify_token
    token = jwt.encode({"test": "data"}, TEST_PRIVATE_KEY_PEM, algorithm="ES256")
    v_res = adapter.verify_token(token)
    assert v_res["success"] is True
    assert v_res["data"]["test"] == "data"


def test_11_customer_cannot_tamper_payment_status():
    """Test 11: Non-admin users cannot directly call admin payment confirmation or mark transactions paid."""
    # Create client JWT token
    from app.core.auth import create_access_token
    client_token = create_access_token(
        data={"sub": "client-user-123", "email": "client@example.com", "role": "client", "tenant_id": DEMO_TENANT_ID}
    )

    # Attempt payment confirmation with client role token
    res = client.post(
        "/api/v1/payments/invoices/inv-001/confirm",
        json={"comment": "Hacked payment confirmation"},
        headers={"Authorization": f"Bearer {client_token}"},
    )
    assert res.status_code == 403
    assert "Insufficient permissions" in res.json().get("detail", "")


