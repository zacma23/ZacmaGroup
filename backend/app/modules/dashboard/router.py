"""Dashboard overview endpoint — provides live metrics from demo data or Supabase."""

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends

from app.core.config import settings
from app.core.db import database_status, supabase
from app.core.demo_data import (
    leads_store,
    employees_store,
    visa_apps_store,
    invoices_store,
    courses_store,
    bookings_store,
    campaigns_store,
    audit_logs_store,
)
from app.core.permissions import require_role
from app.core.tenancy import get_tenant_id


router = APIRouter(prefix="/dashboard", tags=["dashboard"])


MODULES: tuple[dict[str, str], ...] = (
    {
        "id": "crm",
        "name": "CRM",
        "description": "Leads, contacts, and account activity.",
        "endpoint": "/api/v1/crm/leads",
    },
    {
        "id": "hrm",
        "name": "HRM",
        "description": "Employee records and people operations.",
        "endpoint": "/api/v1/hrm/employees",
    },
    {
        "id": "payments",
        "name": "Payments",
        "description": "Invoices, collections, and payment status.",
        "endpoint": "/api/v1/payments/invoices",
    },
    {
        "id": "marketing",
        "name": "Marketing",
        "description": "Campaign performance and audience activity.",
        "endpoint": "/api/v1/marketing/campaigns",
    },
    {
        "id": "training",
        "name": "Training",
        "description": "Courses, enrolments, and completion progress.",
        "endpoint": "/api/v1/training/courses",
    },
    {
        "id": "travel",
        "name": "Travel",
        "description": "Bookings and upcoming itineraries.",
        "endpoint": "/api/v1/travel/bookings",
    },
    {
        "id": "visa",
        "name": "Visa",
        "description": "Applications, documents, and case progress.",
        "endpoint": "/api/v1/visa/applications",
    },
)


def _get_counts(tenant_id: str) -> dict[str, int]:
    """Get record counts from demo stores or Supabase."""
    if supabase is None:
        return {
            "leads": leads_store.count(tenant_id),
            "employees": employees_store.count(tenant_id),
            "invoices": invoices_store.count(tenant_id),
            "campaigns": campaigns_store.count(tenant_id),
            "courses": courses_store.count(tenant_id),
            "bookings": bookings_store.count(tenant_id),
            "applications": visa_apps_store.count(tenant_id),
        }

    counts = {}
    for table, key in [
        ("leads", "leads"),
        ("employees", "employees"),
        ("invoices", "invoices"),
        ("campaigns", "campaigns"),
        ("courses", "courses"),
        ("bookings", "bookings"),
        ("visa_applications", "applications"),
    ]:
        try:
            result = supabase.table(table).select("id", count="exact").eq("tenant_id", tenant_id).execute()
            counts[key] = result.count or 0
        except Exception:
            counts[key] = 0
    return counts


def _get_recent_activity(tenant_id: str) -> list[dict[str, str]]:
    """Get recent activity from audit logs."""
    if supabase is None:
        logs = audit_logs_store.list_all(tenant_id)
        sorted_logs = sorted(logs, key=lambda x: x.get("timestamp", ""), reverse=True)[:5]
        return [
            {
                "title": f"{log['action']} — {log['resource']}",
                "detail": f"{log.get('details', '')} · {log.get('user_email', 'system')}",
            }
            for log in sorted_logs
        ]

    try:
        result = (
            supabase.table("audit_logs")
            .select("*")
            .eq("tenant_id", tenant_id)
            .order("timestamp", desc=True)
            .limit(5)
            .execute()
        )
        return [
            {
                "title": f"{log['action']} — {log.get('resource', '')}",
                "detail": f"{log.get('details', '')} · {log.get('user_email', 'system')}",
            }
            for log in (result.data or [])
        ]
    except Exception:
        return []


def _service_status() -> list[dict[str, str]]:
    database = database_status()
    ai_configured = bool(settings.omniroute_key) or bool(settings.ollama_base_url)
    return [
        {"name": "API", "status": "healthy", "detail": settings.app_environment},
        {
            "name": "Database",
            "status": "configured" if database["configured"] else "demo",
            "detail": database["provider"],
        },
        {
            "name": "AI gateway",
            "status": "configured" if ai_configured else "not configured",
            "detail": settings.ollama_model,
        },
    ]


@router.get("/overview")
def get_overview(
    tenant_id: str = Depends(get_tenant_id),
    _user: dict = Depends(require_role(["admin", "superadmin", "staff", "finance", "hrm", "manager"])),
) -> dict[str, Any]:
    """Return the dashboard summary with live metrics from data stores."""
    counts = _get_counts(tenant_id)

    module_metrics = {
        "crm": f"{counts.get('leads', 0)} open leads",
        "hrm": f"{counts.get('employees', 0)} team members",
        "payments": f"{counts.get('invoices', 0)} invoices",
        "marketing": f"{counts.get('campaigns', 0)} active campaigns",
        "training": f"{counts.get('courses', 0)} courses active",
        "travel": f"{counts.get('bookings', 0)} bookings",
        "visa": f"{counts.get('applications', 0)} applications",
    }

    return {
        "tenantId": tenant_id,
        "environment": settings.app_environment,
        "isDemo": settings.demo_mode,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "metrics": [
            {"label": "Open leads", "value": str(counts.get("leads", 0)), "change": "From CRM module"},
            {"label": "Applications in review", "value": str(counts.get("applications", 0)), "change": "Visa module"},
            {"label": "Invoices", "value": str(counts.get("invoices", 0)), "change": "Payments module"},
            {"label": "Active courses", "value": str(counts.get("courses", 0)), "change": "Training module"},
        ],
        "modules": [
            {**module, "status": "ready", "metric": module_metrics.get(module["id"], "")}
            for module in MODULES
        ],
        "activity": _get_recent_activity(tenant_id),
        "services": _service_status(),
    }
