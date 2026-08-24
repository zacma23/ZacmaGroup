"""Payments & Multi-Provider Platform API Router.

Provides:
- Public customer payment flows & active provider retrieval
- Online gateway checkouts & server-side verification
- Webhook ingestion with signature verification & replay protection
- Admin payment settings, provider management & balance overview
- Invoicing and manual receipt verification workflow
"""

from typing import Any, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status

from app.core.config import settings
from app.core.demo_data import invoices_store
from app.core.permissions import require_role
from app.core.tenancy import get_tenant_id
from app.models import (
    InvoiceCreate,
    InvoiceResponse,
    InvoiceUpdate,
    PaymentAttemptRequest,
    PaymentBalanceSummary,
    PaymentConfirmationRequest,
    PaymentInitRequest,
    PaymentInitResponse,
    PaymentProviderCreate,
    PaymentProviderPublic,
    PaymentProviderResponse,
    PaymentProviderUpdate,
    PaymentRejectionRequest,
    PaymentTransactionResponse,
    PaymentVerificationRequest,
    PaymentVerificationResponse,
)
from app.services.payment_service import PaymentService

router = APIRouter(prefix="/payments", tags=["payments"])


# ===========================================================================
# 1. Public Customer Payment Endpoints
# ===========================================================================

@router.get("/providers/active", response_model=list[PaymentProviderPublic])
def list_active_providers(tenant_id: str = Depends(get_tenant_id)):
    """Retrieve list of active payment providers for customer payment selection.
    Sensitive credentials are never included in this response.
    """
    return PaymentService.get_active_customer_providers(tenant_id)


@router.post("/transactions/initialize", response_model=PaymentInitResponse, status_code=status.HTTP_201_CREATED)
def initialize_payment_transaction(
    payload: PaymentInitRequest,
    tenant_id: str = Depends(get_tenant_id),
):
    """Customer initiates a payment transaction.
    Generates a unique ZACMA-2026-XXXXXXXX reference and returns hosted checkout link or instructions.
    """
    try:
        res = PaymentService.initialize_transaction(
            tenant_id=tenant_id,
            amount=payload.amount,
            provider_code=payload.provider_code,
            customer_name=payload.customer_name,
            customer_email=payload.customer_email,
            customer_phone=payload.customer_phone,
            currency=payload.currency,
            payment_purpose=payload.payment_purpose,
            description=payload.description,
            invoice_id=payload.invoice_id,
            return_url=payload.return_url,
            callback_url=payload.callback_url,
        )
        return res
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/transactions/{public_reference}/status", response_model=PaymentTransactionResponse)
def get_transaction_status(
    public_reference: str,
    tenant_id: str = Depends(get_tenant_id),
):
    """Query current status of a payment transaction."""
    tx = PaymentService.get_transaction_by_ref(tenant_id, public_reference)
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return tx


@router.post("/transactions/{public_reference}/verify", response_model=PaymentVerificationResponse)
def customer_verify_transaction(
    public_reference: str,
    tenant_id: str = Depends(get_tenant_id),
):
    """Client checkout callback verification endpoint."""
    res = PaymentService.verify_transaction(
        tenant_id=tenant_id,
        public_reference=public_reference,
        actor="customer_checkout",
    )
    return res


@router.post("/webhooks/{provider_code}")
async def handle_provider_webhook(
    provider_code: str,
    request: Request,
    tenant_id: str = settings.demo_tenant_id,
):
    """Receive and verify asynchronous webhook notifications from payment providers."""
    try:
        body = await request.json()
    except Exception:
        body = {}

    headers = dict(request.headers)
    res = PaymentService.handle_webhook(
        tenant_id=tenant_id,
        provider_code=provider_code,
        payload=body,
        headers=headers,
    )
    if res.get("status") == "error":
        raise HTTPException(status_code=400, detail=res.get("message", "Webhook verification failed"))
    return res


@router.get("/gateways")
def list_gateways(tenant_id: str = Depends(get_tenant_id)):
    """List active payment gateways and dynamic bank accounts (no hard-coded values)."""
    providers = PaymentService.get_active_customer_providers(tenant_id)
    online_gateways = [p["provider_name"] for p in providers if p["provider_type"] == "gateway"]
    bank_transfers = [p["provider_name"] for p in providers if p["provider_type"] in {"bank_transfer", "mobile_money"}]

    return {
        "active_providers": providers,
        "online_gateways": online_gateways,
        "bank_transfer_options": bank_transfers,
    }


