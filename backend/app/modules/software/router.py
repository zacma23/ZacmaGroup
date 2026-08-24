"""Software Development Module.

Handles software capabilities, client project requests, scope specifications,
CRM synchronization, advance invoicing, and AI-driven system architecture generation.
"""

from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.demo_data import (
    crm_contacts_store,
    invoices_store,
    software_projects_store,
)
from app.core.tenancy import get_tenant_id
from app.models import (
    SoftwareProjectCreate,
    SoftwareProjectResponse,
    SoftwareProjectUpdate,
)
from app.services.crm_service import CrmService
from app.services.payment_service import PaymentService

router = APIRouter(prefix="/software", tags=["software_development"])


CAPABILITIES_CATALOG = {
    "categories": [
        {
            "id": "web_apps",
            "name": "Web Application & SaaS Development",
            "description": "Full-stack cloud web applications built with Next.js, React, FastAPI, Node.js, and PostgreSQL.",
            "examples": ["Enterprise Dashboards", "SaaS Multi-Tenant Platforms", "Client Portals", "Admin Consoles"],
        },
        {
            "id": "mobile_apps",
            "name": "Mobile Application Engineering",
            "description": "Native and cross-platform Android & iOS applications using Flutter and React Native.",
            "examples": ["Telehealth Apps", "Fintech & Mobile Wallets", "Ride & Delivery Services", "Field Data Collectors"],
        },
        {
            "id": "erp_crm",
            "name": "ERP & CRM Custom Development",
            "description": "Customized business management, inventory, payroll, and workflow automation systems.",
            "examples": ["Zacma ERP (https://erp.zacmaa.net/)", "Supply Chain POS", "Custom Sales Pipelines"],
        },
        {
            "id": "school_systems",
            "name": "School & Campus Management Systems",
            "description": "Admissions, grading, attendance, automated tuition invoices, and parent portals.",
            "examples": ["MySchool Platform (https://myschool.zacmaa.net/)", "Academy Portals", "LMS"],
        },
        {
            "id": "ecommerce",
            "name": "E-Commerce & Payment Gateway Solutions",
            "description": "Multi-vendor and standalone digital storefronts with TeleBirr, CBE Birr, and Chapa integration.",
            "examples": ["Zacma E-Commerce (https://ecommerce.zacmaa.net/)", "Online Supermarkets", "B2B Marketplaces"],
        },
        {
            "id": "ai_solutions",
            "name": "AI Applications & Autonomous Agents",
            "description": "LLM integrations, RAG pipelines, automated document classifiers, and conversational agents.",
            "examples": ["Customer Support AI Agents", "Document Risk Auditing", "Automated Telegram Bots"],
        },
        {
            "id": "freelance_talent",
            "name": "Dedicated Engineering Teams & Marketplace",
            "description": "Vetted software engineers, UI/UX designers, and cloud architects for custom enterprise contracts.",
            "examples": ["Zacma Freelancer (https://freelancer.zacmaa.net/)"],
        },
    ],
    "tech_stacks": ["Next.js", "React", "Python/FastAPI", "Flutter", "PostgreSQL", "Supabase", "Docker", "LangChain", "Redis"],
    "supported_platforms": ["Web", "Android", "iOS", "Desktop (Windows/Mac/Linux)", "Cloud / Microservices"],
}


# ---------------------------------------------------------------------------
# GET /software/capabilities
# ---------------------------------------------------------------------------

@router.get("/capabilities")
def get_capabilities():
    """List Zacma Group software development services, platforms, and capabilities."""
    return CAPABILITIES_CATALOG


# ---------------------------------------------------------------------------
# GET /software/projects
# ---------------------------------------------------------------------------

@router.get("/projects", response_model=list[SoftwareProjectResponse])
def list_projects(
    industry: str | None = None,
    status_filter: str | None = None,
    tenant_id: str = Depends(get_tenant_id),
):
    """List all software development project requests with optional filtering."""
    projects = software_projects_store.list_all(tenant_id)
    if industry:
        projects = [p for p in projects if p.get("industry", "").lower() == industry.lower()]
    if status_filter:
        projects = [p for p in projects if p.get("status", "").lower() == status_filter.lower()]
    return projects


