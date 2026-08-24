"""Visa Assistant Module.

Handles visa applications, passport and supporting document uploads,
AI document completeness pre-checks, advance invoice generation,
requesting additional documentation, and approval workflows.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.demo_data import visa_applications_store
from app.core.permissions import require_role
from app.core.tenancy import get_tenant_id
from app.models import (
    RequestMoreInfoRequest,
    VisaApplicationCreate,
    VisaApplicationResponse,
    VisaApplicationUpdate,
)
from app.services.ai_assistant_service import AiAssistantService
from app.services.approval_service import ApprovalService
from app.services.crm_service import CrmService
from app.services.payment_service import PaymentService

router = APIRouter(prefix="/visa", tags=["visa"])


@router.get("/applications", response_model=list[VisaApplicationResponse])
def list_applications(
    destination_country: str | None = None,
    status_filter: str | None = None,
    tenant_id: str = Depends(get_tenant_id),
):
    """List all visa applications with optional filtering."""
    apps = visa_applications_store.list_all(tenant_id)
    if destination_country:
        apps = [a for a in apps if a.get("destination_country", "").lower() == destination_country.lower()]
    if status_filter:
        apps = [a for a in apps if a.get("status", "").lower() == status_filter.lower()]
    return apps


@router.post("/applications", response_model=VisaApplicationResponse, status_code=status.HTTP_201_CREATED)
def create_application(
    payload: VisaApplicationCreate,
    tenant_id: str = Depends(get_tenant_id),
):
    """Submit a new visa application.

    Automatically:
    1. Runs AI completeness pre-check on provided document URLs.
    2. Syncs/creates a CRM Contact with timeline history.
    3. Generates an advance payment invoice with dynamic receiving account details.
    4. Enters Pending approval workflow.
    """
    # 1. AI Document Pre-check
    provided_doc_names = []
    if payload.passport_upload_url:
        provided_doc_names.append("passport")
    for doc in payload.supporting_document_urls:
        provided_doc_names.append(doc.split("/")[-1])

    ai_check = AiAssistantService.precheck_documents(payload.visa_type, provided_doc_names)

    data = payload.model_dump()
    data["ai_document_check_summary"] = ai_check["summary"]
    data["status"] = "Pending"

    created = visa_applications_store.create(data, tenant_id)
    app_id = created["id"]

    # 2. CRM Contact Sync
    contact = CrmService.sync_contact(
        tenant_id=tenant_id,
        full_name=payload.full_name,
        email=payload.email,
        phone=payload.phone,
        address=payload.address,
        country=payload.country,
        source_module="Visa",
        status="Lead",
        tags=["Visa", payload.visa_type, payload.destination_country],
        initial_action=f"Applied for {payload.destination_country} ({payload.visa_type}) Visa",
        linked_entity_id=app_id,
    )
    contact_id = contact.get("id")

    # 3. Invoice Generation for advance fee
    invoice = PaymentService.generate_invoice(
        tenant_id=tenant_id,
        customer_name=payload.full_name,
        customer_email=payload.email,
        contact_id=contact_id,
        module_type="Visa",
        amount=payload.advance_amount or 5000.0,
        currency="ETB",
        description=f"Advance Visa Processing Fee: {payload.destination_country} ({payload.visa_type})",
        payment_method=payload.advance_payment_method,
    )

    # Link IDs
    visa_applications_store.update(
        app_id,
        {
            "linked_crm_contact_id": contact_id,
            "linked_invoice_id": invoice.get("id"),
        },
        tenant_id,
    )

    return visa_applications_store.get(app_id, tenant_id)


@router.get("/applications/{app_id}", response_model=VisaApplicationResponse)
def get_application(app_id: str, tenant_id: str = Depends(get_tenant_id)):
    """Get single visa application details."""
    app = visa_applications_store.get(app_id, tenant_id)
    if not app:
        raise HTTPException(status_code=404, detail="Visa application not found")
    return app


@router.put("/applications/{app_id}", response_model=VisaApplicationResponse)
def update_application(
    app_id: str,
    payload: VisaApplicationUpdate,
    tenant_id: str = Depends(get_tenant_id),
):
    """Update visa application fields."""
    updates = payload.model_dump(exclude_unset=True)
    updated = visa_applications_store.update(app_id, updates, tenant_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Visa application not found")
    return updated


@router.delete("/applications/{app_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_application(app_id: str, tenant_id: str = Depends(get_tenant_id)):
    """Delete a visa application."""
    if not visa_applications_store.delete(app_id, tenant_id):
        raise HTTPException(status_code=404, detail="Visa application not found")


@router.post("/applications/{app_id}/approve")
def approve_application(
    app_id: str,
    comment: str = "Visa application approved by admin",
    tenant_id: str = Depends(get_tenant_id),
    user: dict = Depends(require_role(["admin", "superadmin"])),
):
    """Admin approval of visa application."""
    admin_email = user.get("email", "admin@zacma.com")
    res = ApprovalService.approve(tenant_id, "visa", app_id, admin_email, comment)
    if not res:
        raise HTTPException(status_code=404, detail="Application not found")
    return {"status": "success", "message": "Visa application approved", "data": res}


@router.post("/applications/{app_id}/deny")
def deny_application(
    app_id: str,
    reason: str,
    tenant_id: str = Depends(get_tenant_id),
    user: dict = Depends(require_role(["admin", "superadmin"])),
):
    """Admin rejection of visa application."""
    admin_email = user.get("email", "admin@zacma.com")
    res = ApprovalService.deny(tenant_id, "visa", app_id, admin_email, reason)
    if not res:
        raise HTTPException(status_code=404, detail="Application not found")
    return {"status": "success", "message": "Visa application denied", "data": res}


@router.post("/applications/{app_id}/request-info")
def request_more_info(
    app_id: str,
    payload: RequestMoreInfoRequest,
    tenant_id: str = Depends(get_tenant_id),
    user: dict = Depends(require_role(["admin", "superadmin"])),
):
    """Request additional documents or information from applicant."""
    admin_email = user.get("email", "admin@zacma.com")
    res = ApprovalService.request_more_info(
        tenant_id, "visa", app_id, admin_email, payload.message, payload.requested_documents
    )
    if not res:
        raise HTTPException(status_code=404, detail="Application not found")
    return {"status": "success", "message": "Document request dispatched", "data": res}
