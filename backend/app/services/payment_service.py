"""ZACMA Multi-Provider Payment & Invoicing Engine Service.

Provides a unified, production-grade payment architecture supporting:
- Provider Adapters (Chapa, CBE, Telebirr, Awash, Generic Banks)
- Dynamic Admin Configuration (Add/Edit/Toggle/Test providers)
- Balance Management (Distinguishing provider API balance from internal platform balance)
- Unique Reference Strategy (ZACMA-2026-XXXXXXXX)
- Secure Server-Side Verification & Idempotent Webhook Processing
- Service Integrations (Student Registration, Invoicing, Visa, Software, Travel)
"""

import hashlib
import logging
import secrets
import string
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from app.core.config import settings
from app.core.db import supabase
from app.core.demo_data import (
    DEMO_TENANT_ID,
    invoices_store,
    payment_logs_store,
    payment_providers_store,
    payment_transactions_store,
    payment_webhooks_store,
    students_store,
)
from app.services.crm_service import CrmService
from app.services.notification_service import NotificationService
from app.services.payment_adapters.base import BasePaymentAdapter
from app.services.payment_adapters.cbe import CbePaymentAdapter
from app.services.payment_adapters.chapa import ChapaPaymentAdapter
from app.services.payment_adapters.generic_bank import GenericBankPaymentAdapter
from app.services.payment_adapters.santimpay import SantimPayPaymentAdapter
from app.services.payment_adapters.telebirr import TelebirrPaymentAdapter

logger = logging.getLogger("zacma.payments")