# ---------------------------------------------------------------------------
# POST /software/projects
# ---------------------------------------------------------------------------

@router.post("/projects", response_model=SoftwareProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: SoftwareProjectCreate,
    tenant_id: str = Depends(get_tenant_id),
):
    """Submit a new Software Development project request.

    Automatically:
    1. Creates project record with reference code (e.g. ZAC-DEV-XXXX).
    2. Syncs/creates CRM Contact.
    3. Generates advance invoice with dynamic receiving account details.
    4. Places request in pending review queue.
    """
    data = payload.model_dump()
    data["status"] = "Pending"
    data["payment_status"] = "Pending"

    created = software_projects_store.create(data, tenant_id)
    proj_id = created["id"]
    ref_code = created.get("reference_code", f"ZAC-DEV-{abs(hash(proj_id)) % 9000 + 1000}")
    software_projects_store.update(proj_id, {"reference_code": ref_code}, tenant_id)

    # 2. CRM Contact Sync
    contact = CrmService.sync_contact(
        tenant_id=tenant_id,
        full_name=payload.client_name,
        email=payload.email,
        phone=payload.phone,
        address=payload.industry or "Addis Ababa",
        country="Ethiopia",
        source_module="Custom",
        status="Lead",
        tags=["Software Development", payload.industry or "General", *payload.platforms],
        initial_action=f"Requested Software Development: {payload.project_name}",
        linked_entity_id=proj_id,
    )
    contact_id = contact.get("id")

    # 3. Advance Payment Invoice
    invoice = PaymentService.generate_invoice(
        tenant_id=tenant_id,
        customer_name=payload.client_name,
        customer_email=payload.email,
        contact_id=contact_id,
        module_type="Software",
        amount=payload.advance_amount or 15000.0,
        currency=payload.currency or "ETB",
        description=f"Advance Engineering & Architecture Fee: {payload.project_name} ({ref_code})",
        payment_method=payload.advance_payment_method or "CBE",
    )

    # Link references
    software_projects_store.update(
        proj_id,
        {
            "linked_crm_contact_id": contact_id,
            "linked_invoice_id": invoice.get("id"),
        },
        tenant_id,
    )

    return software_projects_store.get(proj_id, tenant_id)


# ---------------------------------------------------------------------------
# GET /software/projects/{id_or_ref}
# ---------------------------------------------------------------------------

@router.get("/projects/{id_or_ref}", response_model=SoftwareProjectResponse)
def get_project(id_or_ref: str, tenant_id: str = Depends(get_tenant_id)):
    """Get detailed project request by ID or Reference Code."""
    # First search by ID
    proj = software_projects_store.get(id_or_ref, tenant_id)
    if not proj:
        # Search by reference code
        for p in software_projects_store.list_all(tenant_id):
            if p.get("reference_code", "").lower() == id_or_ref.strip().lower():
                return p
        raise HTTPException(status_code=404, detail="Software project request not found")
    return proj


# ---------------------------------------------------------------------------
# PUT /software/projects/{id_or_ref}
# ---------------------------------------------------------------------------

@router.put("/projects/{id_or_ref}", response_model=SoftwareProjectResponse)
def update_project(
    id_or_ref: str,
    payload: SoftwareProjectUpdate,
    tenant_id: str = Depends(get_tenant_id),
):
    """Update software project request details."""
    proj = software_projects_store.get(id_or_ref, tenant_id)
    target_id = id_or_ref
    if not proj:
        for p in software_projects_store.list_all(tenant_id):
            if p.get("reference_code", "").lower() == id_or_ref.strip().lower():
                proj = p
                target_id = p["id"]
                break

    if not proj:
        raise HTTPException(status_code=404, detail="Software project request not found")

    updates = {k: v for k, v in payload.model_dump().items() if v is not None}
    updated = software_projects_store.update(target_id, updates, tenant_id)
    return updated
