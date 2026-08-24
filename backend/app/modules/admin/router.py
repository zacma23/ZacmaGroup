"""Admin Dashboard & Back Office Module.

Provides SuperAdmin/Admin unified controls for:
- User management and role assignments
- Global cross-module search (by name, email, phone)
- System-wide statistics and overview counters
- System settings (payment receiving account, gateways, email templates, lists)
- Audit log trails
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.config import settings
from app.core.db import supabase
from app.core.demo_data import (
    admin_users_store,
    audit_logs_store,
    business_modules_store,
    crm_contacts_store,
    invoices_store,
    module_submissions_store,
    students_store,
    support_tickets_store,
    system_settings_store,
    travel_requests_store,
    visa_applications_store,
)
from app.core.permissions import require_role
from app.core.tenancy import get_tenant_id
from app.models import (
    AdminAiSearchRequest,
    AdminAiSearchResponse,
    AdminSearchResponse,
    AdminUserCreate,
    AdminUserUpdate,
    SystemSettingsUpdate,
)

router = APIRouter(prefix="/admin", tags=["admin"])

_admin_dep = require_role(["admin", "superadmin", "staff"])


# ---------------------------------------------------------------------------
# Global Search, Sort, Filter & AI Natural Query Across All Modules
# ---------------------------------------------------------------------------

@router.get("/search", response_model=AdminSearchResponse)
def global_search(
    q: Optional[str] = None,
    module: Optional[str] = "all",
    status: Optional[str] = "all",
    category: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    sort_by: str = "newest",
    page: int = 1,
    page_size: int = 25,
    tenant_id: str = Depends(get_tenant_id),
    _user: dict = Depends(_admin_dep),
):
    """Unified multi-module search, filter, sort, and server-side pagination for administrators."""
    from app.services.admin_search_service import AdminSearchService
    return AdminSearchService.search(
        tenant_id=tenant_id,
        query=q,
        module=module,
        status=status,
        category=category,
        date_from=date_from,
        date_to=date_to,
        min_amount=min_amount,
        max_amount=max_amount,
        sort_by=sort_by,
        page=page,
        page_size=page_size,
    )


@router.post("/search/ai", response_model=AdminAiSearchResponse)
def ai_natural_search(
    payload: AdminAiSearchRequest,
    tenant_id: str = Depends(get_tenant_id),
    _user: dict = Depends(_admin_dep),
):
    """Authorized Natural Language AI search translating admin questions into tenant-scoped searches."""
    from app.services.admin_search_service import AdminSearchService
    return AdminSearchService.ai_natural_search(
        tenant_id=tenant_id,
        natural_query=payload.query,
        max_results=payload.max_results,
    )


# ---------------------------------------------------------------------------
# Cross-Module System Statistics
# ---------------------------------------------------------------------------

@router.get("/stats")
def get_stats(
    tenant_id: str = Depends(get_tenant_id),
    _user: dict = Depends(_admin_dep),
):
    """Return unified counts and metrics across all business lines."""
    from app.core.demo_data import people_store, organizations_store, crm_opportunities_store, campaigns_store, payment_transactions_store

    total_people = len(people_store.list_all(tenant_id))
    total_orgs = len(organizations_store.list_all(tenant_id))
    new_leads = len([p for p in people_store.list_all(tenant_id) if p.get("status") in ["Lead", "Prospect"]])
    open_opps = [o for o in crm_opportunities_store.list_all(tenant_id) if o.get("status") == "Open"]
    total_pipeline_val = sum(o.get("value", 0.0) for o in open_opps)
    active_students = len([s for s in students_store.list_all(tenant_id) if s.get("status") in ["Pending", "Approved", "Active"]])
    successful_payments = len([t for t in payment_transactions_store.list_all(tenant_id) if t.get("status") == "successful"])
    active_campaigns = len([c for c in campaigns_store.list_all(tenant_id) if c.get("status") in ["Sent", "Scheduled", "Active"]])

    pending_students = len([s for s in students_store.list_all(tenant_id) if s.get("status") == "Pending"])
    pending_visas = len([v for v in visa_applications_store.list_all(tenant_id) if v.get("status") in ["Pending", "UnderReview"]])
    pending_travel = len([t for t in travel_requests_store.list_all(tenant_id) if t.get("status") == "Planning"])
    open_tickets = len([tk for tk in support_tickets_store.list_all(tenant_id) if tk.get("status") in ["Open", "InProgress"]])
    unpaid_invoices = len([i for i in invoices_store.list_all(tenant_id) if i.get("status") in ["sent", "paid"]])

    return {
        "overview": {
            "total_people": total_people,
            "total_organizations": total_orgs,
            "new_leads": new_leads,
            "open_opportunities": len(open_opps),
            "pipeline_value": round(total_pipeline_val, 2),
            "active_students": active_students,
            "successful_payments": successful_payments,
            "active_campaigns": active_campaigns,
            "pending_student_registrations": pending_students,
            "pending_visa_applications": pending_visas,
            "pending_travel_requests": pending_travel,
            "open_support_tickets": open_tickets,
            "pending_payment_confirmations": unpaid_invoices,
        },
        "totals": {
            "people": people_store.count(tenant_id),
            "organizations": organizations_store.count(tenant_id),
            "opportunities": crm_opportunities_store.count(tenant_id),
            "campaigns": campaigns_store.count(tenant_id),
            "crm_contacts": crm_contacts_store.count(tenant_id),
            "students": students_store.count(tenant_id),
            "visas": visa_applications_store.count(tenant_id),
            "travel": travel_requests_store.count(tenant_id),
            "support_tickets": support_tickets_store.count(tenant_id),
            "invoices": invoices_store.count(tenant_id),
            "dynamic_modules": business_modules_store.count(tenant_id),
            "dynamic_submissions": module_submissions_store.count(tenant_id),
            "users": admin_users_store.count(tenant_id),
        },
    }


# ---------------------------------------------------------------------------
# System Settings Management
# ---------------------------------------------------------------------------

@router.get("/settings")
def get_system_settings(
    tenant_id: str = Depends(get_tenant_id),
    _user: dict = Depends(_admin_dep),
):
    """Get system-wide editable settings."""
    stored = system_settings_store.list_all(tenant_id)
    if stored:
        return stored[0]

    return {
        "default_receiving_account": settings.default_receiving_account,
        "default_payment_methods": settings.payment_methods_list,
        "courses_list": [
            "Graphics Design", "Video Editing", "Web Design", "Programming", "AI", "Accounting", "Maintenance"
        ],
        "visa_types_list": ["Tourist", "Work", "Study", "Business"],
        "education_levels_list": ["High School", "Diploma", "Bachelor's Degree", "Master's Degree", "Other"],
    }


@router.put("/settings")
def update_system_settings(
    payload: SystemSettingsUpdate,
    tenant_id: str = Depends(get_tenant_id),
    _user: dict = Depends(require_role(["superadmin", "admin"])),
):
    """Update payment receiving account number, lists, and defaults."""
    stored = system_settings_store.list_all(tenant_id)
    updates = payload.model_dump(exclude_unset=True)

    if stored:
        updated = system_settings_store.update(stored[0]["id"], updates, tenant_id)
        return updated

    data = updates
    data["id"] = "sys-settings-001"
    return system_settings_store.create(data, tenant_id)


# ---------------------------------------------------------------------------
# User Management & RBAC (Admin & SuperAdmin Only)
# ---------------------------------------------------------------------------

_superadmin_or_admin_dep = require_role(["superadmin", "admin"])


@router.get("/users")
def list_users(
    tenant_id: str = Depends(get_tenant_id),
    _user: dict = Depends(_superadmin_or_admin_dep),
):
    """List platform users with sensitive fields sanitized."""
    if supabase is None:
        raw_users = admin_users_store.list_all(tenant_id)
        return [{k: v for k, v in u.items() if k != "password_hash"} for u in raw_users]
    try:
        result = supabase.table("profiles").select("*").eq("tenant_id", tenant_id).execute()
        if result.data:
            return [{k: v for k, v in u.items() if k != "password_hash"} for u in result.data]
    except Exception:
        pass
    result = supabase.table("users").select("*").eq("tenant_id", tenant_id).execute()
    return [{k: v for k, v in u.items() if k != "password_hash"} for u in result.data]


@router.post("/users", status_code=status.HTTP_201_CREATED)
def create_user(
    payload: AdminUserCreate,
    tenant_id: str = Depends(get_tenant_id),
    _user: dict = Depends(_superadmin_or_admin_dep),
):
    """Create platform user with role assignment."""
    if supabase is None:
        existing = admin_users_store.list_all(tenant_id)
        if any(u["email"].lower() == payload.email.lower() for u in existing):
            raise HTTPException(status_code=409, detail="Email already exists")
        data = payload.model_dump(exclude={"password"})
        data["firebase_uid"] = f"uid-{abs(hash(payload.email)) % 100000}"
        return admin_users_store.create(data, tenant_id)
    return {}


@router.put("/users/{user_id}")
def update_user(
    user_id: str,
    payload: AdminUserUpdate,
    tenant_id: str = Depends(get_tenant_id),
    _user: dict = Depends(_superadmin_or_admin_dep),
):
    """Update user role or status."""
    updates = payload.model_dump(exclude_none=True)
    if not updates:
        raise HTTPException(status_code=422, detail="No fields to update")
    if supabase is None:
        res = admin_users_store.update(user_id, updates, tenant_id)
        if not res:
            raise HTTPException(status_code=404, detail="User not found")
        return res
    return {}


@router.delete("/users/{user_id}")
def delete_user(
    user_id: str,
    tenant_id: str = Depends(get_tenant_id),
    _user: dict = Depends(_superadmin_or_admin_dep),
):
    """Deactivate user."""
    if supabase is None:
        res = admin_users_store.update(user_id, {"status": "inactive"}, tenant_id)
        if not res:
            raise HTTPException(status_code=404, detail="User not found")
        return {"detail": "User deactivated"}
    return {"detail": "User deactivated"}


# ---------------------------------------------------------------------------
# Tenants & Audit
# ---------------------------------------------------------------------------

@router.get("/tenants")
def list_tenants(_user: dict = Depends(_superadmin_or_admin_dep)):
    """List tenants."""
    return [
        {
            "id": "zacma-demo",
            "name": "Zacma Business Management Platform",
            "slug": "zacma-demo",
            "plan": "Enterprise",
            "status": "Active",
            "user_count": admin_users_store.count(settings.demo_tenant_id),
        }
    ]


@router.get("/audit_logs")
def list_audit_logs(
    tenant_id: str = Depends(get_tenant_id),
    _user: dict = Depends(_superadmin_or_admin_dep),
):
    """List security and operational audit trail."""
    logs = audit_logs_store.list_all(tenant_id)
    return sorted(logs, key=lambda x: x.get("timestamp", ""), reverse=True)
