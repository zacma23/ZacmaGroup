"""Automation & Integration Engine Service.

Orchestrates asynchronous business process automation, webhook dispatch,
integration with external workflow platforms (e.g. n8n, Zapier, custom workers),
exponential backoff retry management, and automated service fulfillment.
"""

import hashlib
import hmac
import json
import logging
from datetime import datetime, timezone
from typing import Any, Optional
import uuid

import httpx

from app.core.config import settings
from app.core.demo_data import (
    automation_jobs_store,
    module_submissions_store,
    software_projects_store,
    students_store,
    travel_requests_store,
    visa_applications_store,
)
from app.services.crm_service import CrmService
from app.services.notification_service import NotificationService
from app.services.telegram_bot_service import TelegramPaymentBotService

logger = logging.getLogger("zacma.automation")


class AutomationService:
    """Enterprise Automation & Webhook Integration Service."""

    @staticmethod
    def _find_entity_store_and_item(tenant_id: str, entity_type: str, entity_id: str):
        """Find entity record and its corresponding store."""
        mapping = {
            "software": software_projects_store,
            "software_projects": software_projects_store,
            "visa": visa_applications_store,
            "visas": visa_applications_store,
            "visa_applications": visa_applications_store,
            "student": students_store,
            "students": students_store,
            "travel": travel_requests_store,
            "travels": travel_requests_store,
            "travel_requests": travel_requests_store,
            "custom": module_submissions_store,
            "submissions": module_submissions_store,
        }
        store = mapping.get(entity_type.lower())
        if not store:
            return None, None
        
        # Check by id or reference_code
        item = store.get(entity_id, tenant_id)
        if not item:
            for it in store.list_all(tenant_id):
                if (it.get("reference_code") or "").lower() == entity_id.lower() or it.get("id") == entity_id:
                    return store, it
        return store, item

    @staticmethod
    def create_job(
        tenant_id: str,
        job_type: str,
        entity_type: str,
        entity_id: str,
        payload: dict[str, Any],
        webhook_url: Optional[str] = None,
        max_retries: int = 3,
    ) -> dict[str, Any]:
        """Create a new automation job and register it into the pipeline."""
        now = datetime.now(timezone.utc).isoformat()
        job_id = f"job-{uuid.uuid4().hex[:12]}"
        
        job_record = {
            "id": job_id,
            "tenant_id": tenant_id,
            "job_type": job_type,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "status": "pending",
            "retry_count": 0,
            "max_retries": max_retries,
            "payload": payload,
            "result_data": None,
            "error_message": None,
            "webhook_url": webhook_url or getattr(settings, "automation_webhook_url", None),
            "created_at": now,
            "updated_at": now,
            "completed_at": None,
        }

        created = automation_jobs_store.create(job_record, tenant_id)
        logger.info("AutomationJob created: %s [%s] for %s/%s", job_id, job_type, entity_type, entity_id)
        return created

    @staticmethod
    def execute_job(tenant_id: str, job_id: str) -> dict[str, Any]:
        """Execute an automation job with retry and webhook dispatch."""
        job = automation_jobs_store.get(job_id, tenant_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")

        now = datetime.now(timezone.utc).isoformat()
        job["status"] = "processing"
        job["updated_at"] = now
        automation_jobs_store.update(job_id, job, tenant_id)

        webhook_url = job.get("webhook_url")
        payload = job.get("payload", {})
        entity_type = job.get("entity_type")
        entity_id = job.get("entity_id")

        # 1. Google Cloud Workflows Driver
        try:
            from app.services.gcp_workflows_driver import GoogleWorkflowsDriver
            if GoogleWorkflowsDriver.is_configured():
                GoogleWorkflowsDriver.execute_workflow(
                    workflow_name="service_fulfillment",
                    execution_input={
                        "job_id": job_id,
                        "entity_type": entity_type,
                        "entity_id": entity_id,
                        "payload": payload,
                    },
                )
        except Exception as wf_err:
            logger.debug("Google Workflows execution notice for job %s: %s", job_id, wf_err)

        # 2. External Webhook / n8n Dispatch (if URL is configured)
        if webhook_url and webhook_url.startswith("http"):
            try:
                secret = getattr(settings, "automation_webhook_secret", "zacma_automation_secret_key")
                body_bytes = json.dumps(payload, sort_keys=True).encode("utf-8")
                sig = hmac.new(secret.encode("utf-8"), body_bytes, hashlib.sha256).hexdigest()

                headers = {
                    "Content-Type": "application/json",
                    "X-Automation-Signature": sig,
                    "X-Job-ID": job_id,
                    "X-Entity-Type": entity_type,
                    "X-Entity-ID": entity_id,
                }

                with httpx.Client(timeout=10.0) as client:
                    resp = client.post(webhook_url, json=payload, headers=headers)
                    if resp.status_code >= 400:
                        raise RuntimeError(f"External webhook returned status {resp.status_code}: {resp.text[:200]}")

                logger.info("External automation webhook dispatched successfully to %s", webhook_url)
            except Exception as exc:
                logger.warning("Automation webhook execution failed for job %s: %s", job_id, exc)
                return AutomationService._handle_job_failure(tenant_id, job, str(exc))

        # 2. Complete Job & Activate Service
        return AutomationService._complete_job_fulfillment(tenant_id, job)

    @staticmethod
    def _handle_job_failure(tenant_id: str, job: dict[str, Any], error_msg: str) -> dict[str, Any]:
        """Process job failure with retry backoff check."""
        job_id = job["id"]
        retries = job.get("retry_count", 0) + 1
        max_retries = job.get("max_retries", 3)
        now = datetime.now(timezone.utc).isoformat()

        job["retry_count"] = retries
        job["error_message"] = error_msg
        job["updated_at"] = now

        if retries <= max_retries:
            job["status"] = "retry"
            logger.info("Job %s marked for retry (%d/%d)", job_id, retries, max_retries)
        else:
            job["status"] = "failed"
            logger.error("Job %s permanently failed after %d retries. Error: %s", job_id, retries, error_msg)

        automation_jobs_store.update(job_id, job, tenant_id)
        return job

    @staticmethod
    def _complete_job_fulfillment(tenant_id: str, job: dict[str, Any], result_data: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """Finalize job success, activate service status, log CRM timeline, and notify customer."""
        job_id = job["id"]
        now = datetime.now(timezone.utc).isoformat()
        entity_type = job.get("entity_type", "")
        entity_id = job.get("entity_id", "")
        payload = job.get("payload", {})

        job["status"] = "completed"
        job["completed_at"] = now
        job["updated_at"] = now
        job["result_data"] = result_data or {
            "fulfillment_status": "active",
            "activated_at": now,
            "automated_pipeline": "executed",
        }
        automation_jobs_store.update(job_id, job, tenant_id)

        # 3. Update target application/entity
        store, item = AutomationService._find_entity_store_and_item(tenant_id, entity_type, entity_id)
        if store and item:
            store.update(
                item["id"],
                {
                    "status": "Active" if entity_type == "student" else "ServiceDelivered",
                    "payment_status": "Paid",
                    "service_activated_at": now,
                    "linked_automation_job_id": job_id,
                },
                tenant_id,
            )

            contact_id = item.get("linked_crm_contact_id")
            client_name = item.get("full_name") or item.get("client_name") or payload.get("customer_name") or "Valued Client"
            email = item.get("email") or item.get("customer_email") or payload.get("customer_email")
            item_title = item.get("course") or item.get("project_name") or item.get("destination_country") or entity_type

            # 4. Log CRM timeline
            if contact_id:
                CrmService.add_timeline_event(
                    tenant_id=tenant_id,
                    contact_id=contact_id,
                    action="Service Activated & Automation Completed",
                    description=f"Automated fulfillment completed for {item_title}. Status is now Active/Delivered.",
                    actor="automation_service",
                )

            # 5. Dispatch notification
            if email:
                try:
                    NotificationService.send_email(
                        to_email=email,
                        template_key="service_activated",
                        model={
                            "full_name": client_name,
                            "service_title": item_title,
                            "job_id": job_id,
                            "activation_time": now,
                        },
                        tenant_id=tenant_id,
                    )
                except Exception as e:
                    logger.warning("Could not dispatch activation email to %s: %s", email, e)

            # 6. Telegram notification
            try:
                ref_code = item.get("reference_code") or entity_id
                TelegramPaymentBotService.send_transaction_notification(
                    public_reference=ref_code,
                    amount=item.get("tuition_amount") or item.get("advance_amount") or payload.get("amount", 0.0),
                    currency=item.get("currency") or "ETB",
                    customer_name=client_name,
                    purpose=f"Service Activated: {item_title}",
                    status="active",
                )
            except Exception as e:
                logger.warning("Telegram notification notice: %s", e)

        logger.info("Job %s completed successfully and service activated for %s/%s", job_id, entity_type, entity_id)
        return job

    @staticmethod
    def process_callback(
        tenant_id: str,
        job_id: str,
        callback_data: dict[str, Any],
        signature: Optional[str] = None,
    ) -> dict[str, Any]:
        """Process incoming asynchronous callback from n8n or external automation system."""
        job = automation_jobs_store.get(job_id, tenant_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")

        # Validate signature if provided
        secret = getattr(settings, "automation_webhook_secret", "zacma_automation_secret_key")
        if signature:
            body_bytes = json.dumps(callback_data, sort_keys=True).encode("utf-8")
            expected_sig = hmac.new(secret.encode("utf-8"), body_bytes, hashlib.sha256).hexdigest()
            if not hmac.compare_digest(signature, expected_sig):
                raise ValueError("Invalid callback HMAC signature")

        cb_status = callback_data.get("status", "completed").lower()
        if cb_status == "completed":
            return AutomationService._complete_job_fulfillment(tenant_id, job, callback_data.get("result_data"))
        else:
            return AutomationService._handle_job_failure(tenant_id, job, callback_data.get("error_message", "Callback reported failure"))

    @staticmethod
    def retry_job(tenant_id: str, job_id: str) -> dict[str, Any]:
        """Manually trigger retry for a failed or retry job."""
        job = automation_jobs_store.get(job_id, tenant_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")

        job["status"] = "pending"
        automation_jobs_store.update(job_id, job, tenant_id)
        return AutomationService.execute_job(tenant_id, job_id)

    @staticmethod
    def cancel_job(tenant_id: str, job_id: str) -> dict[str, Any]:
        """Cancel an automation job."""
        job = automation_jobs_store.get(job_id, tenant_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")

        job["status"] = "cancelled"
        job["updated_at"] = datetime.now(timezone.utc).isoformat()
        automation_jobs_store.update(job_id, job, tenant_id)
        return job

    @staticmethod
    def list_jobs(
        tenant_id: str,
        status_filter: Optional[str] = None,
        entity_type: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """List all automation jobs for the tenant with optional filtering."""
        jobs = automation_jobs_store.list_all(tenant_id)
        if status_filter:
            jobs = [j for j in jobs if j.get("status", "").lower() == status_filter.lower()]
        if entity_type:
            jobs = [j for j in jobs if j.get("entity_type", "").lower() == entity_type.lower()]
        jobs.sort(key=lambda j: j.get("created_at", ""), reverse=True)
        return jobs

    @staticmethod
    def get_job(tenant_id: str, job_id: str) -> Optional[dict[str, Any]]:
        """Get single automation job details."""
        return automation_jobs_store.get(job_id, tenant_id)
