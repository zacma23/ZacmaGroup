"""A compact, stable data contract for the web dashboard."""

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends

from app.core.config import settings
from app.core.db import database_status
from app.core.tenancy import get_tenant_id


router = APIRouter(prefix="/dashboard", tags=["dashboard"])


MODULES: tuple[dict[str, str], ...] = (
    {
        "id": "crm",
        "name": "CRM",
        "description": "Leads, contacts, and account activity.",
        "endpoint": "/api/v1/crm/leads",
        "metric": "24 open leads",
    },
    {
        "id": "hrm",
        "name": "HRM",
        "description": "Employee records and people operations.",
        "endpoint": "/api/v1/hrm/employees",
        "metric": "18 team members",
    },
    {
        "id": "payments",
        "name": "Payments",
        "description": "Invoices, collections, and payment status.",
        "endpoint": "/api/v1/payments/invoices",
        "metric": "7 invoices due",
    },
    {
        "id": "marketing",
        "name": "Marketing",
        "description": "Campaign performance and audience activity.",
        "endpoint": "/api/v1/marketing/campaigns",
        "metric": "3 active campaigns",
    },
    {
        "id": "training",
        "name": "Training",
        "description": "Courses, enrolments, and completion progress.",
        "endpoint": "/api/v1/training/courses",
        "metric": "6 courses active",
    },
    {
        "id": "travel",
        "name": "Travel",
        "description": "Bookings and upcoming itineraries.",
        "endpoint": "/api/v1/travel/bookings",
        "metric": "4 upcoming trips",
    },
    {
        "id": "visa",
        "name": "Visa",
        "description": "Applications, documents, and case progress.",
        "endpoint": "/api/v1/visa/applications",
        "metric": "9 applications in review",
    },
)


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
def get_overview(tenant_id: str = Depends(get_tenant_id)) -> dict[str, Any]:
    """Return the dashboard summary without exposing configuration secrets."""
    return {
        "tenantId": tenant_id,
        "environment": settings.app_environment,
        "isDemo": settings.demo_mode,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "metrics": [
            {"label": "Open leads", "value": "24", "change": "+12% this month"},
            {"label": "Applications in review", "value": "9", "change": "2 need documents"},
            {"label": "Invoices due", "value": "$12.4k", "change": "7 invoices"},
            {"label": "Training completion", "value": "86%", "change": "+4% this quarter"},
        ],
        "modules": [{**module, "status": "ready"} for module in MODULES],
        "activity": [
            {"title": "Visa case documents reviewed", "detail": "Student visa · 12 minutes ago"},
            {"title": "New CRM lead assigned", "detail": "Website enquiry · 34 minutes ago"},
            {"title": "Course completion recorded", "detail": "Workplace onboarding · 1 hour ago"},
        ],
        "services": _service_status(),
    }
