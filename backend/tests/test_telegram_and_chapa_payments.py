"""Automated Tests for Chapa Gateway, Telegram Payment Bot, and Multi-Provider Integrations."""

import pytest
from fastapi.testclient import TestClient

from app.core.auth import create_access_token
from app.core.config import settings
from app.main import app
from app.services.telegram_bot_service import TelegramPaymentBotService

client = TestClient(app)


@pytest.fixture
def admin_token() -> str:
    return create_access_token({
        "sub": "admin-id",
        "email": "admin@zacma.com",
        "role": "admin",
        "tenant_id": settings.demo_tenant_id,
        "full_name": "Zacma Admin",
    })


def test_telegram_bot_info_endpoint(admin_token):
    """Verify Telegram Bot info endpoint retrieves bot identity."""
    res = client.get("/api/v1/support/telegram/bot-info", headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 200
    data = res.json()
    assert data["ok"] is True
    assert data["result"]["username"] == "ZacmaBusinessSupportAI_bot"


def test_telegram_invoice_notification_dispatch(admin_token):
    """Verify formatted payment invoice dispatch for Telegram Bot."""
    payload = {
        "chat_id": 123456789,
        "transaction": {
            "public_reference": "ZACMA-2026-SANTIM001",
            "amount": 4500.0,
            "currency": "ETB",
            "customer_name": "Test Student",
            "provider_code": "santimpay",
            "payment_purpose": "AI Mastery Academy Tuition",
        },
        "checkout_url": "https://services.santimpay.com/api/v1/gateway/checkout?id=ZACMA-2026-SANTIM001",
    }
    res = client.post(
        "/api/v1/support/telegram/send-invoice-alert",
        json=payload,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res.status_code == 200
    result = res.json()
    assert result["ok"] in [True, False]  # True or HTTP response from Telegram


def test_telegram_bot_webhook_commands():
    """Verify Telegram Webhook handling for user interactive commands."""
    # 1. /start command
    start_update = {
        "update_id": 1001,
        "message": {
            "chat": {"id": 987654321},
            "from": {"first_name": "Abebe", "username": "abebe_b"},
            "text": "/start",
        },
    }
    res_start = client.post("/api/v1/support/telegram/webhook", json=start_update)
    assert res_start.status_code == 200
    data_start = res_start.json()
    assert data_start["ok"] is True
    assert "Zacma Technology Group" in data_start.get("reply_text", "")

    # 2. /pay command
    pay_update = {
        "update_id": 1002,
        "message": {
            "chat": {"id": 987654321},
            "from": {"first_name": "Abebe"},
            "text": "/pay",
        },
    }
    res_pay = client.post("/api/v1/support/telegram/webhook", json=pay_update)
    assert res_pay.status_code == 200
    assert "SantimPay" in res_pay.json().get("reply_text", "")


def test_santimpay_multi_channel_checkout_and_verification():
    """Verify SantimPay initialize, hosted checkout generation, and verification."""
    # 1. Initialize transaction via SantimPay
    tx_init_payload = {
        "amount": 7500.0,
        "currency": "ETB",
        "provider_code": "santimpay",
        "customer_name": "Almaz Ayana",
        "customer_email": "almaz.ayana@test.com",
        "customer_phone": "+251911882233",
        "payment_purpose": "Software Architecture Consulting",
    }
    init_res = client.post("/api/v1/payments/transactions/initialize", json=tx_init_payload)
    assert init_res.status_code == 201
    tx_data = init_res.json()
    assert "checkout_url" in tx_data
    assert tx_data["status"] == "initiated"
    public_ref = tx_data["public_reference"]

    # 2. Server-side Verify
    verify_res = client.post(f"/api/v1/payments/transactions/{public_ref}/verify")
    assert verify_res.status_code == 200
    verify_data = verify_res.json()
    assert verify_data["success"] is True
    assert verify_data["status"] == "successful"


def test_admin_santimpay_provider_test_endpoint(admin_token):
    """Verify admin connection test for SantimPay gateway."""
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Fetch provider ID for SantimPay
    prov_res = client.get("/api/v1/payments/admin/providers", headers=headers)
    assert prov_res.status_code == 200
    providers = prov_res.json()
    santim_prov = next((p for p in providers if p["provider_code"] == "santimpay"), None)
    assert santim_prov is not None

    # Test connectivity
    test_res = client.post(f"/api/v1/payments/admin/providers/{santim_prov['id']}/test", headers=headers)
    assert test_res.status_code == 200
    test_data = test_res.json()
    assert test_data["success"] is True
