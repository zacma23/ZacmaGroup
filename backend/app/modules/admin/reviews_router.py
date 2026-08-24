"""Admin Review & Approval Workflow Router.

Allows authorized administrators and staff to review client intake requests,
verify payment receipts, trigger/inspect AI service generation, edit outputs,
and issue official approvals and service delivery.
"""

from datetime import datetime, timezone
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.auth import get_current_user, log_audit_event
from app.core.config import settings
from app.core.demo_data import (
    invoices_store,
    module_submissions_store,
    software_projects_store,
    students_store,
    support_tickets_store,
    travel_requests_store,
    visa_applications_store,
)
from app.core.permissions import require_role
from app.models import (
    AdminAiEditRequest,
    AdminPaymentVerificationRequest,
    AdminServiceApprovalRequest,
)
from app.services.ai_service_generator import AiServiceGenerator

router = APIRouter(prefix="/admin/reviews", tags=["admin_reviews"])


def _find_request_by_ref(ref_code: str, tenant_id: str):
    """Find request record and its corresponding store."""
    stores = [
        ("Software Development", software_projects_store),
        ("Visa Assistant", visa_applications_store),
        ("Training Institute", students_store),
        ("Travel Agent", travel_requests_store),
        ("Custom Module", module_submissions_store),
    ]

    for stype, store in stores:
        for item in store.list_all(tenant_id):
            item_ref = item.get("reference_code") or item.get("id")
            if item_ref.lower() == ref_code.strip().lower():
                return stype, store, item

    return None, None, None


# ---------------------------------------------------------------------------
# GET /admin/reviews/queue
# ---------------------------------------------------------------------------

@router.get("/queue")
def get_review_queue(
    status_filter: str | None = None,
    service_filter: str | None = None,
    user: dict = Depends(require_role(["admin", "staff", "finance"])),
):
    """List all client requests in queue with inspection data and receipts."""
    tid = user.get("tenant_id", settings.demo_tenant_id)

    visas = visa_applications_store.list_all(tid)
    students = students_store.list_all(tid)
    travels = travel_requests_store.list_all(tid)
    software_projs = software_projects_store.list_all(tid)
    customs = module_submissions_store.list_all(tid)

    queue = []

    for p in software_projs:
        ref = p.get("reference_code", f"ZAC-DEV-{abs(hash(p['id'])) % 9000 + 1000}")
        queue.append({
            "id": p["id"],
            "reference_code": ref,
            "service_type": "Software Development",
            "title": p.get("project_name", "Software Solution"),
            "client_name": p.get("client_name", "Client"),
            "client_email": p.get("email", ""),
            "client_phone": p.get("phone", ""),
            "status": p.get("status", "Pending"),
            "payment_status": p.get("payment_status", "Pending"),
            "amount": p.get("advance_amount", 15000.0),
            "currency": p.get("currency", "ETB"),
            "payment_receipt": p.get("payment_receipt"),
            "has_receipt": bool(p.get("payment_receipt")),
            "supporting_document_urls": p.get("supporting_document_urls", []),
            "ai_generated_result": p.get("ai_generated_result"),
            "admin_response": p.get("admin_response"),
            "created_at": p.get("created_at", ""),
        })

    for v in visas:
        ref = v.get("reference_code", v["id"])
        queue.append({
            "id": v["id"],
            "reference_code": ref,
            "service_type": "Visa Assistant",
            "title": f"{v.get('destination_country', 'Global')} {v.get('visa_type', 'Tourist')} Visa",
            "client_name": v.get("full_name", "Client"),
            "client_email": v.get("email", ""),
            "client_phone": v.get("phone", ""),
            "status": v.get("status", "Pending"),
            "payment_status": v.get("payment_status", "Pending"),
            "amount": v.get("advance_amount", 5000.0),
            "currency": v.get("currency", "ETB"),
            "payment_receipt": v.get("payment_receipt"),
            "has_receipt": bool(v.get("payment_receipt")),
            "passport_upload_url": v.get("passport_upload_url"),
            "supporting_document_urls": v.get("supporting_document_urls", []),
            "ai_generated_result": v.get("ai_generated_result"),
            "admin_response": v.get("admin_response"),
            "created_at": v.get("created_at", ""),
        })

    for s in students:
        ref = s.get("reference_code", f"ZAC-STU-{abs(hash(s['id'])) % 9000 + 1000}")
        queue.append({
            "id": s["id"],
            "reference_code": ref,
            "service_type": "Training Institute",
            "title": f"Course: {s.get('course', 'Tech Training')}",
            "client_name": s.get("full_name", "Student"),
            "client_email": s.get("email", ""),
            "client_phone": s.get("phone", ""),
            "status": s.get("status", "Pending"),
            "payment_status": s.get("payment_status", "Pending"),
            "amount": s.get("tuition_amount", 4500.0),
            "currency": s.get("currency", "ETB"),
            "payment_receipt": s.get("payment_receipt"),
            "has_receipt": bool(s.get("payment_receipt")),
            "ai_generated_result": s.get("ai_generated_result"),
            "admin_response": s.get("admin_response"),
            "created_at": s.get("created_at", ""),
        })

    for t in travels:
        ref = t.get("reference_code", f"ZAC-TRV-{abs(hash(t['id'])) % 9000 + 1000}")
        queue.append({
            "id": t["id"],
            "reference_code": ref,
            "service_type": "Travel Agent",
            "title": f"Travel to {t.get('destination_country', 'Destination')}",
            "client_name": t.get("full_name", "Traveler"),
            "client_email": t.get("email", ""),
            "client_phone": t.get("phone", ""),
            "status": t.get("status", "Pending"),
            "payment_status": t.get("payment_status", "Pending"),
            "amount": t.get("advance_amount", 8000.0),
            "currency": t.get("currency", "ETB"),
            "payment_receipt": t.get("payment_receipt"),
            "has_receipt": bool(t.get("payment_receipt")),
            "ai_generated_result": t.get("ai_generated_result"),
            "admin_response": t.get("admin_response"),
            "created_at": t.get("created_at", ""),
        })

    for c in customs:
        ref = c.get("reference_code", f"ZAC-MOD-{abs(hash(c['id'])) % 9000 + 1000}")
        queue.append({
            "id": c["id"],
            "reference_code": ref,
            "service_type": "Custom Module",
            "title": c.get("module_slug", "Custom").title(),
            "client_name": c.get("customer_name", "Client"),
            "client_email": c.get("customer_email", ""),
            "client_phone": c.get("customer_phone", ""),
            "status": c.get("status", "Pending"),
            "payment_status": c.get("payment_status", "Pending"),
            "amount": 10000.0,
            "currency": "ETB",
            "payment_receipt": c.get("payment_receipt"),
            "has_receipt": bool(c.get("payment_receipt")),
            "ai_generated_result": c.get("ai_generated_result"),
            "admin_response": c.get("admin_response"),
            "created_at": c.get("created_at", ""),
        })

    # Apply filters
    if status_filter:
        queue = [q for q in queue if q["status"].lower() == status_filter.lower()]
    if service_filter:
        queue = [q for q in queue if service_filter.lower() in q["service_type"].lower()]

    queue.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return queue