# ===========================================================================
# 2. Admin Payment Platform & Balance Management
# ===========================================================================

@router.get("/admin/providers", response_model=list[PaymentProviderResponse])
def admin_list_providers(
    tenant_id: str = Depends(get_tenant_id),
    user: dict = Depends(require_role(["admin", "superadmin", "finance"])),
):
    """Admin view: List all configured providers with masked secret keys."""
    return PaymentService.get_admin_providers(tenant_id)


@router.post("/admin/providers", response_model=dict, status_code=status.HTTP_201_CREATED)
def admin_create_provider(
    payload: PaymentProviderCreate,
    tenant_id: str = Depends(get_tenant_id),
    user: dict = Depends(require_role(["admin", "superadmin", "finance"])),
):
    """Admin adds a new payment provider."""
    created = PaymentService.create_provider(
        tenant_id=tenant_id,
        payload=payload.model_dump(exclude_unset=True),
        actor=user.get("email", "admin"),
    )
    return created


@router.put("/admin/providers/{provider_id}", response_model=dict)
def admin_update_provider(
    provider_id: str,
    payload: PaymentProviderUpdate,
    tenant_id: str = Depends(get_tenant_id),
    user: dict = Depends(require_role(["admin", "superadmin", "finance"])),
):
    """Admin updates provider settings, credentials, or toggles active status."""
    updated = PaymentService.update_provider(
        tenant_id=tenant_id,
        provider_id=provider_id,
        payload=payload.model_dump(exclude_unset=True),
        actor=user.get("email", "admin"),
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Provider not found")
    return updated


@router.delete("/admin/providers/{provider_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_provider(
    provider_id: str,
    tenant_id: str = Depends(get_tenant_id),
    user: dict = Depends(require_role(["admin", "superadmin", "finance"])),
):
    """Admin deletes/deactivates a provider."""
    if not PaymentService.delete_provider(tenant_id, provider_id, actor=user.get("email", "admin")):
        raise HTTPException(status_code=404, detail="Provider not found")


@router.post("/admin/providers/{provider_id}/test")
def admin_test_provider_connection(
    provider_id: str,
    tenant_id: str = Depends(get_tenant_id),
    user: dict = Depends(require_role(["admin", "superadmin", "finance"])),
):
    """Test API connection or configuration for a payment provider."""
    return PaymentService.test_provider_connection(tenant_id, provider_id)


@router.get("/admin/balances", response_model=PaymentBalanceSummary)
def admin_get_balances(
    tenant_id: str = Depends(get_tenant_id),
    user: dict = Depends(require_role(["admin", "superadmin", "finance"])),
):
    """Retrieve detailed balance summary and provider-by-provider ledger breakdown."""
    return PaymentService.get_balances_summary(tenant_id)


@router.get("/admin/transactions", response_model=list[PaymentTransactionResponse])
def admin_list_transactions(
    status_filter: Optional[str] = None,
    provider_filter: Optional[str] = None,
    search: Optional[str] = None,
    tenant_id: str = Depends(get_tenant_id),
    user: dict = Depends(require_role(["admin", "superadmin", "finance"])),
):
    """Admin ledger of all payment transactions with filters and search."""
    return PaymentService.list_transactions(
        tenant_id=tenant_id,
        status_filter=status_filter,
        provider_filter=provider_filter,
        search=search,
    )


@router.post("/admin/transactions/{public_reference}/verify", response_model=PaymentVerificationResponse)
def admin_verify_transaction(
    public_reference: str,
    tenant_id: str = Depends(get_tenant_id),
    user: dict = Depends(require_role(["admin", "superadmin", "finance"])),
):
    """Trigger server-side verification for a transaction."""
    res = PaymentService.verify_transaction(
        tenant_id=tenant_id,
        public_reference=public_reference,
        actor=user.get("email", "admin"),
    )
    return res


# ===========================================================================
# 3. Invoice Management (Multi-Tenant Invoices)
# ===========================================================================

@router.get("/invoices", response_model=list[InvoiceResponse])
def list_invoices(
    module_type: str | None = None,
    status_filter: str | None = None,
    tenant_id: str = Depends(get_tenant_id),
):
    """List all invoices with optional filtering."""
    invoices = invoices_store.list_all(tenant_id)
    if module_type:
        invoices = [i for i in invoices if i.get("module_type", "").lower() == module_type.lower()]
    if status_filter:
        invoices = [i for i in invoices if i.get("status", "").lower() == status_filter.lower()]
    return sorted(invoices, key=lambda x: x.get("created_at", ""), reverse=True)


@router.post("/invoices", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
def create_invoice(
    payload: InvoiceCreate,
    tenant_id: str = Depends(get_tenant_id),
):
    """Generate a new invoice with dynamic provider configurations and email to client."""
    invoice = PaymentService.generate_invoice(
        tenant_id=tenant_id,
        customer_name=payload.customer_name,
        customer_email=payload.customer_email,
        contact_id=payload.contact_id,
        module_type=payload.module_type,
        amount=payload.amount,
        currency=payload.currency,
        description=payload.description,
        payment_method=payload.payment_method,
        receiving_account=payload.receiving_account,
    )
    return invoice


@router.get("/invoices/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(invoice_id: str, tenant_id: str = Depends(get_tenant_id)):
    """Get single invoice details."""
    inv = invoices_store.get(invoice_id, tenant_id)
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return inv


@router.put("/invoices/{invoice_id}", response_model=InvoiceResponse)
def update_invoice(
    invoice_id: str,
    payload: InvoiceUpdate,
    tenant_id: str = Depends(get_tenant_id),
):
    """Update invoice details."""
    updates = payload.model_dump(exclude_unset=True)
    if "status" in updates and hasattr(updates["status"], "value"):
        updates["status"] = updates["status"].value
    updated = invoices_store.update(invoice_id, updates, tenant_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return updated


@router.delete("/invoices/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_invoice(invoice_id: str, tenant_id: str = Depends(get_tenant_id)):
    """Delete an invoice."""
    if not invoices_store.delete(invoice_id, tenant_id):
        raise HTTPException(status_code=404, detail="Invoice not found")


@router.post("/invoices/{invoice_id}/attempt", response_model=InvoiceResponse)
def record_payment_attempt(
    invoice_id: str,
    payload: PaymentAttemptRequest,
    tenant_id: str = Depends(get_tenant_id),
):
    """Client records payment reference or bank transfer proof."""
    inv = PaymentService.record_payment_attempt(
        tenant_id=tenant_id,
        invoice_id=invoice_id,
        gateway=payload.gateway,
        reference_number=payload.reference_number,
        proof_file_url=payload.proof_file_url,
        notes=payload.notes,
    )
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return inv


@router.post("/invoices/{invoice_id}/confirm", response_model=InvoiceResponse)
def confirm_payment(
    invoice_id: str,
    payload: PaymentConfirmationRequest = PaymentConfirmationRequest(),
    tenant_id: str = Depends(get_tenant_id),
    user: dict = Depends(require_role(["admin", "superadmin", "finance"])),
):
    """Admin or Finance confirms payment receipt."""
    admin_id = user.get("email", "finance@zacma.com")
    inv = PaymentService.mark_payment_confirmed(
        tenant_id=tenant_id,
        invoice_id=invoice_id,
        admin_id=admin_id,
        comment=payload.comment,
    )
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return inv


@router.post("/invoices/{invoice_id}/reject", response_model=InvoiceResponse)
def reject_payment(
    invoice_id: str,
    payload: PaymentRejectionRequest,
    tenant_id: str = Depends(get_tenant_id),
    user: dict = Depends(require_role(["admin", "superadmin", "finance"])),
):
    """Admin or Finance rejects payment proof with reason."""
    admin_id = user.get("email", "finance@zacma.com")
    inv = PaymentService.mark_payment_rejected(
        tenant_id=tenant_id,
        invoice_id=invoice_id,
        admin_id=admin_id,
        reason=payload.reason,
    )
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return inv


@router.post("/invoices/{invoice_id}/resend")
def resend_invoice(
    invoice_id: str,
    tenant_id: str = Depends(get_tenant_id),
    user: dict = Depends(require_role(["admin", "superadmin", "finance"])),
):
    """Resend invoice email with payment instructions."""
    res = PaymentService.send_invoice_by_email(tenant_id, invoice_id)
    if res.get("status") == "skipped":
        raise HTTPException(status_code=400, detail=res.get("reason", "Could not resend invoice"))
    return {"status": "success", "message": f"Invoice email resent to {res.get('to')}"}
