"""Shared Approval Workflow Engine Service.

A generic state machine used across all modules:
Status: Pending -> UnderReview -> Approved / Denied -> Completed / Cancelled
(or DocumentsRequested for visa/support workflows)

Triggers automatic client notification emails and logs every transition to the
CRM activity timeline.
"""

from typing import Any, Optional

from app.core.demo_data import (
    students_store,
    visa_applications_store,
    travel_requests_store,
    module_submissions_store,
)
from app.services.crm_service import CrmService
from app.services.notification_service import NotificationService


class ApprovalService:
    @staticmethod
    def _get_store_for_entity(entity_type: str):
        mapping = {
            "student": students_store,
            "students": students_store,
            "visa": visa_applications_store,
            "travel": travel_requests_store,
            "submission": module_submissions_store,
            "submissions": module_submissions_store,
        }
        return mapping.get(entity_type.lower())

    @staticmethod
    def submit(tenant_id: str, entity_type: str, entity_id: str) -> dict[str, Any] | None:
        """Move entity into UnderReview state."""
        store = ApprovalService._get_store_for_entity(entity_type)
        if not store:
            return None
        return store.update(entity_id, {"status": "UnderReview"}, tenant_id)

    @staticmethod
    def approve(
        tenant_id: str,
        entity_type: str,
        entity_id: str,
        admin_id: str,
        comment: Optional[str] = "Approved by admin",
    ) -> dict[str, Any] | None:
        """Approve an application or submission, notify client, and log to CRM."""
        store = ApprovalService._get_store_for_entity(entity_type)
        if not store:
            return None

        updated = store.update(entity_id, {"status": "Approved", "approved_by": admin_id}, tenant_id)
        if not updated:
            return None

        contact_id = updated.get("linked_crm_contact_id")
        full_name = updated.get("full_name") or updated.get("applicant_name") or "Client"
        item_title = updated.get("course") or updated.get("destination_country") or updated.get("module_key") or entity_type

        # Log timeline
        if contact_id:
            CrmService.add_timeline_event(
                tenant_id=tenant_id,
                contact_id=contact_id,
                action="Application Approved",
                description=f"{entity_type.capitalize()} ({item_title}) approved by {admin_id}. Note: {comment}",
                actor=admin_id,
            )

        # Notify
        email = updated.get("email")
        if email:
            NotificationService.send_email(
                to_email=email,
                template_key="registration_approved",
                model={
                    "full_name": full_name,
                    "module_type": entity_type.capitalize(),
                    "item_title": item_title,
                    "comment": comment or "All requirements met.",
                },
                tenant_id=tenant_id,
            )

        return updated

    @staticmethod
    def deny(
        tenant_id: str,
        entity_type: str,
        entity_id: str,
        admin_id: str,
        reason: str,
    ) -> dict[str, Any] | None:
        """Deny an application with reason, notify client, and log to CRM."""
        store = ApprovalService._get_store_for_entity(entity_type)
        if not store:
            return None

        updated = store.update(entity_id, {"status": "Denied", "denial_reason": reason, "denied_by": admin_id}, tenant_id)
        if not updated:
            return None

        contact_id = updated.get("linked_crm_contact_id")
        item_title = updated.get("course") or updated.get("destination_country") or entity_type

        if contact_id:
            CrmService.add_timeline_event(
                tenant_id=tenant_id,
                contact_id=contact_id,
                action="Application Denied",
                description=f"{entity_type.capitalize()} ({item_title}) denied by {admin_id}. Reason: {reason}",
                actor=admin_id,
            )

        return updated

    @staticmethod
    def request_more_info(
        tenant_id: str,
        entity_type: str,
        entity_id: str,
        admin_id: str,
        message: str,
        requested_docs: Optional[list[str]] = None,
    ) -> dict[str, Any] | None:
        """Request additional documents or information from client."""
        store = ApprovalService._get_store_for_entity(entity_type)
        if not store:
            return None

        updates = {
            "status": "DocumentsRequested",
            "info_request_message": message,
            "requested_documents": requested_docs or [],
        }
        updated = store.update(entity_id, updates, tenant_id)
        if not updated:
            return None

        contact_id = updated.get("linked_crm_contact_id")
        if contact_id:
            CrmService.add_timeline_event(
                tenant_id=tenant_id,
                contact_id=contact_id,
                action="Information / Documents Requested",
                description=f"{admin_id} requested additional details: {message}",
                actor=admin_id,
            )

        return updated
