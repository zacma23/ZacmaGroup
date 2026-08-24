"""Marketing Automation & Dynamic Audience Campaign Router."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.demo_data import campaigns_store
from app.core.tenancy import get_tenant_id
from app.models import (
    CampaignCreate,
    CampaignResponse,
    CampaignUpdate,
    CommunicationLogResponse,
    MarketingCampaignDispatch,
    MarketingSegmentCreate,
    MarketingSegmentResponse,
    PersonResponse,
)
from app.services.marketing_service import MarketingService

router = APIRouter(prefix="/marketing", tags=["marketing"])


# ---------------------------------------------------------------------------
# Segments & Dynamic Audiences
# ---------------------------------------------------------------------------

@router.get("/segments", response_model=list[MarketingSegmentResponse])
def list_segments(tenant_id: str = Depends(get_tenant_id)):
    """List all dynamic marketing audiences and target segments."""
    return MarketingService.list_segments(tenant_id)


@router.post("/segments", response_model=MarketingSegmentResponse, status_code=status.HTTP_201_CREATED)
def create_segment(payload: MarketingSegmentCreate, tenant_id: str = Depends(get_tenant_id)):
    """Create a new dynamic audience segment."""
    return MarketingService.create_segment(tenant_id, payload.model_dump())


@router.get("/segments/{segment_id}/members", response_model=list[PersonResponse])
def get_segment_members(segment_id: str, tenant_id: str = Depends(get_tenant_id)):
    """Compute and retrieve all current matching people for a dynamic segment."""
    return MarketingService.get_segment_members(tenant_id, segment_id)


# ---------------------------------------------------------------------------
# Campaigns
# ---------------------------------------------------------------------------

@router.get("/campaigns")
def list_campaigns(tenant_id: str = Depends(get_tenant_id)):
    """List all marketing campaigns with statistics."""
    return MarketingService.list_campaigns(tenant_id)


@router.post("/campaigns", status_code=status.HTTP_201_CREATED)
def create_campaign(payload: CampaignCreate, tenant_id: str = Depends(get_tenant_id)):
    """Create a new marketing campaign."""
    return MarketingService.create_campaign(tenant_id, payload.model_dump())


@router.get("/campaigns/{campaign_id}")
def get_campaign(campaign_id: str, tenant_id: str = Depends(get_tenant_id)):
    """Get single campaign details."""
    camp = campaigns_store.get(campaign_id, tenant_id)
    if not camp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")
    return camp


@router.put("/campaigns/{campaign_id}")
def update_campaign(campaign_id: str, payload: CampaignUpdate, tenant_id: str = Depends(get_tenant_id)):
    """Update campaign information."""
    updated = campaigns_store.update(campaign_id, payload.model_dump(exclude_unset=True), tenant_id)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")
    return updated


@router.delete("/campaigns/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_campaign(campaign_id: str, tenant_id: str = Depends(get_tenant_id)):
    """Delete a campaign."""
    ok = campaigns_store.delete(campaign_id, tenant_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")


@router.post("/campaigns/{campaign_id}/dispatch")
def dispatch_campaign(
    campaign_id: str,
    payload: MarketingCampaignDispatch | None = None,
    tenant_id: str = Depends(get_tenant_id),
):
    """Execute and dispatch campaign to target dynamic segment or custom recipient list."""
    target_seg_id = payload.target_segment_id if payload else None
    custom_ids = payload.custom_recipient_person_ids if payload else None
    try:
        return MarketingService.dispatch_campaign(
            tenant_id=tenant_id,
            campaign_id=campaign_id,
            target_segment_id=target_seg_id,
            custom_recipient_ids=custom_ids,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


# ---------------------------------------------------------------------------
# Communication Logs
# ---------------------------------------------------------------------------

@router.get("/logs", response_model=list[CommunicationLogResponse])
def list_logs(
    person_id: str | None = None,
    campaign_id: str | None = None,
    channel: str | None = None,
    tenant_id: str = Depends(get_tenant_id),
):
    """List sent communication logs across all channels."""
    return MarketingService.list_logs(tenant_id, person_id=person_id, campaign_id=campaign_id, channel=channel)
