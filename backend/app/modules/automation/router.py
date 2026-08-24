"""Automation & Workflow Integration Router.

Provides API endpoints for job management, manual retry triggers,
asynchronous external webhook callbacks (e.g. n8n), and audit inspections.
"""

import hashlib
import hmac
import json
from typing import Optional
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status

from app.core.config import settings
from app.core.permissions import require_role
from app.core.tenancy import get_tenant_id
from app.models import (
    AutomationCallbackPayload,
    AutomationJobCreate,
    AutomationJobResponse,
    AutomationWebhookPayload,
)
from app.services.automation_service import AutomationService

router = APIRouter(prefix="/automation", tags=["automation"])


# ---------------------------------------------------------------------------
# Job Management Endpoints (Admin & Staff)
# ---------------------------------------------------------------------------

@router.get("/jobs", response_model=list[AutomationJobResponse])
def list_automation_jobs(
    status_filter: Optional[str] = None,
    entity_type: Optional[str] = None,
    tenant_id: str = Depends(get_tenant_id),
    user: dict = Depends(require_role(["admin", "staff", "manager"])),
):
    """List all background automation jobs for the current tenant."""
    return AutomationService.list_jobs(tenant_id, status_filter=status_filter, entity_type=entity_type)


@router.get("/jobs/{job_id}", response_model=AutomationJobResponse)
def get_automation_job(
    job_id: str,
    tenant_id: str = Depends(get_tenant_id),
    user: dict = Depends(require_role(["admin", "staff", "manager"])),
):
    """Get single automation job details and execution status."""
    job = AutomationService.get_job(tenant_id, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Automation job not found")
    return job


@router.post("/jobs", response_model=AutomationJobResponse, status_code=status.HTTP_201_CREATED)
def create_automation_job(
    payload: AutomationJobCreate,
    tenant_id: str = Depends(get_tenant_id),
    user: dict = Depends(require_role(["admin", "staff"])),
):
    """Manually create and dispatch an automation job."""
    job = AutomationService.create_job(
        tenant_id=tenant_id,
        job_type=payload.job_type,
        entity_type=payload.entity_type,
        entity_id=payload.entity_id,
        payload=payload.payload,
        webhook_url=payload.webhook_url,
        max_retries=payload.max_retries,
    )
    return AutomationService.execute_job(tenant_id, job["id"])


@router.post("/jobs/{job_id}/retry", response_model=AutomationJobResponse)
def retry_automation_job(
    job_id: str,
    tenant_id: str = Depends(get_tenant_id),
    user: dict = Depends(require_role(["admin", "staff"])),
):
    """Manually trigger retry for a failed or stuck automation job."""
    try:
        return AutomationService.retry_job(tenant_id, job_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/jobs/{job_id}/cancel", response_model=AutomationJobResponse)
def cancel_automation_job(
    job_id: str,
    tenant_id: str = Depends(get_tenant_id),
    user: dict = Depends(require_role(["admin", "staff"])),
):
    """Cancel an active or queued automation job."""
    try:
        return AutomationService.cancel_job(tenant_id, job_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ---------------------------------------------------------------------------
# Asynchronous Callbacks & Webhook Receivers
# ---------------------------------------------------------------------------

@router.post("/callbacks/{job_id}")
async def handle_automation_callback(
    job_id: str,
    request: Request,
    payload: AutomationCallbackPayload,
    x_automation_signature: Optional[str] = Header(None),
    tenant_id: str = Depends(get_tenant_id),
):
    """Asynchronous callback receiver for n8n or external integration workers."""
    if x_automation_signature:
        raw_body = await request.body()
        secret = getattr(settings, "automation_webhook_secret", "zacma_automation_secret_key")
        expected_sig = hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(x_automation_signature, expected_sig):
            # Also allow fallback check against JSON serialized payload
            body_bytes = json.dumps(payload.model_dump(exclude_none=True), sort_keys=True).encode("utf-8")
            alt_sig = hmac.new(secret.encode("utf-8"), body_bytes, hashlib.sha256).hexdigest()
            if not hmac.compare_digest(x_automation_signature, alt_sig):
                raise HTTPException(status_code=400, detail="Invalid callback HMAC signature")

    try:
        updated_job = AutomationService.process_callback(
            tenant_id=tenant_id,
            job_id=job_id,
            callback_data=payload.model_dump(exclude_none=True),
        )
        return {
            "status": "success",
            "message": f"Callback processed for job {job_id}",
            "job_status": updated_job.get("status"),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/webhooks")
async def handle_generic_automation_webhook(
    payload: AutomationWebhookPayload,
    x_automation_signature: Optional[str] = Header(None),
    tenant_id: str = Depends(get_tenant_id),
):
    """Generic incoming automation webhook receiver."""
    event = payload.event
    data = payload.data
    logger = None

    if payload.job_id:
        try:
            return AutomationService.process_callback(
                tenant_id=tenant_id,
                job_id=payload.job_id,
                callback_data={
                    "status": "completed" if "success" in event.lower() or "completed" in event.lower() else "failed",
                    "result_data": data,
                },
                signature=x_automation_signature,
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    return {
        "status": "received",
        "event": event,
        "tenant_id": tenant_id,
    }
