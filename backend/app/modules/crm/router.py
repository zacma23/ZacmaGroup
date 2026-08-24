"""CRM Engine Module.

Provides unified contact management, configurable sales pipeline, opportunities/deals,
activities tracking, chronological timeline feeds, admin notes, and cross-module client lifecycle tracking.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.demo_data import crm_contacts_store, leads_store
from app.core.permissions import require_role
from app.core.tenancy import get_tenant_id
from app.models import (
    ActivityCreate,
    ActivityResponse,
    ActivityUpdate,
    CrmContact,
    CrmContactCreate,
    CrmContactUpdate,
    CrmNote,
    CrmNoteCreate,
    LeadCreate,
    LeadResponse,
    LeadUpdate,
    OpportunityCreate,
    OpportunityResponse,
    OpportunityUpdate,
)
from app.services.crm_service import CrmService

router = APIRouter(prefix="/crm", tags=["crm"])


# ---------------------------------------------------------------------------
# 3.1 Sales Pipeline & Opportunities / Deals
# ---------------------------------------------------------------------------

@router.get("/pipeline")
def get_pipeline(tenant_id: str = Depends(get_tenant_id)):
    """Get aggregated sales pipeline breakdown by stages with values and deal lists."""
    return CrmService.get_pipeline_summary(tenant_id)


@router.get("/opportunities", response_model=list[OpportunityResponse])
def list_opportunities(
    stage: str | None = None,
    status_filter: str | None = None,
    person_id: str | None = None,
    organization_id: str | None = None,
    search: str | None = None,
    tenant_id: str = Depends(get_tenant_id),
):
    """List opportunities/deals with stage and status filters."""
    return CrmService.list_opportunities(
        tenant_id=tenant_id,
        stage=stage,
        status=status_filter,
        person_id=person_id,
        organization_id=organization_id,
        search=search,
    )


@router.post("/opportunities", response_model=OpportunityResponse, status_code=status.HTTP_201_CREATED)
def create_opportunity(
    payload: OpportunityCreate,
    tenant_id: str = Depends(get_tenant_id),
):
    """Create a new sales opportunity / deal."""
    data = payload.model_dump()
    if hasattr(payload.pipeline_stage, "value"):
        data["pipeline_stage"] = payload.pipeline_stage.value
    return CrmService.create_opportunity(tenant_id=tenant_id, payload=data)


@router.get("/opportunities/{opportunity_id}", response_model=OpportunityResponse)
def get_opportunity(
    opportunity_id: str,
    tenant_id: str = Depends(get_tenant_id),
):
    """Get single opportunity by ID."""
    opps = CrmService.list_opportunities(tenant_id=tenant_id)
    opp = next((o for o in opps if o["id"] == opportunity_id), None)
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return opp


@router.put("/opportunities/{opportunity_id}", response_model=OpportunityResponse)
def update_opportunity(
    opportunity_id: str,
    payload: OpportunityUpdate,
    tenant_id: str = Depends(get_tenant_id),
):
    """Update opportunity details, progress pipeline stage, or mark Won/Lost."""
    updates = payload.model_dump(exclude_unset=True)
    if "pipeline_stage" in updates and hasattr(updates["pipeline_stage"], "value"):
        updates["pipeline_stage"] = updates["pipeline_stage"].value
    updated = CrmService.update_opportunity(tenant_id, opportunity_id, updates)
    if not updated:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return updated


# ---------------------------------------------------------------------------
# 3.2 Activities & Tasks
# ---------------------------------------------------------------------------

@router.get("/activities", response_model=list[ActivityResponse])
def list_activities(
    activity_type: str | None = None,
    status_filter: str | None = None,
    person_id: str | None = None,
    opportunity_id: str | None = None,
    tenant_id: str = Depends(get_tenant_id),
):
    """List CRM activities (Calls, Emails, SMS, WhatsApp, Meetings, Tasks, Notes, Follow-ups)."""
    return CrmService.list_activities(
        tenant_id=tenant_id,
        activity_type=activity_type,
        status=status_filter,
        person_id=person_id,
        opportunity_id=opportunity_id,
    )


@router.post("/activities", response_model=ActivityResponse, status_code=status.HTTP_201_CREATED)
def create_activity(
    payload: ActivityCreate,
    tenant_id: str = Depends(get_tenant_id),
):
    """Log a new activity or task."""
    data = payload.model_dump()
    if hasattr(payload.activity_type, "value"):
        data["activity_type"] = payload.activity_type.value
    return CrmService.create_activity(tenant_id=tenant_id, payload=data)


@router.put("/activities/{activity_id}", response_model=ActivityResponse)
def update_activity(
    activity_id: str,
    payload: ActivityUpdate,
    tenant_id: str = Depends(get_tenant_id),
):
    """Update activity or mark completed."""
    updates = payload.model_dump(exclude_unset=True)
    updated = CrmService.update_activity(tenant_id, activity_id, updates)
    if not updated:
        raise HTTPException(status_code=404, detail="Activity not found")
    return updated


# ---------------------------------------------------------------------------
# 3.3 CRM Contacts (Unified Engine)
# ---------------------------------------------------------------------------

@router.get("/contacts", response_model=list[CrmContact])
def list_contacts(
    source_module: str | None = None,
    status_filter: str | None = None,
    search: str | None = None,
    tenant_id: str = Depends(get_tenant_id),
):
    """List all unified CRM contacts with filters and search."""
    return CrmService.list_contacts(
        tenant_id=tenant_id,
        source_module=source_module,
        status=status_filter,
        search=search,
    )


@router.post("/contacts", response_model=CrmContact, status_code=status.HTTP_201_CREATED)
def create_contact(
    payload: CrmContactCreate,
    tenant_id: str = Depends(get_tenant_id),
):
    """Manually create a new CRM contact and link to People."""
    contact = CrmService.sync_contact(
        tenant_id=tenant_id,
        full_name=payload.full_name,
        email=payload.email,
        phone=payload.phone,
        address=payload.address,
        country=payload.country or "Ethiopia",
        source_module=payload.source_module.value,
        status=payload.status.value,
        tags=payload.tags,
        initial_action="Manual Contact Creation",
    )
    if payload.notes:
        CrmService.add_note(tenant_id, contact["id"], "admin", payload.notes)
    return crm_contacts_store.get(contact["id"], tenant_id)


@router.get("/contacts/{contact_id}", response_model=CrmContact)
def get_contact(contact_id: str, tenant_id: str = Depends(get_tenant_id)):
    """Get single CRM contact with complete activity timeline and notes."""
    contact = crm_contacts_store.get(contact_id, tenant_id)
    if not contact:
        raise HTTPException(status_code=404, detail="CRM contact not found")
    return contact


@router.put("/contacts/{contact_id}", response_model=CrmContact)
def update_contact(
    contact_id: str,
    payload: CrmContactUpdate,
    tenant_id: str = Depends(get_tenant_id),
):
    """Update CRM contact profile, status, or tags."""
    updates = payload.model_dump(exclude_unset=True)
    if "status" in updates and hasattr(updates["status"], "value"):
        updates["status"] = updates["status"].value
    updated = crm_contacts_store.update(contact_id, updates, tenant_id)
    if not updated:
        raise HTTPException(status_code=404, detail="CRM contact not found")
    return updated


@router.post("/contacts/{contact_id}/notes", response_model=CrmNote)
def add_contact_note(
    contact_id: str,
    payload: CrmNoteCreate,
    tenant_id: str = Depends(get_tenant_id),
    user: dict = Depends(require_role(["admin", "superadmin", "staff"])),
):
    """Add an admin note to a contact profile."""
    author = user.get("full_name") or user.get("email") or "Admin"
    note = CrmService.add_note(tenant_id, contact_id, author, payload.content)
    if not note:
        raise HTTPException(status_code=404, detail="CRM contact not found")
    return note


# ---------------------------------------------------------------------------
# 3.4 Legacy Leads Endpoints (Backward Compatibility)
# ---------------------------------------------------------------------------

@router.get("/leads", response_model=list[LeadResponse])
def list_leads(tenant_id: str = Depends(get_tenant_id)):
    return leads_store.list_all(tenant_id)


@router.post("/leads", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
def create_lead(payload: LeadCreate, tenant_id: str = Depends(get_tenant_id)):
    # Synchronize into CRM and People layer
    CrmService.sync_contact(
        tenant_id=tenant_id,
        full_name=payload.name,
        email=payload.email,
        phone=payload.phone,
        source_module=payload.source or "manual",
        status="Lead",
        initial_action=f"Lead Created: {payload.name}",
    )
    return leads_store.create(payload.model_dump(), tenant_id)


@router.get("/leads/{lead_id}", response_model=LeadResponse)
def get_lead(lead_id: str, tenant_id: str = Depends(get_tenant_id)):
    lead = leads_store.get(lead_id, tenant_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.put("/leads/{lead_id}", response_model=LeadResponse)
def update_lead(lead_id: str, payload: LeadUpdate, tenant_id: str = Depends(get_tenant_id)):
    updated = leads_store.update(lead_id, payload.model_dump(exclude_unset=True), tenant_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Lead not found")
    return updated


@router.delete("/leads/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lead(lead_id: str, tenant_id: str = Depends(get_tenant_id)):
    if not leads_store.delete(lead_id, tenant_id):
        raise HTTPException(status_code=404, detail="Lead not found")
