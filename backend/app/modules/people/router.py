"""Unified People & Organization Central Directory Router."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.permissions import require_role
from app.core.tenancy import get_tenant_id
from app.models import (
    OrganizationCreate,
    OrganizationResponse,
    OrganizationUpdate,
    PersonCreate,
    PersonDetailedProfile,
    PersonResponse,
    PersonUpdate,
)
from app.services.people_service import PeopleService

router = APIRouter(prefix="/people", tags=["people"])


# ---------------------------------------------------------------------------
# Organizations
# ---------------------------------------------------------------------------

@router.get("/organizations/list", response_model=list[OrganizationResponse])
def list_organizations(
    search: str | None = None,
    tenant_id: str = Depends(get_tenant_id),
):
    """List all corporate organizations and businesses."""
    return PeopleService.list_organizations(tenant_id=tenant_id, search=search)


@router.post("/organizations", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
def create_organization(
    payload: OrganizationCreate,
    tenant_id: str = Depends(get_tenant_id),
):
    """Create a new corporate organization."""
    return PeopleService.find_or_create_organization(
        tenant_id=tenant_id,
        name=payload.name,
        business_type=payload.business_type,
        email=payload.email,
        phone=payload.phone,
        website=payload.website,
        industry=payload.industry,
        address=payload.address,
        city=payload.city,
        country=payload.country,
        source=payload.source,
        notes=payload.notes,
    )


@router.get("/organizations/{org_id}", response_model=OrganizationResponse)
def get_organization(
    org_id: str,
    tenant_id: str = Depends(get_tenant_id),
):
    """Get single organization record."""
    org = PeopleService.get_organization_by_id(tenant_id, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org


# ---------------------------------------------------------------------------
# People Directory
# ---------------------------------------------------------------------------

@router.get("", response_model=list[PersonResponse])
def list_people(
    person_type: str | None = None,
    status_filter: str | None = None,
    organization_id: str | None = None,
    search: str | None = None,
    tenant_id: str = Depends(get_tenant_id),
):
    """List all people (Individuals, Customers, Leads, Students, Staff, Partners, Vendors)."""
    return PeopleService.list_people(
        tenant_id=tenant_id,
        person_type=person_type,
        status_filter=status_filter,
        organization_id=organization_id,
        search=search,
    )


@router.post("", response_model=PersonResponse, status_code=status.HTTP_201_CREATED)
def create_person(
    payload: PersonCreate,
    tenant_id: str = Depends(get_tenant_id),
):
    """Create or match a Person without duplicates."""
    return PeopleService.find_or_create_person(
        tenant_id=tenant_id,
        full_name=payload.full_name,
        email=payload.email,
        phone=payload.phone,
        alt_phone=payload.alt_phone,
        organization_id=payload.organization_id,
        job_title=payload.job_title,
        person_type=payload.person_type.value,
        status=payload.status.value,
        tags=payload.tags,
        address=payload.address,
        city=payload.city,
        country=payload.country,
        source=payload.source,
        notes=payload.notes,
        initial_action="Direct Person Creation",
    )


@router.get("/{person_id}", response_model=PersonResponse)
def get_person(
    person_id: str,
    tenant_id: str = Depends(get_tenant_id),
):
    """Retrieve single person record."""
    person = PeopleService.get_person_by_id(tenant_id, person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    return person


@router.get("/{person_id}/profile", response_model=PersonDetailedProfile)
def get_person_360_profile(
    person_id: str,
    tenant_id: str = Depends(get_tenant_id),
):
    """Get 360-degree unified profile with CRM deals, activities, student courses, payment history, marketing logs, and timeline."""
    profile = PeopleService.get_person_detailed_profile(tenant_id, person_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Person not found")
    return profile


@router.put("/{person_id}", response_model=PersonResponse)
def update_person(
    person_id: str,
    payload: PersonUpdate,
    tenant_id: str = Depends(get_tenant_id),
):
    """Update person details."""
    updates = payload.model_dump(exclude_unset=True)
    if "person_type" in updates and hasattr(updates["person_type"], "value"):
        updates["person_type"] = updates["person_type"].value
    if "status" in updates and hasattr(updates["status"], "value"):
        updates["status"] = updates["status"].value

    updated = PeopleService.update_person(tenant_id, person_id, updates)
    if not updated:
        raise HTTPException(status_code=404, detail="Person not found")
    return updated


@router.delete("/{person_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_person(
    person_id: str,
    tenant_id: str = Depends(get_tenant_id),
    user: dict = Depends(require_role(["admin", "superadmin"])),
):
    """Delete a person record."""
    ok = PeopleService.delete_person(tenant_id, person_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Person not found")
