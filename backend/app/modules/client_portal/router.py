"""Client Portal Module.

Provides authenticated clients with access to their own service applications,
document uploads, payment receipt submissions, AI deliverables, admin feedback,
and notifications.
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
from app.models import PaymentReceiptUploadRequest

router = APIRouter(prefix="/client", tags=["client_portal"])


def _get_client_email(user: dict[str, Any]) -> str:
    email = user.get("email", "").lower().strip()
    if not email:
        raise HTTPException(status_code=401, detail="Authentication required")
    return email


# ---------------------------------------------------------------------------
# GET /client/dashboard
# ---------------------------------------------------------------------------

@router.get("/dashboard")
def get_client_dashboard(user: dict = Depends(get_current_user)):
    """Return aggregated dashboard stats, active requests, and notifications."""
    email = _get_client_email(user)
    tid = user.get("tenant_id", settings.demo_tenant_id)

    # 1. Fetch requests across all stores for this client
    visas = [v for v in visa_applications_store.list_all(tid) if v.get("email", "").lower() == email]
    students = [s for s in students_store.list_all(tid) if s.get("email", "").lower() == email]
    travels = [t for t in travel_requests_store.list_all(tid) if t.get("email", "").lower() == email]
    software_projs = [p for p in software_projects_store.list_all(tid) if p.get("email", "").lower() == email]
    customs = [m for m in module_submissions_store.list_all(tid) if m.get("customer_email", "").lower() == email]
    invoices = [i for i in invoices_store.list_all(tid) if i.get("customer_email", "").lower() == email]

    all_requests = []
    for p in software_projs:
        all_requests.append({
            "id": p["id"],
            "reference_code": p.get("reference_code", f"ZAC-DEV-{abs(hash(p['id'])) % 9000 + 1000}"),
            "service_type": "Software Development",
            "title": p.get("project_name", "Software Solution"),
            "status": p.get("status", "Pending"),
            "payment_status": p.get("payment_status", "Pending"),
            "created_at": p.get("created_at", ""),
            "has_receipt": bool(p.get("payment_receipt")),
            "has_ai_output": bool(p.get("ai_generated_result")),
            "admin_response": p.get("admin_response"),
        })

    for v in visas:
        all_requests.append({
            "id": v["id"],
            "reference_code": v["reference_code"],
            "service_type": "Visa Assistant",
            "title": f"{v.get('destination_country', 'Global')} {v.get('visa_type', 'Tourist')} Visa",
            "status": v.get("status", "Pending"),
            "payment_status": v.get("payment_status", "Pending"),
            "created_at": v.get("created_at", ""),
            "has_receipt": bool(v.get("payment_receipt")),
            "has_ai_output": bool(v.get("ai_generated_result")),
            "admin_response": v.get("admin_response"),
        })

    for s in students:
        course_name = s.get("course", "Maintenance")
        specialty = s.get("specialty") or s.get("maintenance_sub_type")
        title = f"Course: {course_name}"
        if specialty:
            title += f" — {specialty}"
        all_requests.append({
            "id": s["id"],
            "reference_code": s.get("reference_code", f"ZAC-STU-{abs(hash(s['id'])) % 9000 + 1000}"),
            "service_type": "Training Institute",
            "title": title,
            "course": course_name,
            "specialty": specialty,
            "schedule": s.get("schedule"),
            "time_slot": s.get("time_slot") or s.get("time"),
            "status": s.get("status", "Pending"),
            "payment_status": s.get("payment_status", "Pending"),
            "created_at": s.get("created_at", ""),
            "has_receipt": bool(s.get("payment_receipt")),
            "has_ai_output": bool(s.get("ai_generated_result")),
            "admin_response": s.get("admin_response"),
        })

    for t in travels:
        all_requests.append({
            "id": t["id"],
            "reference_code": t.get("reference_code", f"ZAC-TRV-{abs(hash(t['id'])) % 9000 + 1000}"),
            "service_type": "Travel Agent",
            "title": f"Travel to {t.get('destination_country', 'Destination')}",
            "status": t.get("status", "Pending"),
            "payment_status": t.get("payment_status", "Pending"),
            "created_at": t.get("created_at", ""),
            "has_receipt": bool(t.get("payment_receipt")),
            "has_ai_output": bool(t.get("ai_generated_result")),
            "admin_response": t.get("admin_response"),
        })

    for c in customs:
        all_requests.append({
            "id": c["id"],
            "reference_code": c.get("reference_code", f"ZAC-MOD-{abs(hash(c['id'])) % 9000 + 1000}"),
            "service_type": "Custom Service",
            "title": c.get("module_slug", "Custom Request").title(),
            "status": c.get("status", "Pending"),
            "payment_status": c.get("payment_status", "Pending"),
            "created_at": c.get("created_at", ""),
            "has_receipt": bool(c.get("payment_receipt")),
            "has_ai_output": bool(c.get("ai_generated_result")),
            "admin_response": c.get("admin_response"),
        })

    # Sort descending
    all_requests.sort(key=lambda r: r.get("created_at", ""), reverse=True)

    # 2. Compute summary counts
    active_count = sum(1 for r in all_requests if r["status"] not in {"Completed", "Cancelled", "Rejected"})
    receipts_under_review = sum(1 for r in all_requests if r["status"] == "PaymentUnderReview" or (r["has_receipt"] and r["payment_status"] != "Paid"))
    deliverables_ready = sum(1 for r in all_requests if r["has_ai_output"])
    pending_payments = sum(1 for i in invoices if i.get("status") in {"sent", "draft", "overdue"})

    # 3. Dynamic notifications
    notifications = [
        {
            "id": "notif-payments",
            "title": "Active Payment Methods",
            "message": "Instant checkout available via Chapa, or bank transfer (CBE, TeleBirr, Awash). Always upload your transfer receipt.",
            "type": "info",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "read": False,
        }
    ]

    for req in all_requests:
        if req["status"] == "PaymentApproved":
            notifications.append({
                "id": f"notif-pa-{req['reference_code']}",
                "title": f"Payment Approved: {req['reference_code']}",
                "message": f"Your payment receipt for {req['title']} was verified. AI processing is now active.",
                "type": "success",
                "created_at": req["created_at"],
                "read": False,
            })
        elif req["status"] in {"Approved", "ServiceDelivered"}:
            notifications.append({
                "id": f"notif-app-{req['reference_code']}",
                "title": f"Service Approved: {req['reference_code']}",
                "message": f"Your {req['title']} has been approved and official deliverables are ready to download.",
                "type": "success",
                "created_at": req["created_at"],
                "read": False,
            })

    return {
        "client_email": email,
        "client_name": user.get("full_name", "Client"),
        "role": user.get("role", "client"),
        "summary": {
            "total_requests": len(all_requests),
            "active_requests": active_count,
            "receipts_under_review": receipts_under_review,
            "deliverables_ready": deliverables_ready,
            "pending_invoices": pending_payments,
        },
        "recent_requests": all_requests,
        "invoices": invoices,
        "notifications": notifications,
    }


# ---------------------------------------------------------------------------
# GET /client/requests
# ---------------------------------------------------------------------------

@router.get("/requests")
def list_client_requests(user: dict = Depends(get_current_user)):
    """List all requests submitted by the logged-in client."""
    dash = get_client_dashboard(user)
    return dash["recent_requests"]


# ---------------------------------------------------------------------------
# GET /client/requests/{ref_code}
# ---------------------------------------------------------------------------

@router.get("/requests/{ref_code}")
def get_client_request_detail(ref_code: str, user: dict = Depends(get_current_user)):
    """Get complete details, documents, receipts, and AI outputs for a specific request."""
    email = _get_client_email(user)
    tid = user.get("tenant_id", settings.demo_tenant_id)
    ref = ref_code.strip()

    # Search in stores
    stores = [
        ("Software Development", software_projects_store),
        ("Visa Assistant", visa_applications_store),
        ("Training Institute", students_store),
        ("Travel Agent", travel_requests_store),
        ("Custom Module", module_submissions_store),
    ]

    matched_record = None
    service_type = "General"

    for stype, store in stores:
        for item in store.list_all(tid):
            item_ref = item.get("reference_code") or item.get("id")
            if item_ref.lower() == ref.lower():
                # Enforce ownership: user must own this request or be an admin/staff
                item_email = item.get("email") or item.get("customer_email") or ""
                if user.get("role") not in {"admin", "staff"} and item_email.lower() != email:
                    raise HTTPException(status_code=403, detail="Unauthorized access to this request")
                matched_record = item
                service_type = stype
                break
        if matched_record:
            break

    if not matched_record:
        raise HTTPException(status_code=404, detail="Request not found")

    # Find associated invoice
    invoices = [
        i for i in invoices_store.list_all(tid)
        if i.get("reference_code", "").lower() == ref.lower()
        or (matched_record.get("full_name") and i.get("customer_name") == matched_record.get("full_name"))
    ]
    invoice = invoices[0] if invoices else None

    return {
        "reference_code": ref,
        "service_type": service_type,
        "data": matched_record,
        "invoice": invoice,
        "status": matched_record.get("status", "Pending"),
        "payment_status": matched_record.get("payment_status", "Pending"),
        "payment_receipt": matched_record.get("payment_receipt"),
        "ai_generated_result": matched_record.get("ai_generated_result"),
        "admin_response": matched_record.get("admin_response"),
    }


# ---------------------------------------------------------------------------
# POST /client/requests/{ref_code}/receipt
# ---------------------------------------------------------------------------

@router.post("/requests/{ref_code}/receipt")
def upload_payment_receipt(
    ref_code: str,
    payload: PaymentReceiptUploadRequest,
    user: dict = Depends(get_current_user),
):
    """Client submits an official payment receipt for an existing request."""
    email = _get_client_email(user)
    tid = user.get("tenant_id", settings.demo_tenant_id)
    ref = ref_code.strip()

    # Find the target request
    stores = [
        ("Software Development", software_projects_store),
        ("Visa Assistant", visa_applications_store),
        ("Training Institute", students_store),
        ("Travel Agent", travel_requests_store),
        ("Custom Module", module_submissions_store),
    ]

    target_store = None
    target_item = None

    for stype, store in stores:
        for item in store.list_all(tid):
            item_ref = item.get("reference_code") or item.get("id")
            if item_ref.lower() == ref.lower():
                item_email = item.get("email") or item.get("customer_email") or ""
                if user.get("role") not in {"admin", "staff"} and item_email.lower() != email:
                    raise HTTPException(status_code=403, detail="Unauthorized")
                target_store = store
                target_item = item
                break
        if target_item:
            break

    if not target_item:
        raise HTTPException(status_code=404, detail="Request reference not found")

    # Record receipt object
    receipt_data = {
        "payment_method": payload.payment_method,
        "transaction_reference": payload.transaction_reference,
        "receipt_file_url": payload.receipt_file_url,
        "amount": payload.amount or target_item.get("tuition_amount") or target_item.get("advance_amount") or 5000.0,
        "currency": payload.currency or "ETB",
        "submitted_at": datetime.now(timezone.utc).isoformat(),
        "submitted_by": email,
        "status": "UnderReview",
        "notes": payload.notes,
    }

    # Update target record status
    target_store.update(
        target_item["id"],
        {
            "payment_receipt": receipt_data,
            "payment_status": "ReceiptUploaded",
            "status": "PaymentUnderReview",
        },
        tid,
    )

    # Update associated invoice
    invoices = [i for i in invoices_store.list_all(tid) if i.get("reference_code", "").lower() == ref.lower()]
    for inv in invoices:
        invoices_store.update(inv["id"], {"status": "sent"}, tid)

    # Log audit event
    log_audit_event(
        tid,
        "PAYMENT_RECEIPT_UPLOADED",
        f"requests/{ref}",
        f"Client {email} uploaded payment receipt for Ref {ref} (Bank: {payload.payment_method}, TxRef: {payload.transaction_reference})",
        user_email=email,
    )

    return {
        "status": "success",
        "message": "Payment receipt uploaded successfully. Our finance team will review and verify your payment.",
        "reference_code": ref,
        "receipt": receipt_data,
        "current_status": "PaymentUnderReview",
    }
