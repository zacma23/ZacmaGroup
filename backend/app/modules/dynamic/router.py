"""Dynamic Module System Router (Section 6).

Enables SuperAdmins to register brand-new business lines (e.g. Real Estate,
Legal Consultancy) with dynamic form builder field definitions.
Every dynamic module automatically inherits CRM Contact sync, Payment/Invoicing,
and Approval workflows without writing new backend code.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.demo_data import business_modules_store, module_submissions_store
from app.core.permissions import require_role
from app.core.tenancy import get_tenant_id
from app.models import (
    BusinessModule,
    BusinessModuleCreate,
    ModuleSubmission,
    ModuleSubmissionCreate,
    ModuleSubmissionUpdate,
)
from app.services.approval_service import ApprovalService
from app.services.crm_service import CrmService
from app.services.payment_service import PaymentService

router = APIRouter(tags=["dynamic_modules"])


# ---------------------------------------------------------------------------
# Module Registry (SuperAdmin)
# ---------------------------------------------------------------------------

@router.get("/admin/modules", response_model=list[BusinessModule])
def list_business_modules(
    tenant_id: str = Depends(get_tenant_id),
    _user: dict = Depends(require_role(["admin", "superadmin"])),
):
    """List all registered business modules."""
    return business_modules_store.list_all(tenant_id)


@router.post("/admin/modules", response_model=BusinessModule, status_code=status.HTTP_201_CREATED)
def create_business_module(
    payload: BusinessModuleCreate,
    tenant_id: str = Depends(get_tenant_id),
    _user: dict = Depends(require_role(["superadmin", "admin"])),
):
    """Register a new business module with dynamic form field definitions."""
    existing = business_modules_store.list_all(tenant_id)
    if any(m.get("key") == payload.key for m in existing):
        raise HTTPException(status_code=409, detail=f"Module key '{payload.key}' already exists")

    data = payload.model_dump()
    data["is_active"] = True
    return business_modules_store.create(data, tenant_id)


@router.get("/admin/modules/{module_id}", response_model=BusinessModule)
def get_business_module(
    module_id: str,
    tenant_id: str = Depends(get_tenant_id),
    _user: dict = Depends(require_role(["admin", "superadmin"])),
):
    """Get single business module definition."""
    mod = business_modules_store.get(module_id, tenant_id)
    if not mod:
        raise HTTPException(status_code=404, detail="Business module not found")
    return mod


@router.delete("/admin/modules/{module_id}")
def delete_business_module(
    module_id: str,
    tenant_id: str = Depends(get_tenant_id),
    _user: dict = Depends(require_role(["superadmin"])),
):
    """Deactivate or remove a business module."""
    if not business_modules_store.delete(module_id, tenant_id):
        raise HTTPException(status_code=404, detail="Business module not found")
    return {"status": "success", "detail": "Business module deleted"}


# ---------------------------------------------------------------------------
# Dynamic Module Submissions (Intake + Approval + CRM)
# ---------------------------------------------------------------------------

@router.get("/submissions/{module_key}", response_model=list[ModuleSubmission])
def list_submissions(
    module_key: str,
    status_filter: str | None = None,
    tenant_id: str = Depends(get_tenant_id),
):
    """List all submissions for a given dynamic module key."""
    all_subs = module_submissions_store.list_all(tenant_id)
    filtered = [s for s in all_subs if s.get("module_key", "").lower() == module_key.lower()]
    if status_filter:
        filtered = [s for s in filtered if s.get("status", "").lower() == status_filter.lower()]
    return filtered


@router.post("/submissions/{module_key}", response_model=ModuleSubmission, status_code=status.HTTP_201_CREATED)
def submit_to_dynamic_module(
    module_key: str,
    payload: ModuleSubmissionCreate,
    tenant_id: str = Depends(get_tenant_id),
):
    """Submit dynamic form intake for a registered business line.

    Automatically:
    1. Validates module exists and is active.
    2. Syncs/creates a CRM Contact.
    3. Auto-generates invoice if module has requires_payment=True.
    4. Places submission in Pending approval workflow.
    """
    modules = business_modules_store.list_all(tenant_id)
    target_mod = next((m for m in modules if m.get("key") == module_key), None)
    if not target_mod:
        raise HTTPException(status_code=404, detail=f"Business module '{module_key}' is not registered")

    data = payload.model_dump()
    data["module_id"] = target_mod["id"]
    data["module_key"] = module_key
    data["status"] = "Pending"

    created_sub = module_submissions_store.create(data, tenant_id)
    sub_id = created_sub["id"]

    # 1. CRM Contact Sync
    contact = CrmService.sync_contact(
        tenant_id=tenant_id,
        full_name=payload.full_name,
        email=payload.email,
        phone=payload.phone,
        source_module=target_mod["name"],
        status="Lead",
        tags=["Dynamic", target_mod["name"]],
        initial_action=f"Submitted to {target_mod['name']}",
        linked_entity_id=sub_id,
    )
    contact_id = contact.get("id")

    # 2. Optional Invoice Generation
    invoice_id = None
    if target_mod.get("requires_payment") and target_mod.get("base_amount", 0) > 0:
        invoice = PaymentService.generate_invoice(
            tenant_id=tenant_id,
            customer_name=payload.full_name,
            customer_email=payload.email,
            contact_id=contact_id,
            module_type=target_mod["name"],
            amount=target_mod["base_amount"],
            currency="ETB",
            description=f"{target_mod['name']} Service Fee",
            payment_method=payload.payment_method or "TeleBirr",
        )
        invoice_id = invoice.get("id")

    module_submissions_store.update(
        sub_id,
        {
            "linked_crm_contact_id": contact_id,
            "linked_invoice_id": invoice_id,
        },
        tenant_id,
    )

    return module_submissions_store.get(sub_id, tenant_id)


@router.get("/submissions/{module_key}/{sub_id}", response_model=ModuleSubmission)
def get_submission(
    module_key: str,
    sub_id: str,
    tenant_id: str = Depends(get_tenant_id),
):
    """Get single dynamic module submission."""
    sub = module_submissions_store.get(sub_id, tenant_id)
    if not sub or sub.get("module_key") != module_key:
        raise HTTPException(status_code=404, detail="Submission not found")
    return sub


@router.post("/submissions/{module_key}/{sub_id}/approve")
def approve_submission(
    module_key: str,
    sub_id: str,
    comment: str = "Submission approved by admin",
    tenant_id: str = Depends(get_tenant_id),
    user: dict = Depends(require_role(["admin", "superadmin"])),
):
    """Admin approval of dynamic module submission."""
    admin_email = user.get("email", "admin@zacma.com")
    res = ApprovalService.approve(tenant_id, "submission", sub_id, admin_email, comment)
    if not res:
        raise HTTPException(status_code=404, detail="Submission not found")
    return {"status": "success", "message": "Submission approved", "data": res}


@router.post("/submissions/{module_key}/{sub_id}/deny")
def deny_submission(
    module_key: str,
    sub_id: str,
    reason: str,
    tenant_id: str = Depends(get_tenant_id),
    user: dict = Depends(require_role(["admin", "superadmin"])),
):
    """Admin rejection of dynamic module submission."""
    admin_email = user.get("email", "admin@zacma.com")
    res = ApprovalService.deny(tenant_id, "submission", sub_id, admin_email, reason)
    if not res:
        raise HTTPException(status_code=404, detail="Submission not found")
    return {"status": "success", "message": "Submission denied", "data": res}
