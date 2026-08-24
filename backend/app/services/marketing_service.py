"""Marketing Automation & Campaign Engine Service.

Provides:
- Dynamic Audience Segmentation over unified People database
- Multi-Channel Campaigns (Email, SMS, Notifications)
- Recipient resolution, dispatch execution, and communication logging
- Cross-module touchpoint recording on Person timelines
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from app.core.db import supabase
from app.core.demo_data import (
    campaigns_store,
    communication_logs_store,
    invoices_store,
    marketing_segments_store,
    payment_transactions_store,
    people_store,
)
from app.services.crm_service import CrmService
from app.services.event_bus import event_bus


class MarketingService:
    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    # ---------------------------------------------------------------------------
    # Dynamic Audience Segmentation
    # ---------------------------------------------------------------------------
    @staticmethod
    def list_segments(tenant_id: str) -> list[dict[str, Any]]:
        segments = marketing_segments_store.list_all(tenant_id)
        # Update live dynamic member counts
        for seg in segments:
            members = MarketingService.get_segment_members(tenant_id, seg["id"])
            seg["member_count"] = len(members)
        return sorted(segments, key=lambda x: x.get("created_at", ""), reverse=True)

    @staticmethod
    def create_segment(tenant_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        now = MarketingService._now()
        seg_id = f"seg-{str(uuid.uuid4())[:8]}"
        data = {
            "id": seg_id,
            "tenant_id": tenant_id,
            "name": payload["name"],
            "description": payload.get("description"),
            "filter_criteria": payload.get("filter_criteria", {}),
            "is_dynamic": payload.get("is_dynamic", True),
            "member_count": 0,
            "created_at": now,
            "updated_at": now,
        }
        if supabase is None:
            created = marketing_segments_store.create(data, tenant_id)
        else:
            try:
                res = supabase.table("marketing_segments").insert(data).execute()
                created = res.data[0] if res.data else data
            except Exception:
                created = data

        members = MarketingService.get_segment_members(tenant_id, seg_id)
        created["member_count"] = len(members)
        return created

    @staticmethod
    def get_segment_members(tenant_id: str, segment_id: str) -> list[dict[str, Any]]:
        """Dynamically compute matching people for a given segment."""
        seg = marketing_segments_store.get(segment_id, tenant_id)
        if not seg:
            return []

        criteria = seg.get("filter_criteria", {})
        all_people = people_store.list_all(tenant_id)

        # Preload transactions & invoices for financial segment queries
        paid_emails = {
            (t.get("customer_email") or "").lower()
            for t in payment_transactions_store.list_all(tenant_id)
            if t.get("status") == "successful" and t.get("customer_email")
        }

        matched = []
        for p in all_people:
            p_email = (p.get("email") or "").lower()
            p_type = p.get("person_type")
            p_status = p.get("status")
            p_tags = p.get("tags", [])

            # Filter by person_type
            if criteria.get("person_type") and p_type != criteria["person_type"]:
                continue

            # Filter by status
            if criteria.get("status") and p_status != criteria["status"]:
                continue

            # Filter by has_organization
            if criteria.get("has_organization") is True and not p.get("organization_id"):
                continue

            # Filter by tags
            if criteria.get("tag") and criteria["tag"] not in p_tags:
                continue

            # Filter by paid status
            if criteria.get("paid_only") is True and p_email not in paid_emails:
                continue

            if criteria.get("unpaid_only") is True and p_email in paid_emails:
                continue

            matched.append(p)

        return matched

    # ---------------------------------------------------------------------------
    # Campaigns Management & Execution
    # ---------------------------------------------------------------------------
    @staticmethod
    def list_campaigns(tenant_id: str) -> list[dict[str, Any]]:
        return sorted(campaigns_store.list_all(tenant_id), key=lambda x: x.get("created_at", ""), reverse=True)

    @staticmethod
    def create_campaign(tenant_id: str, payload: dict[str, Any], created_by: Optional[str] = None) -> dict[str, Any]:
        now = MarketingService._now()
        camp_id = f"camp-{str(uuid.uuid4())[:8]}"

        segment_id = payload.get("segment_id")
        target_count = 0
        if segment_id:
            target_count = len(MarketingService.get_segment_members(tenant_id, segment_id))

        data = {
            "id": camp_id,
            "tenant_id": tenant_id,
            "name": payload["name"],
            "campaign_type": payload.get("campaign_type") or payload.get("channel", "Email"),
            "channel": payload.get("campaign_type") or payload.get("channel", "Email"),
            "segment_id": segment_id,
            "subject": payload.get("subject") or payload.get("name"),
            "message_body": payload.get("message_body") or payload.get("description", "Campaign announcement"),
            "template_id": payload.get("template_id"),
            "sender": payload.get("sender", "Zacma Marketing <marketing@zacma.com>"),
            "budget": float(payload.get("budget", 0.0)),
            "status": "Draft",
            "scheduled_at": payload.get("scheduled_at") or payload.get("start_date"),
            "sent_at": None,
            "total_recipients": target_count,
            "delivered_count": 0,
            "opened_count": 0,
            "stats": {"target_count": target_count, "clicks": 0, "bounces": 0},
            "created_by": created_by,
            "created_at": now,
            "updated_at": now,
        }

        if supabase is None:
            created = campaigns_store.create(data, tenant_id)
        else:
            try:
                res = supabase.table("campaigns").insert(data).execute()
                created = res.data[0] if res.data else data
            except Exception:
                created = data

        return created

    @staticmethod
    def dispatch_campaign(
        tenant_id: str,
        campaign_id: str,
        target_segment_id: Optional[str] = None,
        custom_recipient_ids: Optional[list[str]] = None,
        actor: str = "marketing_automation",
    ) -> dict[str, Any]:
        """Executes a campaign: generates communication logs and adds timeline events to people."""
        now = MarketingService._now()
        campaign = campaigns_store.get(campaign_id, tenant_id)
        if not campaign:
            raise ValueError("Campaign not found")

        # Determine recipient list
        recipients = []
        seg_id = target_segment_id or campaign.get("segment_id")
        if seg_id:
            recipients = MarketingService.get_segment_members(tenant_id, seg_id)

        if custom_recipient_ids:
            for pid in custom_recipient_ids:
                p = people_store.get(pid, tenant_id)
                if p and p not in recipients:
                    recipients.append(p)

        if not recipients:
            # Fallback to all people if no segment was assigned
            recipients = people_store.list_all(tenant_id)[:10]

        delivered = 0
        channel = campaign.get("campaign_type") or campaign.get("channel", "Email")
        subject = campaign.get("subject") or campaign.get("name")
        message_body = campaign.get("message_body") or campaign.get("description", "Announcement from Zacma.")

        for r in recipients:
            recipient_address = r.get("email") if channel.lower() == "email" else (r.get("phone") or r.get("full_name"))
            if not recipient_address:
                continue

            comm_id = f"comm-{str(uuid.uuid4())[:8]}"
            log_item = {
                "id": comm_id,
                "tenant_id": tenant_id,
                "channel": channel,
                "sender": campaign.get("sender", "Zacma Marketing <marketing@zacma.com>"),
                "recipient": recipient_address,
                "person_id": r["id"],
                "person_name": r.get("full_name"),
                "organization_id": r.get("organization_id"),
                "campaign_id": campaign_id,
                "subject": subject,
                "message_body": message_body,
                "status": "Delivered",
                "created_at": now,
            }
            communication_logs_store.create(log_item, tenant_id)

            # Record touchpoint on Person's CRM timeline
            CrmService.add_timeline_event(
                tenant_id=tenant_id,
                contact_id=r["id"],
                action=f"Campaign Sent ({channel})",
                description=f"Received campaign '{campaign.get('name')}': {subject}",
                actor=actor,
            )
            delivered += 1

        updates = {
            "status": "Sent",
            "sent_at": now,
            "total_recipients": len(recipients),
            "delivered_count": delivered,
            "opened_count": int(delivered * 0.45),
            "stats": {"target_count": len(recipients), "delivered": delivered, "open_rate": "45%", "clicks": int(delivered * 0.15)},
            "updated_at": now,
        }
        campaigns_store.update(campaign_id, updates, tenant_id)

        event_bus.publish(
            tenant_id=tenant_id,
            event_name="campaign.sent",
            payload={"campaign_id": campaign_id, "delivered": delivered, "channel": channel},
        )

        return {
            "campaign_id": campaign_id,
            "status": "Sent",
            "recipients_count": len(recipients),
            "delivered_count": delivered,
            "sent_at": now,
        }

    # ---------------------------------------------------------------------------
    # Communication Logs
    # ---------------------------------------------------------------------------
    @staticmethod
    def list_logs(
        tenant_id: str,
        person_id: Optional[str] = None,
        campaign_id: Optional[str] = None,
        channel: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        logs = communication_logs_store.list_all(tenant_id)
        if person_id:
            logs = [l for l in logs if l.get("person_id") == person_id]
        if campaign_id:
            logs = [l for l in logs if l.get("campaign_id") == campaign_id]
        if channel and channel != "all":
            logs = [l for l in logs if l.get("channel", "").lower() == channel.lower()]
        return sorted(logs, key=lambda x: x.get("created_at", ""), reverse=True)