# ---------------------------------------------------------------------------
# POST /admin/reviews/{ref_code}/verify-payment
# ---------------------------------------------------------------------------

@router.post("/{ref_code}/verify-payment")
def verify_payment(
    ref_code: str,
    payload: AdminPaymentVerificationRequest,
    user: dict = Depends(require_role(["admin", "staff", "finance"])),
):
    """Admin confirms or rejects an uploaded payment receipt."""
    tid = user.get("tenant_id", settings.demo_tenant_id)
    admin_email = user.get("email", "admin@zacma.com")

    stype, store, item = _find_request_by_ref(ref_code, tid)
    if not item:
        raise HTTPException(status_code=404, detail="Request reference not found")

    new_status = "PaymentApproved" if payload.verified else "PaymentRejected"
    payment_status = "Paid" if payload.verified else "Rejected"

    receipt = item.get("payment_receipt") or {}
    receipt["status"] = "Verified" if payload.verified else "Rejected"
    receipt["verified_by"] = admin_email
    receipt["verified_at"] = datetime.now(timezone.utc).isoformat()
    receipt["comment"] = payload.comment
    receipt["rejection_reason"] = payload.rejection_reason

    # If verified, trigger AI output automatically
    ai_output = item.get("ai_generated_result")
    if payload.verified and not ai_output:
        ai_output = AiServiceGenerator.generate_for_service(stype, item)

    store.update(
        item["id"],
        {
            "status": new_status,
            "payment_status": payment_status,
            "payment_receipt": receipt,
            "ai_generated_result": ai_output,
        },
        tid,
    )

    # Update associated invoice
    invoices = [i for i in invoices_store.list_all(tid) if i.get("reference_code", "").lower() == ref_code.lower()]
    for inv in invoices:
        invoices_store.update(
            inv["id"],
            {
                "status": "confirmed" if payload.verified else "rejected",
                "confirmed_by": admin_email,
                "confirmed_at": datetime.now(timezone.utc).isoformat(),
            },
            tid,
        )

    # Automatic Service Activation & Automation Job Pipeline
    if payload.verified:
        try:
            from app.services.automation_service import AutomationService
            job = AutomationService.create_job(
                tenant_id=tid,
                job_type="admin_service_activation",
                entity_type=stype.lower().replace(" ", "_"),
                entity_id=ref_code,
                payload={
                    "reference_code": ref_code,
                    "service_type": stype,
                    "verified_by": admin_email,
                    "amount": item.get("tuition_amount") or item.get("advance_amount") or 5000.0,
                    "currency": item.get("currency") or "ETB",
                },
            )
            AutomationService.execute_job(tid, job["id"])
        except Exception as auto_err:
            pass

    log_audit_event(
        tid,
        "PAYMENT_VERIFIED" if payload.verified else "PAYMENT_REJECTED",
        f"requests/{ref_code}",
        f"Admin {admin_email} {'confirmed' if payload.verified else 'rejected'} payment for Ref {ref_code}",
        user_email=admin_email,
    )

    return {
        "status": "success",
        "message": f"Payment receipt for Ref {ref_code} {'approved' if payload.verified else 'rejected'}.",
        "reference_code": ref_code,
        "current_status": new_status,
        "ai_output_ready": bool(ai_output),
    }


