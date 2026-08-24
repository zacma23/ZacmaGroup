"""Shared CRM Engine & Sales Pipeline Service.

Provides:
- Unified Contact & Lead synchronization (building upon People layer)
- Configurable Sales Pipeline (New Lead, Contacted, Qualified, Needs Analysis, Proposal, Negotiation, Won, Lost)
- Opportunities & Deals Management with probability and revenue forecasting
- Activities Management (Call, Email, SMS, WhatsApp, Meeting, Task, Note, Follow-up)
- Chronological timeline feeds and customer touchpoint tracking
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from app.core.db import supabase
from app.core.demo_data import (
    crm_activities_store,
    crm_contacts_store,
    crm_opportunities_store,
    leads_store,
    organizations_store,
    people_store,
)
from app.services.event_bus import event_bus
from app.services.people_service import PeopleService


class CrmService:
    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    # ---------------------------------------------------------------------------
    # Contact & Lead Synchronization
    # ---------------------------------------------------------------------------
    @staticmethod
    def sync_contact(
        tenant_id: str,
        full_name: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        address: Optional[str] = None,
        country: str = "Ethiopia",
        source_module: str = "Custom",
        status: str = "Lead",
        tags: Optional[list[str]] = None,
        initial_action: Optional[str] = None,
        linked_entity_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        job_title: Optional[str] = None,
    ) -> dict[str, Any]:
        """Find or create contact in unified People directory & CRM store."""
        tags = tags or [source_module]
        now = CrmService._now()

        # 1. Sync into Central People Directory
        person = PeopleService.find_or_create_person(
            tenant_id=tenant_id,
            full_name=full_name,
            email=email,
            phone=phone,
            organization_id=organization_id,
            job_title=job_title,
            person_type="Customer" if status in {"Active", "Customer"} else "Lead",
            status=status,
            tags=tags,
            address=address,
            country=country,
            source=source_module,
            initial_action=initial_action,
        )

        # 2. Maintain legacy/backward-compatible crm_contacts_store
        all_contacts = crm_contacts_store.list_all(tenant_id)
        existing = None
        for c in all_contacts:
            if (email and c.get("email") == email) or (phone and c.get("phone") == phone) or c.get("id") == person["id"]:
                existing = c
                break

        timeline_event = {
            "id": str(uuid.uuid4()),
            "timestamp": now,
            "action": initial_action or f"{source_module} Registration",
            "description": f"Activity recorded via {source_module} module.",
            "actor": "client",
            "metadata": {"linked_entity_id": linked_entity_id} if linked_entity_id else {},
        }

        if existing:
            current_tags = set(existing.get("tags", []))
            current_tags.update(tags)
            existing_timeline = existing.get("timeline", [])
            existing_timeline.append(timeline_event)
            updates = {
                "tags": list(current_tags),
                "timeline": existing_timeline,
                "person_id": person["id"],
                "updated_at": now,
            }
            if linked_entity_id and linked_entity_id not in existing.get("linked_registration_ids", []):
                updates["linked_registration_ids"] = existing.get("linked_registration_ids", []) + [linked_entity_id]
            crm_contacts_store.update(existing["id"], updates, tenant_id)
            return existing

        new_contact_data = {
            "id": person["id"],
            "tenant_id": tenant_id,
            "person_id": person["id"],
            "full_name": full_name,
            "email": email,
            "phone": phone,
            "address": address,
            "country": country,
            "source_module": source_module,
            "status": status,
            "tags": tags,
            "assigned_admin_id": None,
            "timeline": [timeline_event],
            "notes_list": [],
            "linked_registration_ids": [linked_entity_id] if linked_entity_id else [],
            "linked_invoice_ids": [],
            "linked_ticket_ids": [],
            "created_at": now,
            "updated_at": now,
        }
        created = crm_contacts_store.create(new_contact_data, tenant_id)

        # Also sync to legacy leads_store for backward-compatibility
        leads_store.create({
            "id": person["id"],
            "tenant_id": tenant_id,
            "name": full_name,
            "email": email,
            "company": person.get("organization_name"),
            "phone": phone,
            "source": source_module,
            "status": status.lower(),
            "notes": f"Created via {source_module}",
            "created_at": now,
        }, tenant_id)

        return created

    @staticmethod
    def list_contacts(
        tenant_id: str,
        source_module: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        contacts = crm_contacts_store.list_all(tenant_id)
        if source_module and source_module != "all":
            contacts = [c for c in contacts if c.get("source_module", "").lower() == source_module.lower()]
        if status and status != "all":
            contacts = [c for c in contacts if c.get("status", "").lower() == status.lower()]
        if search:
            s = search.lower()
            contacts = [
                c for c in contacts
                if s in c.get("full_name", "").lower()
                or s in (c.get("email") or "").lower()
                or s in (c.get("phone") or "").lower()
                or any(s in t.lower() for t in c.get("tags", []))
            ]
        return sorted(contacts, key=lambda x: x.get("created_at", ""), reverse=True)

    @staticmethod
    def add_timeline_event(
        tenant_id: str,
        contact_id: str,
        action: str,
        description: str,
        actor: str = "system",
        metadata: Optional[dict[str, Any]] = None,
    ):
        event = {
            "id": str(uuid.uuid4()),
            "timestamp": CrmService._now(),
            "action": action,
            "description": description,
            "actor": actor,
            "metadata": metadata or {},
        }
        contact = crm_contacts_store.get(contact_id, tenant_id)
        if contact:
            timeline = contact.get("timeline", [])
            timeline.append(event)
            crm_contacts_store.update(contact_id, {"timeline": timeline, "updated_at": CrmService._now()}, tenant_id)

    @staticmethod
    def add_note(tenant_id: str, contact_id: str, author_email: str, content: str) -> dict[str, Any]:
        note = {
            "id": str(uuid.uuid4()),
            "author": author_email,
            "content": content,
            "created_at": CrmService._now(),
        }
        contact = crm_contacts_store.get(contact_id, tenant_id)
        if contact:
            notes = contact.get("notes_list", [])
            notes.append(note)
            crm_contacts_store.update(contact_id, {"notes_list": notes, "updated_at": CrmService._now()}, tenant_id)
        return note

    # ---------------------------------------------------------------------------
    # Sales Pipeline & Opportunities / Deals
    # ---------------------------------------------------------------------------
    @staticmethod
    def create_opportunity(tenant_id: str, payload: dict[str, Any], actor: str = "admin") -> dict[str, Any]:
        now = CrmService._now()
        opp_id = f"opp-{str(uuid.uuid4())[:8]}"

        # Resolve person and organization names
        person_name = None
        if payload.get("person_id"):
            p = people_store.get(payload["person_id"], tenant_id)
            if p:
                person_name = p.get("full_name")

        org_name = None
        if payload.get("organization_id"):
            o = organizations_store.get(payload["organization_id"], tenant_id)
            if o:
                org_name = o.get("name")

        data = {
            "id": opp_id,
            "tenant_id": tenant_id,
            "title": payload.get("title"),
            "person_id": payload.get("person_id"),
            "person_name": person_name,
            "organization_id": payload.get("organization_id"),
            "organization_name": org_name,
            "value": float(payload.get("value", 0.0)),
            "currency": payload.get("currency", "ETB"),
            "pipeline_stage": payload.get("pipeline_stage", "New Lead"),
            "probability": int(payload.get("probability", 20)),
            "expected_close_date": payload.get("expected_close_date"),
            "owner_id": payload.get("owner_id") or actor,
            "source": payload.get("source", "Direct"),
            "notes": payload.get("notes"),
            "status": "Won" if payload.get("pipeline_stage") == "Won" else ("Lost" if payload.get("pipeline_stage") == "Lost" else "Open"),
            "created_at": now,
            "updated_at": now,
        }

        if supabase is None:
            created = crm_opportunities_store.create(data, tenant_id)
        else:
            try:
                res = supabase.table("crm_opportunities").insert(data).execute()
                created = res.data[0] if res.data else data
            except Exception:
                created = data

        if payload.get("person_id"):
            CrmService.add_timeline_event(
                tenant_id=tenant_id,
                contact_id=payload["person_id"],
                action="Opportunity Created",
                description=f"Created deal '{data['title']}' for {data['value']:,.2f} {data['currency']} (Stage: {data['pipeline_stage']})",
                actor=actor,
            )

        event_bus.publish(
            tenant_id=tenant_id,
            event_name="lead.created",
            payload={"opportunity_id": opp_id, "title": data["title"], "value": data["value"]},
        )
        return created

    @staticmethod
    def update_opportunity(tenant_id: str, opportunity_id: str, updates: dict[str, Any], actor: str = "admin") -> Optional[dict[str, Any]]:
        updates["updated_at"] = CrmService._now()
        if "pipeline_stage" in updates:
            stage = updates["pipeline_stage"]
            if stage == "Won":
                updates["status"] = "Won"
                updates["probability"] = 100
            elif stage == "Lost":
                updates["status"] = "Lost"
                updates["probability"] = 0

        if supabase is None:
            updated = crm_opportunities_store.update(opportunity_id, updates, tenant_id)
        else:
            try:
                res = supabase.table("crm_opportunities").update(updates).eq("id", opportunity_id).eq("tenant_id", tenant_id).execute()
                updated = res.data[0] if res.data else updates
            except Exception:
                updated = updates

        if updated and updated.get("person_id"):
            CrmService.add_timeline_event(
                tenant_id=tenant_id,
                contact_id=updated["person_id"],
                action="Opportunity Stage Updated",
                description=f"Deal '{updated.get('title')}' moved to stage: {updated.get('pipeline_stage')}",
                actor=actor,
            )
            event_bus.publish(
                tenant_id=tenant_id,
                event_name="lead.updated",
                payload={"opportunity_id": opportunity_id, "stage": updated.get("pipeline_stage")},
            )
        return updated

    @staticmethod
    def list_opportunities(
        tenant_id: str,
        stage: Optional[str] = None,
        status: Optional[str] = None,
        person_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        search: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        opps = crm_opportunities_store.list_all(tenant_id)
        if stage and stage != "all":
            opps = [o for o in opps if o.get("pipeline_stage", "").lower() == stage.lower()]
        if status and status != "all":
            opps = [o for o in opps if o.get("status", "").lower() == status.lower()]
        if person_id:
            opps = [o for o in opps if o.get("person_id") == person_id]
        if organization_id:
            opps = [o for o in opps if o.get("organization_id") == organization_id]
        if search:
            s = search.lower()
            opps = [
                o for o in opps
                if s in o.get("title", "").lower()
                or s in (o.get("person_name") or "").lower()
                or s in (o.get("organization_name") or "").lower()
                or s in (o.get("source") or "").lower()
            ]
        return sorted(opps, key=lambda x: x.get("created_at", ""), reverse=True)

    @staticmethod
    def get_pipeline_summary(tenant_id: str) -> dict[str, Any]:
        """Aggregate pipeline value and counts by stage."""
        opps = crm_opportunities_store.list_all(tenant_id)
        stages = ["New Lead", "Contacted", "Qualified", "Needs Analysis", "Proposal", "Negotiation", "Won", "Lost"]
        stage_summary = []
        total_pipeline_value = 0.0
        weighted_pipeline_value = 0.0

        for st in stages:
            stage_opps = [o for o in opps if o.get("pipeline_stage") == st]
            stage_val = sum(o.get("value", 0.0) for o in stage_opps)
            stage_weighted = sum(o.get("value", 0.0) * (o.get("probability", 0) / 100.0) for o in stage_opps)
            if st != "Lost":
                total_pipeline_value += stage_val
                weighted_pipeline_value += stage_weighted

            stage_summary.append({
                "stage": st,
                "count": len(stage_opps),
                "total_value": round(stage_val, 2),
                "weighted_value": round(stage_weighted, 2),
                "opportunities": stage_opps,
            })

        return {
            "total_opportunities": len(opps),
            "total_pipeline_value": round(total_pipeline_value, 2),
            "weighted_pipeline_value": round(weighted_pipeline_value, 2),
            "currency": "ETB",
            "stages": stage_summary,
        }

    # ---------------------------------------------------------------------------
    # CRM Activities & Tasks
    # ---------------------------------------------------------------------------
    @staticmethod
    def create_activity(tenant_id: str, payload: dict[str, Any], actor: str = "admin") -> dict[str, Any]:
        now = CrmService._now()
        act_id = f"act-{str(uuid.uuid4())[:8]}"

        person_name = None
        if payload.get("person_id"):
            p = people_store.get(payload["person_id"], tenant_id)
            if p:
                person_name = p.get("full_name")

        data = {
            "id": act_id,
            "tenant_id": tenant_id,
            "activity_type": payload.get("activity_type", "Note"),
            "subject": payload.get("subject"),
            "description": payload.get("description"),
            "person_id": payload.get("person_id"),
            "person_name": person_name,
            "organization_id": payload.get("organization_id"),
            "opportunity_id": payload.get("opportunity_id"),
            "due_date": payload.get("due_date"),
            "completed_at": payload.get("completed_at"),
            "status": "Completed" if payload.get("completed_at") else "Pending",
            "actor": actor,
            "created_at": now,
            "updated_at": now,
        }

        if supabase is None:
            created = crm_activities_store.create(data, tenant_id)
        else:
            try:
                res = supabase.table("crm_activities").insert(data).execute()
                created = res.data[0] if res.data else data
            except Exception:
                created = data

        if payload.get("person_id"):
            CrmService.add_timeline_event(
                tenant_id=tenant_id,
                contact_id=payload["person_id"],
                action=f"Activity: {data['activity_type']}",
                description=f"{data['subject']}: {data.get('description', '')}",
                actor=actor,
            )

        event_bus.publish(
            tenant_id=tenant_id,
            event_name="activity.created",
            payload={"activity_id": act_id, "type": data["activity_type"], "person_id": payload.get("person_id")},
        )
        return created

    @staticmethod
    def list_activities(
        tenant_id: str,
        activity_type: Optional[str] = None,
        status: Optional[str] = None,
        person_id: Optional[str] = None,
        opportunity_id: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        acts = crm_activities_store.list_all(tenant_id)
        if activity_type and activity_type != "all":
            acts = [a for a in acts if a.get("activity_type", "").lower() == activity_type.lower()]
        if status and status != "all":
            acts = [a for a in acts if a.get("status", "").lower() == status.lower()]
        if person_id:
            acts = [a for a in acts if a.get("person_id") == person_id]
        if opportunity_id:
            acts = [a for a in acts if a.get("opportunity_id") == opportunity_id]
        return sorted(acts, key=lambda x: (x.get("due_date") or x.get("created_at", "")), reverse=True)

    @staticmethod
    def update_activity(tenant_id: str, activity_id: str, updates: dict[str, Any]) -> Optional[dict[str, Any]]:
        updates["updated_at"] = CrmService._now()
        if updates.get("status") == "Completed" and not updates.get("completed_at"):
            updates["completed_at"] = CrmService._now()

        if supabase is None:
            return crm_activities_store.update(activity_id, updates, tenant_id)
        try:
            res = supabase.table("crm_activities").update(updates).eq("id", activity_id).eq("tenant_id", tenant_id).execute()
            return res.data[0] if res.data else updates
        except Exception:
            return updates