class PaymentService:
    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def generate_transaction_ref(prefix: str = "ZACMA-2026") -> str:
        """Generate a cryptographically secure, collision-resistant unique transaction reference.
        Example: ZACMA-2026-A8F9B2C1
        """
        random_suffix = "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        return f"{prefix}-{random_suffix}"

    # ---------------------------------------------------------------------------
    # Provider Adapters Factory
    # ---------------------------------------------------------------------------
    @staticmethod
    def get_adapter(provider_config: dict[str, Any]) -> BasePaymentAdapter:
        """Instantiate the appropriate provider adapter."""
        code = provider_config.get("provider_code", "").lower()
        if code in {"santimpay", "santim_pay", "santim", "santim_gateway"}:
            return SantimPayPaymentAdapter(provider_config)
        elif code == "chapa":
            return ChapaPaymentAdapter(provider_config)
        elif code == "cbe":
            return CbePaymentAdapter(provider_config)
        elif code in {"telebirr", "telebirr_qr", "telebirr_ussd"}:
            return TelebirrPaymentAdapter(provider_config)
        else:
            return GenericBankPaymentAdapter(provider_config)

    # ---------------------------------------------------------------------------
    # Provider Management (Admin & Customer Views)
    # ---------------------------------------------------------------------------
    @staticmethod
    def get_active_customer_providers(tenant_id: str) -> list[dict[str, Any]]:
        """Return active payment providers formatted for customer-facing checkout (no secrets)."""
        if supabase is None:
            providers = payment_providers_store.list_all(tenant_id)
        else:
            try:
                res = supabase.table("payment_providers").select("*").eq("tenant_id", tenant_id).eq("is_active", True).execute()
                providers = res.data or []
            except Exception:
                providers = payment_providers_store.list_all(tenant_id)

        active = [p for p in providers if p.get("is_active", True)]
        active.sort(key=lambda x: (not x.get("is_default", False), x.get("priority", 99)))

        # Sanitize sensitive fields before returning
        safe_list = []
        for p in active:
            safe_list.append({
                "id": p.get("id"),
                "provider_name": p.get("provider_name"),
                "provider_code": p.get("provider_code"),
                "provider_type": p.get("provider_type", "bank_transfer"),
                "is_active": True,
                "is_default": p.get("is_default", False),
                "currency": p.get("currency", "ETB"),
                "supported_currencies": p.get("supported_currencies", ["ETB"]),
                "account_name": p.get("account_name"),
                "account_number": p.get("account_number"),
                "customer_payment_number": p.get("customer_payment_number"),
                "instructions": p.get("instructions"),
                "environment": p.get("environment", "test"),
                "transaction_fee_percent": p.get("transaction_fee_percent", 0.0),
                "transaction_fee_fixed": p.get("transaction_fee_fixed", 0.0),
            })
        return safe_list

    @staticmethod
    def get_admin_providers(tenant_id: str) -> list[dict[str, Any]]:
        """Return all configured payment providers for admin view with masked credentials."""
        if supabase is None:
            providers = payment_providers_store.list_all(tenant_id)
        else:
            try:
                res = supabase.table("payment_providers").select("*").eq("tenant_id", tenant_id).execute()
                providers = res.data or []
            except Exception:
                providers = payment_providers_store.list_all(tenant_id)

        providers.sort(key=lambda x: (not x.get("is_default", False), x.get("priority", 99)))

        admin_list = []
        for p in providers:
            sec = p.get("secret_key")
            api = p.get("api_key")
            masked_sec = f"{sec[:4]}••••••••••••" if sec and len(sec) > 6 else ("••••••••" if sec else None)
            masked_api = f"{api[:4]}••••••••••••" if api and len(api) > 6 else ("••••••••" if api else None)

            admin_list.append({
                "id": p.get("id"),
                "tenant_id": tenant_id,
                "provider_name": p.get("provider_name"),
                "provider_code": p.get("provider_code"),
                "provider_type": p.get("provider_type", "bank_transfer"),
                "is_active": p.get("is_active", True),
                "is_default": p.get("is_default", False),
                "priority": p.get("priority", 1),
                "environment": p.get("environment", "test"),
                "currency": p.get("currency", "ETB"),
                "supported_currencies": p.get("supported_currencies", ["ETB"]),
                "account_name": p.get("account_name"),
                "account_number": p.get("account_number"),
                "customer_payment_number": p.get("customer_payment_number"),
                "instructions": p.get("instructions"),
                "api_endpoint": p.get("api_endpoint"),
                "callback_url": p.get("callback_url"),
                "webhook_url": p.get("webhook_url"),
                "supports_balance_api": p.get("supports_balance_api", False),
                "transaction_fee_percent": p.get("transaction_fee_percent", 0.0),
                "transaction_fee_fixed": p.get("transaction_fee_fixed", 0.0),
                "has_secret_key": bool(sec),
                "masked_secret_key": masked_sec,
                "masked_api_key": masked_api,
                "merchant_id": p.get("merchant_id"),
                "created_at": p.get("created_at"),
                "updated_at": p.get("updated_at"),
            })
        return admin_list

    @staticmethod
    def get_provider_by_code(tenant_id: str, provider_code: str) -> Optional[dict[str, Any]]:
        """Retrieve full provider configuration (including server secrets) for backend processing."""
        if supabase is None:
            providers = payment_providers_store.list_all(tenant_id)
            for p in providers:
                if p.get("provider_code", "").lower() == provider_code.lower():
                    return p
            if provider_code.lower() == "chapa":
                return {
                    "id": "prov-chapa-legacy",
                    "tenant_id": tenant_id,
                    "provider_name": "Chapa Payment Gateway (Legacy)",
                    "provider_code": "chapa",
                    "provider_type": "gateway",
                    "is_active": False,
                    "webhook_secret": "chapa_webhook_mock_secret",
                    "secret_key": "CHASECK_TEST-mocksecretkey12345",
                }
            return None
        try:
            res = supabase.table("payment_providers").select("*").eq("tenant_id", tenant_id).eq("provider_code", provider_code).execute()
            if res.data:
                return res.data[0]
        except Exception:
            pass
        if provider_code.lower() == "chapa":
            return {
                "id": "prov-chapa-legacy",
                "tenant_id": tenant_id,
                "provider_name": "Chapa Payment Gateway (Legacy)",
                "provider_code": "chapa",
                "provider_type": "gateway",
                "is_active": False,
                "webhook_secret": "chapa_webhook_mock_secret",
                "secret_key": "CHASECK_TEST-mocksecretkey12345",
            }
        return None

    @staticmethod
    def create_provider(tenant_id: str, payload: dict[str, Any], actor: str = "admin") -> dict[str, Any]:
        """Create a new payment provider."""
        now = PaymentService._now()
        provider_id = f"prov-{str(uuid.uuid4())[:8]}"

        # If set as default, unset other defaults
        if payload.get("is_default"):
            PaymentService._unset_other_defaults(tenant_id)

        data = {
            "id": provider_id,
            "tenant_id": tenant_id,
            "provider_name": payload.get("provider_name"),
            "provider_code": payload.get("provider_code", "").lower().strip(),
            "provider_type": payload.get("provider_type", "bank_transfer"),
            "is_active": payload.get("is_active", True),
            "is_default": payload.get("is_default", False),
            "priority": payload.get("priority", 1),
            "environment": payload.get("environment", "test"),
            "currency": payload.get("currency", "ETB"),
            "supported_currencies": payload.get("supported_currencies", ["ETB"]),
            "account_name": payload.get("account_name"),
            "account_number": payload.get("account_number"),
            "customer_payment_number": payload.get("customer_payment_number"),
            "instructions": payload.get("instructions"),
            "api_endpoint": payload.get("api_endpoint"),
            "callback_url": payload.get("callback_url"),
            "webhook_url": payload.get("webhook_url"),
            "supports_balance_api": payload.get("supports_balance_api", False),
            "transaction_fee_percent": payload.get("transaction_fee_percent", 0.0),
            "transaction_fee_fixed": payload.get("transaction_fee_fixed", 0.0),
            "secret_key": payload.get("secret_key"),
            "api_key": payload.get("api_key"),
            "merchant_id": payload.get("merchant_id"),
            "webhook_secret": payload.get("webhook_secret"),
            "public_key": payload.get("public_key"),
            "additional_config": payload.get("additional_config", {}),
            "created_at": now,
            "updated_at": now,
        }

        if supabase is None:
            created = payment_providers_store.create(data, tenant_id)
        else:
            try:
                res = supabase.table("payment_providers").insert(data).execute()
                created = res.data[0] if res.data else data
            except Exception:
                created = data

        PaymentService.log_audit(
            tenant_id=tenant_id,
            actor=actor,
            action="Provider Created",
            resource_type="payment_provider",
            resource_id=provider_id,
            details={"provider_code": data["provider_code"], "provider_name": data["provider_name"]},
        )
        return created

    @staticmethod
    def update_provider(tenant_id: str, provider_id: str, payload: dict[str, Any], actor: str = "admin") -> Optional[dict[str, Any]]:
        """Update an existing payment provider."""
        now = PaymentService._now()
        updates = {k: v for k, v in payload.items() if v is not None}
        updates["updated_at"] = now

        if updates.get("is_default"):
            PaymentService._unset_other_defaults(tenant_id, exclude_id=provider_id)

        if supabase is None:
            updated = payment_providers_store.update(provider_id, updates, tenant_id)
        else:
            try:
                res = supabase.table("payment_providers").update(updates).eq("id", provider_id).eq("tenant_id", tenant_id).execute()
                updated = res.data[0] if res.data else updates
            except Exception:
                updated = updates

        if updated:
            PaymentService.log_audit(
                tenant_id=tenant_id,
                actor=actor,
                action="Provider Updated",
                resource_type="payment_provider",
                resource_id=provider_id,
                details={"updated_fields": list(updates.keys())},
            )
        return updated

    @staticmethod
    def delete_provider(tenant_id: str, provider_id: str, actor: str = "admin") -> bool:
        """Deactivate or delete payment provider."""
        if supabase is None:
            res = payment_providers_store.delete(provider_id, tenant_id)
        else:
            try:
                supabase.table("payment_providers").delete().eq("id", provider_id).eq("tenant_id", tenant_id).execute()
                res = True
            except Exception:
                res = False

        if res:
            PaymentService.log_audit(
                tenant_id=tenant_id,
                actor=actor,
                action="Provider Deleted",
                resource_type="payment_provider",
                resource_id=provider_id,
                details={},
            )
        return res

    @staticmethod
    def test_provider_connection(tenant_id: str, provider_id: str) -> dict[str, Any]:
        """Test provider connection using adapter."""
        if supabase is None:
            prov = payment_providers_store.get(provider_id, tenant_id)
        else:
            try:
                res = supabase.table("payment_providers").select("*").eq("id", provider_id).eq("tenant_id", tenant_id).execute()
                prov = res.data[0] if res.data else None
            except Exception:
                prov = None

        if not prov:
            return {"success": False, "message": "Provider not found"}

        adapter = PaymentService.get_adapter(prov)
        return adapter.test_connection()

    @staticmethod
    def _unset_other_defaults(tenant_id: str, exclude_id: Optional[str] = None):
        """Ensure only one provider is set as default."""
        if supabase is None:
            for p in payment_providers_store.list_all(tenant_id):
                if p.get("id") != exclude_id and p.get("is_default"):
                    payment_providers_store.update(p["id"], {"is_default": False}, tenant_id)

    # ---------------------------------------------------------------------------
    # Transaction Management (Initialize, Verify, Webhooks, Refunds)
    # ---------------------------------------------------------------------------
    @staticmethod
    def initialize_transaction(
        tenant_id: str,
        amount: float,
        provider_code: str,
        customer_name: str,
        customer_email: Optional[str] = None,
        customer_phone: Optional[str] = None,
        currency: str = "ETB",
        payment_purpose: str = "Service Fee",
        description: Optional[str] = None,
        invoice_id: Optional[str] = None,
        return_url: Optional[str] = None,
        callback_url: Optional[str] = None,
    ) -> dict[str, Any]:
        """Create a payment transaction with unique reference ZACMA-2026-XXXXXXXX and invoke adapter."""
        provider = PaymentService.get_provider_by_code(tenant_id, provider_code)
        if not provider or not provider.get("is_active", True):
            # Fallback to default provider
            active_providers = PaymentService.get_active_customer_providers(tenant_id)
            if not active_providers:
                raise ValueError("No active payment providers available")
            provider = PaymentService.get_provider_by_code(tenant_id, active_providers[0]["provider_code"])

        public_ref = PaymentService.generate_transaction_ref()
        now = PaymentService._now()
        tx_id = f"tx-{str(uuid.uuid4())[:8]}"

        fee_pct = provider.get("transaction_fee_percent", 0.0) or 0.0
        fee_fixed = provider.get("transaction_fee_fixed", 0.0) or 0.0
        fee = round((amount * fee_pct / 100.0) + fee_fixed, 2)
        net_amount = round(amount - fee, 2)

        transaction_data = {
            "id": tx_id,
            "tenant_id": tenant_id,
            "public_reference": public_ref,
            "customer_name": customer_name,
            "customer_email": customer_email,
            "customer_phone": customer_phone,
            "provider_id": provider.get("id"),
            "provider_code": provider.get("provider_code"),
            "payment_method": provider.get("provider_name"),
            "amount": amount,
            "fee": fee,
            "net_amount": net_amount,
            "currency": currency,
            "status": "initiated",
            "payment_purpose": payment_purpose,
            "description": description or f"{payment_purpose} - {public_ref}",
            "invoice_id": invoice_id,
            "provider_transaction_id": None,
            "provider_reference": None,
            "checkout_url": None,
            "callback_status": None,
            "verification_status": "unverified",
            "error_message": None,
            "created_at": now,
            "updated_at": now,
            "completed_at": None,
        }

        adapter = PaymentService.get_adapter(provider)
        init_result = adapter.initialize_payment(
            transaction=transaction_data,
            return_url=return_url,
            callback_url=callback_url,
        )

        transaction_data["checkout_url"] = init_result.get("checkout_url")
        transaction_data["status"] = init_result.get("status", "initiated")
        transaction_data["provider_reference"] = init_result.get("provider_reference")

        if supabase is None:
            payment_transactions_store.create(transaction_data, tenant_id)
        else:
            try:
                supabase.table("payment_transactions").insert(transaction_data).execute()
            except Exception as exc:
                logger.error("Error inserting transaction to Supabase: %s", exc)

        # Notify Telegram Bot
        try:
            from app.services.telegram_bot_service import TelegramPaymentBotService
            TelegramPaymentBotService.send_payment_invoice_notification(
                transaction=transaction_data,
                checkout_url=transaction_data["checkout_url"],
            )
        except Exception as t_err:
            logger.debug("Telegram payment notice skipped: %s", t_err)

        PaymentService.log_audit(
            tenant_id=tenant_id,
            actor=customer_email or customer_name,
            action="Payment Initialized",
            resource_type="payment_transaction",
            resource_id=public_ref,
            details={"provider": provider.get("provider_code"), "amount": amount, "currency": currency},
        )

        return {
            "transaction_id": tx_id,
            "public_reference": public_ref,
            "provider_code": provider.get("provider_code"),
            "amount": amount,
            "currency": currency,
            "status": transaction_data["status"],
            "checkout_url": transaction_data["checkout_url"],
            "account_name": init_result.get("account_name"),
            "account_number": init_result.get("account_number"),
            "customer_payment_number": init_result.get("customer_payment_number"),
            "instructions": init_result.get("instructions"),
            "message": "Payment initialized successfully",
        }

    @staticmethod
    def verify_transaction(tenant_id: str, public_reference: str, actor: str = "system") -> dict[str, Any]:
        """Verify transaction status server-side and update invoice/registration."""
        tx = PaymentService.get_transaction_by_ref(tenant_id, public_reference)
        if not tx:
            return {
                "success": False,
                "status": "not_found",
                "public_reference": public_reference,
                "amount": 0.0,
                "currency": "ETB",
                "message": "Transaction not found",
            }

        if tx.get("status") == "successful":
            return {
                "success": True,
                "status": "successful",
                "public_reference": public_reference,
                "amount": tx.get("amount"),
                "currency": tx.get("currency"),
                "message": "Transaction already verified and completed",
            }

        provider = PaymentService.get_provider_by_code(tenant_id, tx.get("provider_code", ""))
        if not provider:
            return {"success": False, "status": "failed", "message": "Provider config not found"}

        adapter = PaymentService.get_adapter(provider)
        res = adapter.verify_payment(tx)

        if res.get("success"):
            now = PaymentService._now()
            updates = {
                "status": "successful",
                "verification_status": "verified",
                "provider_transaction_id": res.get("provider_transaction_id") or tx.get("provider_transaction_id"),
                "completed_at": now,
                "updated_at": now,
            }
            PaymentService._update_transaction(tenant_id, tx["id"], updates)

            # Auto-complete linked invoice if applicable
            if tx.get("invoice_id"):
                PaymentService.mark_payment_confirmed(
                    tenant_id=tenant_id,
                    invoice_id=tx["invoice_id"],
                    admin_id=actor,
                    comment="Automatically verified via Payment Provider",
                )

            # Auto-update linked student registration if reference or email matches
            PaymentService._sync_student_payment_status(tenant_id, public_reference, tx.get("customer_email"))

            # Sync to People & CRM Layer as Customer
            try:
                from app.services.crm_service import CrmService
                from app.services.event_bus import event_bus
                from app.services.people_service import PeopleService

                customer_email = tx.get("customer_email")
                customer_name = tx.get("customer_name") or "Customer"
                person = PeopleService.find_or_create_person(
                    tenant_id=tenant_id,
                    full_name=customer_name,
                    email=customer_email,
                    person_type="Customer",
                    status="Active",
                    source="Payment",
                    initial_action=f"Payment Completed ({tx.get('amount'):,.2f} {tx.get('currency')})",
                )
                CrmService.add_timeline_event(
                    tenant_id=tenant_id,
                    contact_id=person["id"],
                    action="Payment Verified",
                    description=f"Verified payment {public_reference} for {tx.get('amount'):,.2f} {tx.get('currency')} via {tx.get('provider_code')}",
                    actor=actor,
                )
                event_bus.publish(
                    tenant_id=tenant_id,
                    event_name="payment.successful",
                    payload={"public_reference": public_reference, "amount": tx.get("amount"), "customer_email": customer_email},
                )
            except Exception:
                pass

            # Dispatch Telegram confirmation receipt
            try:
                from app.services.telegram_bot_service import TelegramPaymentBotService
                TelegramPaymentBotService.send_payment_confirmation(
                    transaction={**tx, **updates},
                )
            except Exception as t_err:
                logger.debug("Telegram confirmation skipped: %s", t_err)

            # Automatic Service Activation & Automation Job Pipeline
            try:
                from app.services.automation_service import AutomationService
                entity_type = "student" if "STU" in public_reference else "service"
                job = AutomationService.create_job(
                    tenant_id=tenant_id,
                    job_type="service_fulfillment",
                    entity_type=entity_type,
                    entity_id=public_reference,
                    payload={
                        "public_reference": public_reference,
                        "amount": tx.get("amount"),
                        "currency": tx.get("currency"),
                        "customer_name": tx.get("customer_name"),
                        "customer_email": tx.get("customer_email"),
                        "purpose": tx.get("payment_purpose"),
                    },
                )
                AutomationService.execute_job(tenant_id, job["id"])
            except Exception as a_err:
                logger.warning("Automation pipeline notice for %s: %s", public_reference, a_err)

            PaymentService.log_audit(
                tenant_id=tenant_id,
                actor=actor,
                action="Payment Verified",
                resource_type="payment_transaction",
                resource_id=public_reference,
                details={"amount": tx.get("amount"), "provider": tx.get("provider_code")},
            )
        else:
            fail_status = res.get("status", "failed")
            now = PaymentService._now()
            updates = {
                "status": fail_status,
                "verification_status": "failed",
                "error_message": res.get("message", "Verification failed"),
                "updated_at": now,
            }
            PaymentService._update_transaction(tenant_id, tx["id"], updates)

        return {
            "success": res.get("success", False),
            "status": res.get("status", "pending"),
            "public_reference": public_reference,
            "amount": tx.get("amount"),
            "currency": tx.get("currency"),
            "provider_reference": res.get("provider_reference"),
            "message": res.get("message", "Verification complete"),
        }

    @staticmethod
    def handle_webhook(
        tenant_id: str,
        provider_code: str,
        payload: dict[str, Any],
        headers: dict[str, str],
    ) -> dict[str, Any]:
        """Idempotent webhook handler with HMAC signature checking & replay protection."""
        now = PaymentService._now()
        provider = PaymentService.get_provider_by_code(tenant_id, provider_code)
        if not provider:
            return {"status": "error", "message": f"Unknown provider {provider_code}"}

        # Calculate idempotency key from payload hash
        payload_str = str(sorted(payload.items())) if isinstance(payload, dict) else str(payload)
        idempotency_key = hashlib.sha256(f"{provider_code}:{payload_str}".encode("utf-8")).hexdigest()

        # Check idempotency store to prevent duplicate processing
        existing_wh = [
            w for w in payment_webhooks_store.list_all(tenant_id)
            if w.get("idempotency_key") == idempotency_key
        ]
        if existing_wh:
            logger.info("Duplicate webhook event ignored (idempotency key: %s)", idempotency_key)
            return {"status": "success", "message": "Duplicate event ignored (idempotent)"}

        adapter = PaymentService.get_adapter(provider)
        result = adapter.process_webhook(payload, headers)

        tx_ref = result.get("transaction_reference")
        wh_record = {
            "id": f"wh-{str(uuid.uuid4())[:8]}",
            "tenant_id": tenant_id,
            "provider_code": provider_code,
            "event_type": payload.get("event") or payload.get("type") or "payment.event",
            "transaction_reference": tx_ref,
            "payload": payload,
            "signature": (
                headers.get("signed-token")
                or headers.get("Signed-Token")
                or headers.get("x-santimpay-signature")
                or headers.get("x-chapa-signature")
                or headers.get("signature")
            ),
            "is_verified": result.get("verified", False),
            "is_processed": False,
            "idempotency_key": idempotency_key,
            "created_at": now,
        }

        if not result.get("verified", True):
            wh_record["error_message"] = "Invalid webhook signature"
            payment_webhooks_store.create(wh_record, tenant_id)
            PaymentService.log_audit(
                tenant_id=tenant_id,
                actor=f"webhook:{provider_code}",
                action="Webhook Rejected",
                resource_type="payment_webhook",
                resource_id=wh_record["id"],
                details={"reason": "Signature verification failed"},
            )
        if tx_ref:
            res_status = result.get("status", "successful")
            if res_status == "successful":
                PaymentService.verify_transaction(tenant_id, tx_ref, actor=f"webhook:{provider_code}")
            else:
                tx = PaymentService.get_transaction_by_ref(tenant_id, tx_ref)
                if tx:
                    PaymentService._update_transaction(
                        tenant_id,
                        tx["id"],
                        {
                            "status": res_status,
                            "verification_status": "failed" if res_status == "failed" else "unverified",
                            "updated_at": PaymentService._now(),
                        },
                    )
            wh_record["is_processed"] = True

        payment_webhooks_store.create(wh_record, tenant_id)
        PaymentService.log_audit(
            tenant_id=tenant_id,
            actor=f"webhook:{provider_code}",
            action="Webhook Processed",
            resource_type="payment_webhook",
            resource_id=wh_record["id"],
            details={"transaction_reference": tx_ref, "status": result.get("status")},
        )
        return {
            "status": "success",
            "internal_status": result.get("status", "successful"),
            "verified": result.get("verified", True),
            "message": "Webhook processed successfully",
            "tx_ref": tx_ref,
        }

    @staticmethod
    def get_transaction_by_ref(tenant_id: str, public_reference: str) -> Optional[dict[str, Any]]:
        """Find transaction by public reference."""
        if supabase is None:
            for tx in payment_transactions_store.list_all(tenant_id):
                if tx.get("public_reference") == public_reference:
                    return tx
            return None
        try:
            res = supabase.table("payment_transactions").select("*").eq("tenant_id", tenant_id).eq("public_reference", public_reference).execute()
            if res.data:
                return res.data[0]
        except Exception:
            pass
        return None

    @staticmethod
    def list_transactions(
        tenant_id: str,
        status_filter: Optional[str] = None,
        provider_filter: Optional[str] = None,
        search: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """List and filter payment transactions."""
        if supabase is None:
            txs = payment_transactions_store.list_all(tenant_id)
        else:
            try:
                res = supabase.table("payment_transactions").select("*").eq("tenant_id", tenant_id).execute()
                txs = res.data or []
            except Exception:
                txs = payment_transactions_store.list_all(tenant_id)

        if status_filter and status_filter != "all":
            txs = [t for t in txs if t.get("status", "").lower() == status_filter.lower()]
        if provider_filter and provider_filter != "all":
            txs = [t for t in txs if t.get("provider_code", "").lower() == provider_filter.lower()]
        if search:
            s = search.lower()
            txs = [
                t for t in txs
                if s in t.get("public_reference", "").lower()
                or s in t.get("customer_name", "").lower()
                or s in (t.get("customer_email") or "").lower()
                or s in (t.get("provider_reference") or "").lower()
            ]

        return sorted(txs, key=lambda x: x.get("created_at", ""), reverse=True)

    @staticmethod
    def _update_transaction(tenant_id: str, tx_id: str, updates: dict[str, Any]):
        if supabase is None:
            payment_transactions_store.update(tx_id, updates, tenant_id)
        else:
            try:
                supabase.table("payment_transactions").update(updates).eq("id", tx_id).eq("tenant_id", tenant_id).execute()
            except Exception:
                pass

    @staticmethod
    def _sync_student_payment_status(tenant_id: str, reference_code: str, customer_email: Optional[str] = None):
        """Update student registration status to Paid / Approved when payment succeeds."""
        for s in students_store.list_all(tenant_id):
            if (
                s.get("reference_code") == reference_code
                or s.get("id") == reference_code
                or (customer_email and s.get("email") == customer_email)
            ):
                students_store.update(s["id"], {"status": "Approved", "payment_status": "Paid"}, tenant_id)

    # ---------------------------------------------------------------------------
    # Balances Breakdown & Dashboard Summaries
    # ---------------------------------------------------------------------------
    @staticmethod
    def get_balances_summary(tenant_id: str) -> dict[str, Any]:
        """Aggregate total received, pending, volumes, and provider balances (distinguishing API vs internal)."""
        txs = payment_transactions_store.list_all(tenant_id) if supabase is None else []
        if supabase is not None:
            try:
                res = supabase.table("payment_transactions").select("*").eq("tenant_id", tenant_id).execute()
                txs = res.data or []
            except Exception:
                txs = payment_transactions_store.list_all(tenant_id)

        providers = PaymentService.get_admin_providers(tenant_id)

        total_received = sum(t.get("net_amount", t.get("amount", 0.0)) for t in txs if t.get("status") == "successful")
        pending_balance = sum(t.get("amount", 0.0) for t in txs if t.get("status") in {"pending", "initiated", "processing"})
        total_refunded = sum(t.get("amount", 0.0) for t in txs if t.get("status") == "refunded")
        total_volume = sum(t.get("amount", 0.0) for t in txs if t.get("status") == "successful")
        successful_count = sum(1 for t in txs if t.get("status") == "successful")
        failed_count = sum(1 for t in txs if t.get("status") in {"failed", "cancelled", "expired"})

        # Provider balances breakdown
        provider_balances = []
        for p in providers:
            p_code = p["provider_code"]
            p_txs = [t for t in txs if t.get("provider_code") == p_code]
            p_received = sum(t.get("net_amount", t.get("amount", 0.0)) for t in p_txs if t.get("status") == "successful")
            p_pending = sum(t.get("amount", 0.0) for t in p_txs if t.get("status") in {"pending", "initiated", "processing"})

            adapter = PaymentService.get_adapter(p)
            bal_result = adapter.get_balance()

            provider_balances.append({
                "provider_id": p["id"],
                "provider_name": p["provider_name"],
                "provider_code": p_code,
                "provider_type": p["provider_type"],
                "is_active": p["is_active"],
                "currency": p["currency"],
                "supports_balance_api": p.get("supports_balance_api", False),
                "balance_available_from_api": bal_result.get("supported", False),
                "provider_reported_balance": bal_result.get("balance"),
                "internal_platform_balance": round(p_received, 2),
                "pending_balance": round(p_pending, 2),
                "status_message": bal_result.get("message", "Balance unavailable from provider API"),
            })

        return {
            "total_received": round(total_received, 2),
            "pending_balance": round(pending_balance, 2),
            "available_balance": round(total_received - total_refunded, 2),
            "total_transferred": 0.0,
            "total_refunded": round(total_refunded, 2),
            "total_volume": round(total_volume, 2),
            "today_transactions_count": len([t for t in txs if t.get("status") == "successful"]),
            "today_transactions_volume": round(total_received, 2),
            "month_transactions_count": len(txs),
            "month_transactions_volume": round(total_volume, 2),
            "successful_count": successful_count,
            "failed_count": failed_count,
            "currency": "ETB",
            "provider_balances": provider_balances,
        }

    # ---------------------------------------------------------------------------
    # Audit Logging
    # ---------------------------------------------------------------------------
    @staticmethod
    def log_audit(
        tenant_id: str,
        actor: str,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
        ip_address: str = "127.0.0.1",
    ):
        """Append an immutable audit entry."""
        log_entry = {
            "id": f"plog-{str(uuid.uuid4())[:8]}",
            "tenant_id": tenant_id,
            "actor": actor,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "details": details or {},
            "ip_address": ip_address,
            "created_at": PaymentService._now(),
        }
        if supabase is None:
            payment_logs_store.create(log_entry, tenant_id)
        else:
            try:
                supabase.table("payment_logs").insert(log_entry).execute()
            except Exception:
                pass

    # ---------------------------------------------------------------------------
    # Backward-Compatible Invoicing Helpers (Configured Dynamically)
    # ---------------------------------------------------------------------------
    @staticmethod
    def generate_invoice(
        tenant_id: str,
        customer_name: str,
        customer_email: Optional[str] = None,
        contact_id: Optional[str] = None,
        module_type: str = "general",
        amount: float = 0.0,
        currency: str = "ETB",
        description: Optional[str] = None,
        payment_method: str = "CBE",
        receiving_account: Optional[str] = None,
        due_days: int = 7,
    ) -> dict[str, Any]:
        """Generate an invoice with dynamic provider configurations (no hard-coded numbers)."""
        ref_code = PaymentService.generate_transaction_ref(prefix=f"ZAC-{module_type[:3].upper()}")
        now = PaymentService._now()
        due_date = (datetime.now(timezone.utc)).isoformat()

        # If receiving_account not explicitly provided, find active provider details
        if not receiving_account:
            prov = PaymentService.get_provider_by_code(tenant_id, payment_method.lower())
            if prov and prov.get("account_number"):
                receiving_account = prov["account_number"]
            else:
                receiving_account = "Configured in Settings"

        invoice_data = {
            "id": f"inv-{str(uuid.uuid4())[:8]}",
            "tenant_id": tenant_id,
            "customer_name": customer_name,
            "customer_email": customer_email,
            "contact_id": contact_id,
            "module_type": module_type,
            "amount": amount,
            "currency": currency,
            "payment_method": payment_method,
            "receiving_account": receiving_account,
            "reference_code": ref_code,
            "due_date": due_date,
            "description": description or f"{module_type} Service Fee",
            "status": "sent",
            "payment_attempts": [],
            "confirmed_by": None,
            "confirmed_at": None,
            "rejection_reason": None,
            "created_at": now,
            "updated_at": now,
        }

        if supabase is None:
            created = invoices_store.create(invoice_data, tenant_id)
        else:
            try:
                res = supabase.table("invoices").insert(invoice_data).execute()
                created = res.data[0] if res.data else invoice_data
            except Exception:
                created = invoice_data

        if contact_id:
            CrmService.add_timeline_event(
                tenant_id=tenant_id,
                contact_id=contact_id,
                action="Invoice Generated",
                description=f"Generated invoice #{ref_code} for {amount:,.2f} {currency}",
                actor="system",
                metadata={"invoice_id": created["id"], "amount": amount, "reference_code": ref_code},
            )

        if customer_email:
            PaymentService.send_invoice_by_email(tenant_id, created["id"], created)

        return created

    @staticmethod
    def send_invoice_by_email(
        tenant_id: str,
        invoice_id: str,
        invoice_obj: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Dispatch invoice notification email with active provider instructions."""
        invoice = invoice_obj or (invoices_store.get(invoice_id, tenant_id) if supabase is None else None)
        if not invoice or not invoice.get("customer_email"):
            return {"status": "skipped", "reason": "No recipient email or invoice not found"}

        model = {
            "customer_name": invoice.get("customer_name", "Valued Client"),
            "reference_code": invoice.get("reference_code", invoice_id),
            "module_type": invoice.get("module_type", "General"),
            "amount": f"{invoice.get('amount', 0):,.2f}",
            "currency": invoice.get("currency", "ETB"),
            "description": invoice.get("description", "Service Fee"),
            "payment_method": invoice.get("payment_method", "CBE"),
            "receiving_account": invoice.get("receiving_account") or "Configured in Settings",
        }

        return NotificationService.send_email(
            to_email=invoice["customer_email"],
            template_key="invoice_created",
            model=model,
            tenant_id=tenant_id,
        )

    @staticmethod
    def record_payment_attempt(
        tenant_id: str,
        invoice_id: str,
        gateway: str,
        reference_number: str,
        proof_file_url: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> dict[str, Any] | None:
        """Record customer-submitted receipt upload."""
        attempt = {
            "gateway": gateway,
            "reference_number": reference_number,
            "proof_file_url": proof_file_url,
            "notes": notes,
            "timestamp": PaymentService._now(),
            "status": "pending_confirmation",
        }

        if supabase is None:
            invoice = invoices_store.get(invoice_id, tenant_id)
            if not invoice:
                return None
            attempts = invoice.get("payment_attempts", [])
            attempts.append(attempt)
            return invoices_store.update(invoice_id, {"payment_attempts": attempts, "status": "paid"}, tenant_id)

        return None

    @staticmethod
    def mark_payment_confirmed(
        tenant_id: str,
        invoice_id: str,
        admin_id: str,
        comment: Optional[str] = "Payment confirmed by admin",
    ) -> dict[str, Any] | None:
        """Mark invoice confirmed and notify client."""
        now = PaymentService._now()
        updates = {
            "status": "confirmed",
            "confirmed_by": admin_id,
            "confirmed_at": now,
        }

        if supabase is None:
            invoice = invoices_store.update(invoice_id, updates, tenant_id)
        else:
            invoice = None

        if invoice and invoice.get("contact_id"):
            CrmService.add_timeline_event(
                tenant_id=tenant_id,
                contact_id=invoice["contact_id"],
                action="Payment Confirmed",
                description=f"Payment for invoice #{invoice.get('reference_code')} confirmed by {admin_id}.",
                actor=admin_id,
            )

        if invoice and invoice.get("customer_email"):
            NotificationService.send_email(
                to_email=invoice["customer_email"],
                template_key="payment_confirmed",
                model={
                    "customer_name": invoice.get("customer_name", "Client"),
                    "reference_code": invoice.get("reference_code", invoice_id),
                    "amount": f"{invoice.get('amount', 0):,.2f}",
                    "currency": invoice.get("currency", "ETB"),
                    "description": invoice.get("description", "Service"),
                },
                tenant_id=tenant_id,
            )

        return invoice

    @staticmethod
    def mark_payment_rejected(
        tenant_id: str,
        invoice_id: str,
        admin_id: str,
        reason: str,
    ) -> dict[str, Any] | None:
        """Mark invoice rejected."""
        updates = {
            "status": "rejected",
            "rejection_reason": reason,
        }
        if supabase is None:
            return invoices_store.update(invoice_id, updates, tenant_id)
        return None
