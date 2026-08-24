"""Unified People & Organization Central Directory Service.

Provides:
- Deduplication and identity matching (by email and phone)
- Person lifecycle management (Individuals, Customers, Leads, Students, Staff, Partners, Vendors)
- Organization / Business management and employee hierarchy
- 360-degree unified profile aggregation (CRM deals, activities, student courses, payment history, marketing logs, timeline)
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from app.core.db import supabase
from app.core.demo_data import (
    communication_logs_store,
    crm_activities_store,
    crm_contacts_store,
    crm_opportunities_store,
    invoices_store,
    organizations_store,
    payment_transactions_store,
    people_store,
    software_projects_store,
    students_store,
    support_tickets_store,
    travel_requests_store,
    visa_applications_store,
)
from app.services.event_bus import event_bus


class PeopleService:
    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    # ---------------------------------------------------------------------------
    # Deduplication & Person Matching
    # ---------------------------------------------------------------------------
    @staticmethod
    def find_or_create_person(
        tenant_id: str,
        full_name: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        alt_phone: Optional[str] = None,
        organization_id: Optional[str] = None,
        job_title: Optional[str] = None,
        person_type: str = "Individual",
        status: str = "Active",
        tags: Optional[list[str]] = None,
        address: Optional[str] = None,
        city: Optional[str] = None,
        country: str = "Ethiopia",
        source: str = "Direct",
        notes: Optional[str] = None,
        initial_action: Optional[str] = None,
    ) -> dict[str, Any]:
        """Find an existing person by email or phone, or create a new person without duplicates."""
        now = PeopleService._now()
        tags = tags or []
        email_clean = email.strip().lower() if email and email.strip() else None
        phone_clean = phone.strip() if phone and phone.strip() else None

        # 1. Search existing in memory or database
        all_people = people_store.list_all(tenant_id)

        existing = None
        for p in all_people:
            p_email = (p.get("email") or "").strip().lower()
            p_phone = (p.get("phone") or "").strip()
            if (email_clean and p_email and email_clean == p_email) or (phone_clean and p_phone and phone_clean == p_phone):
                existing = p
                break

        if existing:
            # Update tags, organization, or job title if newly provided
            updates = {"updated_at": now}
            merged_tags = list(set(existing.get("tags", []) + tags))
            if merged_tags != existing.get("tags", []):
                updates["tags"] = merged_tags
            if organization_id and not existing.get("organization_id"):
                updates["organization_id"] = organization_id
            if job_title and not existing.get("job_title"):
                updates["job_title"] = job_title
            if phone_clean and not existing.get("phone"):
                updates["phone"] = phone_clean
            if address and not existing.get("address"):
                updates["address"] = address

            # Upgrade person_type if becoming a Customer or Student
            if person_type in {"Customer", "Student"} and existing.get("person_type") in {"Individual", "Lead"}:
                updates["person_type"] = person_type

            updated = people_store.update(existing["id"], updates, tenant_id)
            if supabase is not None:
                try:
                    res = supabase.table("people").update(updates).eq("id", existing["id"]).eq("tenant_id", tenant_id).execute()
                    if res.data:
                        updated = res.data[0]
                except Exception:
                    pass

            event_bus.publish(
                tenant_id=tenant_id,
                event_name="contact.matched",
                payload={"person_id": existing["id"], "action": initial_action or "Activity linked to existing person"},
            )
            return updated or existing

        # 2. Create new Person
        person_id = f"person-{str(uuid.uuid4())[:8]}"
        person_data = {
            "id": person_id,
            "tenant_id": tenant_id,
            "full_name": full_name.strip(),
            "email": email_clean,
            "phone": phone_clean,
            "alt_phone": alt_phone,
            "organization_id": organization_id,
            "job_title": job_title,
            "person_type": person_type,
            "status": status,
            "tags": tags,
            "address": address,
            "city": city,
            "country": country,
            "source": source,
            "notes": notes,
            "created_at": now,
            "updated_at": now,
        }

        created = people_store.create(person_data, tenant_id)
        if supabase is not None:
            try:
                res = supabase.table("people").insert(person_data).execute()
                if res.data:
                    created = res.data[0]
            except Exception:
                pass

        event_bus.publish(
            tenant_id=tenant_id,
            event_name="contact.created",
            payload={"person_id": person_id, "full_name": full_name, "email": email_clean, "source": source},
        )
        return created

    # ---------------------------------------------------------------------------
    # Organizations
    # ---------------------------------------------------------------------------
    @staticmethod
    def find_or_create_organization(
        tenant_id: str,
        name: str,
        business_type: str = "Company",
        email: Optional[str] = None,
        phone: Optional[str] = None,
        website: Optional[str] = None,
        industry: Optional[str] = None,
        address: Optional[str] = None,
        city: Optional[str] = None,
        country: str = "Ethiopia",
        source: str = "Inquiry",
        notes: Optional[str] = None,
    ) -> dict[str, Any]:
        """Find or create an organization by name."""
        name_clean = name.strip()
        now = PeopleService._now()

        all_orgs = organizations_store.list_all(tenant_id)
        for org in all_orgs:
            if org.get("name", "").strip().lower() == name_clean.lower():
                return org

        org_id = f"org-{str(uuid.uuid4())[:8]}"
        org_data = {
            "id": org_id,
            "tenant_id": tenant_id,
            "name": name_clean,
            "business_type": business_type,
            "email": email,
            "phone": phone,
            "website": website,
            "industry": industry,
            "address": address,
            "city": city,
            "country": country,
            "status": "Active",
            "source": source,
            "owner_id": None,
            "notes": notes,
            "created_at": now,
            "updated_at": now,
        }

        created = organizations_store.create(org_data, tenant_id)
        if supabase is not None:
            try:
                res = supabase.table("organizations").insert(org_data).execute()
                if res.data:
                    created = res.data[0]
            except Exception:
                pass

        event_bus.publish(
            tenant_id=tenant_id,
            event_name="organization.created",
            payload={"organization_id": org_id, "name": name_clean},
        )
        return created

    # ---------------------------------------------------------------------------
    # Queries & Single Views
    # ---------------------------------------------------------------------------
    @staticmethod
    def list_people(
        tenant_id: str,
        person_type: Optional[str] = None,
        status_filter: Optional[str] = None,
        organization_id: Optional[str] = None,
        search: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """List and filter People with organization names attached."""
        people = people_store.list_all(tenant_id)

        orgs = {o["id"]: o.get("name") for o in organizations_store.list_all(tenant_id)}

        if person_type and person_type != "all":
            people = [p for p in people if p.get("person_type", "").lower() == person_type.lower()]
        if status_filter and status_filter != "all":
            people = [p for p in people if p.get("status", "").lower() == status_filter.lower()]
        if organization_id:
            people = [p for p in people if p.get("organization_id") == organization_id]
        if search:
            s = search.lower()
            people = [
                p for p in people
                if s in p.get("full_name", "").lower()
                or s in (p.get("email") or "").lower()
                or s in (p.get("phone") or "").lower()
                or s in (p.get("job_title") or "").lower()
                or any(s in t.lower() for t in p.get("tags", []))
            ]

        results = []
        for p in people:
            item = dict(p)
            item["organization_name"] = orgs.get(p.get("organization_id"))
            results.append(item)

        return sorted(results, key=lambda x: x.get("created_at", ""), reverse=True)

    @staticmethod
    def get_person_by_id(tenant_id: str, person_id: str) -> Optional[dict[str, Any]]:
        p = people_store.get(person_id, tenant_id)
        if p and p.get("organization_id"):
            org = organizations_store.get(p["organization_id"], tenant_id)
            p["organization_name"] = org.get("name") if org else None
        return p

    @staticmethod
    def update_person(tenant_id: str, person_id: str, updates: dict[str, Any]) -> Optional[dict[str, Any]]:
        updates["updated_at"] = PeopleService._now()
        if supabase is None:
            return people_store.update(person_id, updates, tenant_id)
        try:
            res = supabase.table("people").update(updates).eq("id", person_id).eq("tenant_id", tenant_id).execute()
            return res.data[0] if res.data else updates
        except Exception:
            return updates

    @staticmethod
    def delete_person(tenant_id: str, person_id: str) -> bool:
        if supabase is None:
            return people_store.delete(person_id, tenant_id)
        try:
            supabase.table("people").delete().eq("id", person_id).eq("tenant_id", tenant_id).execute()
            return True
        except Exception:
            return False

    @staticmethod
    def list_organizations(tenant_id: str, search: Optional[str] = None) -> list[dict[str, Any]]:
        orgs = organizations_store.list_all(tenant_id)

        all_people = people_store.list_all(tenant_id)
        results = []
        for o in orgs:
            item = dict(o)
            item["people_count"] = sum(1 for p in all_people if p.get("organization_id") == o["id"])
            if search:
                s = search.lower()
                if (
                    s not in item.get("name", "").lower()
                    and s not in (item.get("industry") or "").lower()
                    and s not in (item.get("email") or "").lower()
                ):
                    continue
            results.append(item)

        return sorted(results, key=lambda x: x.get("created_at", ""), reverse=True)

    @staticmethod
    def get_organization_by_id(tenant_id: str, org_id: str) -> Optional[dict[str, Any]]:
        return organizations_store.get(org_id, tenant_id)

    # ---------------------------------------------------------------------------
    # 360-Degree Unified Person Profile Aggregator
    # ---------------------------------------------------------------------------
    @staticmethod
    def get_person_detailed_profile(tenant_id: str, person_id: str) -> Optional[dict[str, Any]]:
        """Assembles a true 360° cross-module view for a person without duplication."""
        person = PeopleService.get_person_by_id(tenant_id, person_id)
        if not person:
            return None

        email = (person.get("email") or "").lower()
        phone = person.get("phone")
        full_name = person.get("full_name")
        org_id = person.get("organization_id")

        # 1. Organization
        org = organizations_store.get(org_id, tenant_id) if org_id else None

        # 2. CRM Opportunities / Deals
        all_opps = crm_opportunities_store.list_all(tenant_id)
        opps = [o for o in all_opps if o.get("person_id") == person_id or (org_id and o.get("organization_id") == org_id)]

        # 3. CRM Activities & Tasks
        all_acts = crm_activities_store.list_all(tenant_id)
        acts = [a for a in all_acts if a.get("person_id") == person_id or (org_id and a.get("organization_id") == org_id)]

        # 4. Student Records
        all_students = students_store.list_all(tenant_id)
        student_records = [
            s for s in all_students
            if (email and s.get("email", "").lower() == email)
            or (phone and s.get("phone") == phone)
            or s.get("full_name") == full_name
        ]

        # 5. Service Requests (Software, Visa, Travel, Support Tickets)
        service_requests = []
        for p in software_projects_store.list_all(tenant_id):
            if (email and p.get("email", "").lower() == email) or (phone and p.get("phone") == phone):
                service_requests.append({"module": "Software", "title": p.get("project_name"), "reference": p.get("reference_code"), "status": p.get("status"), "created_at": p.get("created_at")})

        for v in visa_applications_store.list_all(tenant_id):
            if (email and v.get("email", "").lower() == email) or (phone and v.get("phone") == phone) or v.get("applicant_name") == full_name:
                service_requests.append({"module": "Visa", "title": f"Visa to {v.get('destination_country')}", "reference": v.get("reference_code"), "status": v.get("status"), "created_at": v.get("created_at")})

        for t in travel_requests_store.list_all(tenant_id):
            if (email and t.get("email", "").lower() == email) or (phone and t.get("phone") == phone) or t.get("traveler_name") == full_name:
                service_requests.append({"module": "Travel", "title": f"Travel: {t.get('destination_country')}", "reference": t.get("reference_code"), "status": t.get("status"), "created_at": t.get("created_at")})

        for tk in support_tickets_store.list_all(tenant_id):
            if (email and tk.get("email", "").lower() == email) or (phone and tk.get("phone") == phone):
                service_requests.append({"module": "Inquiry/Ticket", "title": tk.get("subject"), "reference": tk.get("id"), "status": tk.get("status"), "created_at": tk.get("created_at")})

        # 6. Invoices & Payments
        all_invoices = invoices_store.list_all(tenant_id)
        invoices = [
            i for i in all_invoices
            if (email and i.get("customer_email", "").lower() == email)
            or i.get("customer_name") == full_name
            or (person.get("crm_contact_id") and i.get("contact_id") == person.get("crm_contact_id"))
        ]

        all_txs = payment_transactions_store.list_all(tenant_id)
        txs = [
            t for t in all_txs
            if (email and (t.get("customer_email") or "").lower() == email)
            or t.get("customer_name") == full_name
        ]
        total_paid = sum(t.get("amount", 0.0) for t in txs if t.get("status") == "successful")

        # 7. Marketing Communications
        all_comms = communication_logs_store.list_all(tenant_id)
        comms = [c for c in all_comms if c.get("person_id") == person_id or (email and c.get("recipient", "").lower() == email)]

        # 8. Unified Chronological Timeline
        timeline_events = []
        for tk in support_tickets_store.list_all(tenant_id):
            if (email and tk.get("email", "").lower() == email) or (phone and tk.get("phone") == phone):
                timeline_events.append({
                    "date": tk.get("created_at"),
                    "category": "Inquiry",
                    "title": f"Inquiry Submitted: {tk.get('subject')}",
                    "description": tk.get("message", "Inquiry received via website form."),
                    "actor": "client",
                })

        for opp in opps:
            timeline_events.append({
                "date": opp.get("created_at"),
                "category": "Opportunity",
                "title": f"CRM Opportunity Created: {opp.get('title')}",
                "description": f"Stage: {opp.get('pipeline_stage')} — Value: {opp.get('value'):,.2f} {opp.get('currency')}",
                "actor": "sales",
            })

        for act in acts:
            timeline_events.append({
                "date": act.get("completed_at") or act.get("created_at"),
                "category": "Activity",
                "title": f"{act.get('activity_type')}: {act.get('subject')}",
                "description": act.get("description", "Activity recorded by team."),
                "actor": act.get("actor", "staff"),
            })

        for s in student_records:
            timeline_events.append({
                "date": s.get("created_at"),
                "category": "Course",
                "title": f"Enrolled in {s.get('course')}",
                "description": f"Schedule: {s.get('schedule', 'Standard')} ({s.get('status')})",
                "actor": "student",
            })

        for t in txs:
            timeline_events.append({
                "date": t.get("completed_at") or t.get("created_at"),
                "category": "Payment",
                "title": f"Payment: {t.get('public_reference')} ({t.get('status')})",
                "description": f"Amount: {t.get('amount'):,.2f} {t.get('currency')} via {t.get('payment_method')}",
                "actor": "payment_engine",
            })

        for c in comms:
            timeline_events.append({
                "date": c.get("created_at"),
                "category": "Marketing",
                "title": f"Campaign {c.get('channel')}: {c.get('subject')}",
                "description": c.get("message_body", "Marketing message delivered."),
                "actor": "marketing_automation",
            })

        timeline_events.sort(key=lambda x: x.get("date") or "", reverse=True)

        return {
            "person": person,
            "organization": org,
            "crm_lead": {"id": person["id"], "name": person["full_name"], "status": person["status"]},
            "opportunities": opps,
            "activities": acts,
            "student_records": student_records,
            "service_requests": service_requests,
            "invoices": invoices,
            "payments": txs,
            "total_paid_volume": round(total_paid, 2),
            "campaign_communications": comms,
            "timeline": timeline_events,
        }
