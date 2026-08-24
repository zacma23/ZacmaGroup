"""Student Registration Module (Training Institute).

Handles student enrollments, course tracking, payment integration,
attendance session marking, approvals, and AI course recommendations.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.demo_data import students_store
from app.core.permissions import require_role
from app.core.tenancy import get_tenant_id
from app.models import (
    AttendanceMarkRequest,
    StudentRegistration,
    StudentRegistrationCreate,
    StudentRegistrationUpdate,
)
from app.services.ai_assistant_service import AiAssistantService
from app.services.approval_service import ApprovalService
from app.services.crm_service import CrmService
from app.services.payment_service import PaymentService

router = APIRouter(prefix="/students", tags=["students"])


@router.get("/registrations", response_model=list[StudentRegistration])
def list_registrations(
    course: str | None = None,
    status_filter: str | None = None,
    tenant_id: str = Depends(get_tenant_id),
):
    """List all student registrations with optional filtering."""
    registrations = students_store.list_all(tenant_id)
    if course:
        registrations = [r for r in registrations if r.get("course", "").lower() == course.lower()]
    if status_filter:
        registrations = [r for r in registrations if r.get("status", "").lower() == status_filter.lower()]
    return registrations


@router.post("/registrations", response_model=StudentRegistration, status_code=status.HTTP_201_CREATED)
def create_registration(
    payload: StudentRegistrationCreate,
    tenant_id: str = Depends(get_tenant_id),
):
    """Submit a new student registration.

    Automatically:
    1. Generates an AI course recommendation.
    2. Syncs/creates a CRM Contact with timeline history.
    3. Auto-generates an invoice with dynamic receiving account details.
    4. Enters Pending approval workflow.
    """
    # 1. AI Recommendation
    ai_rec = AiAssistantService.recommend_course(
        payload.education_level, payload.interests or payload.course
    )

    data = payload.model_dump()
    data["ai_course_recommendation"] = ai_rec
    data["status"] = "Pending"
    data["attendance"] = []

    created_reg = students_store.create(data, tenant_id)
    reg_id = created_reg["id"]

    # 2. CRM Contact Sync
    tags = ["Student", payload.course]
    if payload.specialty:
        tags.append(payload.specialty)
    if payload.schedule:
        tags.append(payload.schedule)

    action_text = f"Enrolled in {payload.course}"
    if payload.specialty:
        action_text += f" - {payload.specialty}"

    contact = CrmService.sync_contact(
        tenant_id=tenant_id,
        full_name=payload.full_name,
        email=payload.email,
        phone=payload.phone,
        address=payload.address,
        source_module="Student",
        status="Lead",
        tags=tags,
        initial_action=action_text,
        linked_entity_id=reg_id,
    )
    contact_id = contact.get("id")

    # 3. Invoice Generation
    inv_desc = f"Course Enrollment Fee: {payload.course}"
    if payload.specialty:
        inv_desc += f" ({payload.specialty})"

    invoice = PaymentService.generate_invoice(
        tenant_id=tenant_id,
        customer_name=payload.full_name,
        customer_email=payload.email,
        contact_id=contact_id,
        module_type="Student",
        amount=4500.0,  # Standard Course Tuition
        currency="ETB",
        description=inv_desc,
        payment_method=payload.payment_method,
    )

    # Link IDs and ensure reference code
    ref_code = created_reg.get("reference_code", f"ZAC-STU-{abs(hash(reg_id)) % 9000 + 1000}")
    students_store.update(
        reg_id,
        {
            "reference_code": ref_code,
            "linked_crm_contact_id": contact_id,
            "linked_invoice_id": invoice.get("id"),
        },
        tenant_id,
    )

    return students_store.get(reg_id, tenant_id)


@router.get("/registrations/{reg_id}", response_model=StudentRegistration)
def get_registration(reg_id: str, tenant_id: str = Depends(get_tenant_id)):
    """Get single registration details."""
    reg = students_store.get(reg_id, tenant_id)
    if not reg:
        raise HTTPException(status_code=404, detail="Student registration not found")
    return reg


@router.put("/registrations/{reg_id}", response_model=StudentRegistration)
def update_registration(
    reg_id: str,
    payload: StudentRegistrationUpdate,
    tenant_id: str = Depends(get_tenant_id),
):
    """Update registration fields."""
    updates = payload.model_dump(exclude_unset=True)
    updated = students_store.update(reg_id, updates, tenant_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Student registration not found")
    return updated


@router.post("/registrations/{reg_id}/approve")
def approve_registration(
    reg_id: str,
    comment: str = "Registration approved by admin",
    tenant_id: str = Depends(get_tenant_id),
    user: dict = Depends(require_role(["admin", "superadmin"])),
):
    """Admin approval of student registration."""
    admin_email = user.get("email", "admin@zacma.com")
    res = ApprovalService.approve(tenant_id, "student", reg_id, admin_email, comment)
    if not res:
        raise HTTPException(status_code=404, detail="Registration not found")
    return {"status": "success", "message": "Registration approved", "data": res}


@router.post("/registrations/{reg_id}/deny")
def deny_registration(
    reg_id: str,
    reason: str,
    tenant_id: str = Depends(get_tenant_id),
    user: dict = Depends(require_role(["admin", "superadmin"])),
):
    """Admin rejection of student registration."""
    admin_email = user.get("email", "admin@zacma.com")
    res = ApprovalService.deny(tenant_id, "student", reg_id, admin_email, reason)
    if not res:
        raise HTTPException(status_code=404, detail="Registration not found")
    return {"status": "success", "message": "Registration denied", "data": res}


@router.post("/registrations/{reg_id}/attendance")
def mark_attendance(
    reg_id: str,
    payload: AttendanceMarkRequest,
    tenant_id: str = Depends(get_tenant_id),
    user: dict = Depends(require_role(["admin", "superadmin", "staff"])),
):
    """Record student attendance for a course session."""
    reg = students_store.get(reg_id, tenant_id)
    if not reg:
        raise HTTPException(status_code=404, detail="Registration not found")

    attendance = reg.get("attendance", [])
    attendance.append(payload.model_dump())
    students_store.update(reg_id, {"attendance": attendance}, tenant_id)
    return {"status": "success", "attendance": attendance}


@router.get("/registrations/{reg_id}/welcome-draft")
def get_welcome_email_draft(reg_id: str, tenant_id: str = Depends(get_tenant_id)):
    """AI-drafted welcome onboarding email for admin preview."""
    reg = students_store.get(reg_id, tenant_id)
    if not reg:
        raise HTTPException(status_code=404, detail="Registration not found")
    draft = AiAssistantService.draft_welcome_email(reg["full_name"], reg["course"])
    return {"draft_welcome_email": draft}