# ---------------------------------------------------------------------------
# POST /admin/reviews/{ref_code}/trigger-ai
# ---------------------------------------------------------------------------

@router.post("/{ref_code}/trigger-ai")
def trigger_ai_service_generation(
    ref_code: str,
    user: dict = Depends(require_role(["admin", "staff"])),
):
    """Trigger on-demand AI deliverable generation for a request."""
    tid = user.get("tenant_id", settings.demo_tenant_id)
    admin_email = user.get("email", "admin@zacma.com")

    stype, store, item = _find_request_by_ref(ref_code, tid)
    if not item:
        raise HTTPException(status_code=404, detail="Request not found")

    ai_output = AiServiceGenerator.generate_for_service(stype, item)

    store.update(
        item["id"],
        {
            "ai_generated_result": ai_output,
            "status": "AiResultGenerated",
        },
        tid,
    )

    log_audit_event(
        tid,
        "AI_SERVICE_GENERATED",
        f"requests/{ref_code}",
        f"AI service output generated for {stype} (Ref: {ref_code})",
        user_email=admin_email,
    )

    return {
        "status": "success",
        "reference_code": ref_code,
        "ai_generated_result": ai_output,
    }


# ---------------------------------------------------------------------------
# POST /admin/reviews/{ref_code}/edit-ai-result
# ---------------------------------------------------------------------------

@router.post("/{ref_code}/edit-ai-result")
def edit_ai_result(
    ref_code: str,
    payload: AdminAiEditRequest,
    user: dict = Depends(require_role(["admin", "staff"])),
):
    """Admin modifies or refines the AI deliverable prior to client release."""
    tid = user.get("tenant_id", settings.demo_tenant_id)
    stype, store, item = _find_request_by_ref(ref_code, tid)
    if not item:
        raise HTTPException(status_code=404, detail="Request not found")

    store.update(
        item["id"],
        {
            "ai_generated_result": payload.ai_generated_result,
            "admin_notes": payload.admin_notes,
        },
        tid,
    )

    return {
        "status": "success",
        "message": "AI deliverable updated successfully.",
        "ai_generated_result": payload.ai_generated_result,
    }


# ---------------------------------------------------------------------------
# POST /admin/reviews/{ref_code}/approve-service
# ---------------------------------------------------------------------------

@router.post("/{ref_code}/approve-service")
def approve_and_deliver_service(
    ref_code: str,
    payload: AdminServiceApprovalRequest,
    user: dict = Depends(require_role(["admin", "staff"])),
):
    """Admin issues final approval and delivers the service output to the client."""
    tid = user.get("tenant_id", settings.demo_tenant_id)
    admin_email = user.get("email", "admin@zacma.com")

    stype, store, item = _find_request_by_ref(ref_code, tid)
    if not item:
        raise HTTPException(status_code=404, detail="Request not found")

    admin_response = {
        "status": payload.status,
        "message": payload.admin_response_message,
        "decided_by": admin_email,
        "decided_at": datetime.now(timezone.utc).isoformat(),
    }

    updates: dict[str, Any] = {
        "status": payload.status,
        "admin_response": admin_response,
    }

    if payload.deliverable_payload:
        updates["ai_generated_result"] = payload.deliverable_payload

    store.update(item["id"], updates, tid)

    log_audit_event(
        tid,
        "SERVICE_APPROVED",
        f"requests/{ref_code}",
        f"Admin {admin_email} approved and delivered service for Ref {ref_code} ({stype})",
        user_email=admin_email,
    )

    return {
        "status": "success",
        "message": f"Service request {ref_code} has been successfully approved and marked as {payload.status}.",
        "reference_code": ref_code,
        "current_status": payload.status,
        "admin_response": admin_response,
    }
