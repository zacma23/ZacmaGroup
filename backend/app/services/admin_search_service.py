"""Enterprise Admin Search, Sorting, Filtering, and Natural Language AI Query Engine.

Provides unified server-side multi-entity searching, multi-field partial matching,
multi-criteria sorting, facet calculations, pagination, and authorized natural language
AI querying across 15+ business domains.
"""

from datetime import datetime, timezone
import logging
import re
from typing import Any, Optional

from app.core.config import settings
from app.core.demo_data import (
    admin_users_store,
    attendance_store,
    audit_logs_store,
    automation_jobs_store,
    bookings_store,
    campaigns_store,
    courses_store,
    crm_activities_store,
    crm_contacts_store,
    crm_opportunities_store,
    employees_store,
    invoices_store,
    knowledge_base_store,
    leaves_store,
    organizations_store,
    payment_transactions_store,
    people_store,
    software_projects_store,
    students_store,
    support_tickets_store,
    travel_requests_store,
    visa_applications_store,
)
from app.models import (
    AdminAiSearchResponse,
    AdminSearchFacet,
    AdminSearchPagination,
    AdminSearchResponse,
    AdminSearchResultItem,
)

logger = logging.getLogger("zacma.admin_search")


class AdminSearchService:
    """Enterprise multi-domain search and AI query aggregator."""

    @classmethod
    def _collect_all_items(cls, tenant_id: str) -> list[dict[str, Any]]:
        """Collect all records across all business lines for the given tenant."""
        items: list[dict[str, Any]] = []

        # 1. Students / Training Registrations
        for s in students_store.list_all(tenant_id):
            items.append({
                "id": s["id"],
                "module": "Training",
                "entity_type": "student",
                "title": f"{s.get('full_name', 'Student')} — {s.get('course', 'Course')}",
                "subtitle": f"Schedule: {s.get('schedule', 'Flexible')} ({s.get('time_slot', 'N/A')})",
                "status": s.get("status", "Pending"),
                "email": s.get("email"),
                "phone": s.get("phone"),
                "amount": None,
                "currency": "ETB",
                "priority": "Normal",
                "category": s.get("course"),
                "created_at": s.get("created_at"),
                "updated_at": s.get("created_at"),
                "reference_code": s.get("reference_code") or f"STU-{s['id'][:6].upper()}",
                "detail_url": f"/dashboard/training",
                "metadata": {"address": s.get("address"), "payment_method": s.get("payment_method")},
            })

        # 2. Visa Applications
        for v in visa_applications_store.list_all(tenant_id):
            items.append({
                "id": v["id"],
                "module": "Visa",
                "entity_type": "visa",
                "title": f"{v.get('full_name', 'Applicant')} — {v.get('destination_country', 'Visa')}",
                "subtitle": f"Type: {v.get('visa_type', 'General')} | Travel: {v.get('intended_travel_date', 'TBD')}",
                "status": v.get("status", "Submitted"),
                "email": v.get("email"),
                "phone": v.get("phone"),
                "amount": None,
                "currency": "USD",
                "priority": "High" if v.get("status") in ["Under Review", "Pending"] else "Normal",
                "category": v.get("destination_country"),
                "created_at": v.get("created_at"),
                "updated_at": v.get("created_at"),
                "reference_code": v.get("reference_code") or f"VIS-{v['id'][:6].upper()}",
                "detail_url": f"/dashboard/visa",
                "metadata": {"passport": v.get("passport_number"), "documents_count": len(v.get("document_urls", []))},
            })

        # 3. Travel Requests & Bookings
        for t in travel_requests_store.list_all(tenant_id):
            items.append({
                "id": t["id"],
                "module": "Travel",
                "entity_type": "travel_request",
                "title": f"{t.get('full_name', 'Traveler')} — {t.get('destination_country', 'Travel')}",
                "subtitle": f"Travelers: {t.get('number_of_travelers', 1)} | Departure: {t.get('departure_date', 'Flexible')}",
                "status": t.get("status", "Pending"),
                "email": t.get("email"),
                "phone": t.get("phone"),
                "amount": float(t.get("budget", 0)) if t.get("budget") else None,
                "currency": "USD",
                "priority": "Normal",
                "category": t.get("destination_country"),
                "created_at": t.get("created_at"),
                "updated_at": t.get("created_at"),
                "reference_code": t.get("reference_code") or f"TRV-{t['id'][:6].upper()}",
                "detail_url": f"/dashboard/travel",
                "metadata": {"package": t.get("travel_package"), "origin": t.get("origin_country")},
            })

        for b in bookings_store.list_all(tenant_id):
            items.append({
                "id": b["id"],
                "module": "Travel",
                "entity_type": "booking",
                "title": f"Booking #{b['id'][:8]} — {b.get('destination', 'Trip')}",
                "subtitle": f"Customer: {b.get('customer_name', 'N/A')} | Guests: {b.get('guests', 1)}",
                "status": b.get("status", "Confirmed"),
                "email": b.get("customer_email"),
                "phone": b.get("customer_phone"),
                "amount": float(b.get("total_price", 0)) if b.get("total_price") else None,
                "currency": "USD",
                "priority": "Normal",
                "category": b.get("destination"),
                "created_at": b.get("created_at"),
                "updated_at": b.get("created_at"),
                "reference_code": b.get("reference_code") or f"BKG-{b['id'][:6].upper()}",
                "detail_url": f"/dashboard/travel",
                "metadata": {"dates": b.get("travel_dates")},
            })

        # 4. Payments & Transactions & Invoices
        for tx in payment_transactions_store.list_all(tenant_id):
            items.append({
                "id": tx["id"],
                "module": "Payments",
                "entity_type": "payment_transaction",
                "title": f"Payment {tx.get('public_reference', tx['id'][:8])} — {tx.get('amount', 0):,.2f} {tx.get('currency', 'ETB')}",
                "subtitle": f"Customer: {tx.get('customer_name', 'Anonymous')} | Provider: {tx.get('provider_code', 'Chapa').upper()}",
                "status": tx.get("status", "pending"),
                "email": tx.get("customer_email"),
                "phone": tx.get("customer_phone"),
                "amount": float(tx.get("amount", 0)),
                "currency": tx.get("currency", "ETB"),
                "priority": "High" if tx.get("status") == "pending" else "Normal",
                "category": tx.get("provider_code"),
                "created_at": tx.get("created_at"),
                "updated_at": tx.get("updated_at") or tx.get("created_at"),
                "reference_code": tx.get("public_reference"),
                "detail_url": f"/dashboard/payments",
                "metadata": {"purpose": tx.get("payment_purpose"), "settled": tx.get("is_settled", False)},
            })

        for inv in invoices_store.list_all(tenant_id):
            items.append({
                "id": inv["id"],
                "module": "Payments",
                "entity_type": "invoice",
                "title": f"Invoice {inv.get('reference_code', inv['id'][:8])} — {inv.get('amount', 0):,.2f} {inv.get('currency', 'ETB')}",
                "subtitle": f"Client: {inv.get('customer_name', 'Client')} | Due: {inv.get('due_date', 'N/A')}",
                "status": inv.get("status", "unpaid"),
                "email": inv.get("customer_email"),
                "phone": None,
                "amount": float(inv.get("amount", 0)),
                "currency": inv.get("currency", "ETB"),
                "priority": "High" if inv.get("status") in ["unpaid", "overdue"] else "Normal",
                "category": "Invoice",
                "created_at": inv.get("created_at"),
                "updated_at": inv.get("created_at"),
                "reference_code": inv.get("reference_code"),
                "detail_url": f"/dashboard/payments",
                "metadata": {"service": inv.get("service_type")},
            })

        # 5. Support Tickets
        for tk in support_tickets_store.list_all(tenant_id):
            items.append({
                "id": tk["id"],
                "module": "Support",
                "entity_type": "support_ticket",
                "title": f"Ticket #{tk['id'][:8]}: {tk.get('subject', 'Inquiry')}",
                "subtitle": f"From: {tk.get('full_name', 'User')} | Category: {tk.get('category', 'General')}",
                "status": tk.get("status", "Open"),
                "email": tk.get("email"),
                "phone": tk.get("phone"),
                "amount": None,
                "currency": None,
                "priority": tk.get("priority", "Medium"),
                "category": tk.get("category", "General"),
                "created_at": tk.get("created_at"),
                "updated_at": tk.get("updated_at") or tk.get("created_at"),
                "reference_code": f"TCK-{tk['id'][:6].upper()}",
                "detail_url": f"/dashboard/admin/inbox",
                "metadata": {"message_preview": (tk.get("message") or "")[:100]},
            })

        # 6. CRM Contacts & Opportunities
        for c in crm_contacts_store.list_all(tenant_id):
            items.append({
                "id": c["id"],
                "module": "CRM",
                "entity_type": "crm_contact",
                "title": f"Contact: {c.get('full_name', 'Contact')}",
                "subtitle": f"Source: {c.get('source_module', 'Inbound')} | Org: {c.get('organization_name', 'Individual')}",
                "status": c.get("status", "Active"),
                "email": c.get("email"),
                "phone": c.get("phone"),
                "amount": None,
                "currency": None,
                "priority": "Normal",
                "category": c.get("source_module"),
                "created_at": c.get("created_at"),
                "updated_at": c.get("created_at"),
                "reference_code": f"CRM-{c['id'][:6].upper()}",
                "detail_url": f"/dashboard/crm",
                "metadata": {"notes": c.get("notes")},
            })

        for opp in crm_opportunities_store.list_all(tenant_id):
            items.append({
                "id": opp["id"],
                "module": "CRM Opportunities",
                "entity_type": "crm_opportunity",
                "title": f"Deal: {opp.get('title', 'Deal')} — {opp.get('value', 0):,.2f} {opp.get('currency', 'ETB')}",
                "subtitle": f"Stage: {opp.get('pipeline_stage', 'New Lead')} ({opp.get('probability', 0)}% prob) | Contact: {opp.get('person_name', 'N/A')}",
                "status": opp.get("status", "Open"),
                "email": None,
                "phone": None,
                "amount": float(opp.get("value", 0)),
                "currency": opp.get("currency", "ETB"),
                "priority": "High" if opp.get("value", 0) > 100000 else "Normal",
                "category": opp.get("pipeline_stage"),
                "created_at": opp.get("created_at"),
                "updated_at": opp.get("created_at"),
                "reference_code": f"OPP-{opp['id'][:6].upper()}",
                "detail_url": f"/dashboard/crm",
                "metadata": {"org": opp.get("organization_name"), "expected_close": opp.get("expected_close_date")},
            })

        # 7. People Directory & Organizations
        for p in people_store.list_all(tenant_id):
            items.append({
                "id": p["id"],
                "module": "People",
                "entity_type": "person",
                "title": f"Person: {p.get('full_name', 'Person')}",
                "subtitle": f"{p.get('job_title', 'Member')} | Type: {p.get('person_type', 'Individual')} | {p.get('city', 'Addis Ababa')}",
                "status": p.get("status", "Active"),
                "email": p.get("email"),
                "phone": p.get("phone"),
                "amount": None,
                "currency": None,
                "priority": "Normal",
                "category": p.get("person_type"),
                "created_at": p.get("created_at"),
                "updated_at": p.get("created_at"),
                "reference_code": f"PPL-{p['id'][:6].upper()}",
                "detail_url": f"/dashboard/people",
                "metadata": {"tags": p.get("tags", []), "organization_id": p.get("organization_id")},
            })

        for org in organizations_store.list_all(tenant_id):
            items.append({
                "id": org["id"],
                "module": "Organizations",
                "entity_type": "organization",
                "title": f"Org: {org.get('name', 'Company')}",
                "subtitle": f"Industry: {org.get('industry', 'Business')} | Type: {org.get('business_type', 'Enterprise')}",
                "status": org.get("status", "Active"),
                "email": org.get("email"),
                "phone": org.get("phone"),
                "amount": None,
                "currency": None,
                "priority": "Normal",
                "category": org.get("industry"),
                "created_at": org.get("created_at"),
                "updated_at": org.get("created_at"),
                "reference_code": f"ORG-{org['id'][:6].upper()}",
                "detail_url": f"/dashboard/people",
                "metadata": {"website": org.get("website")},
            })

        # 8. Software Development Projects
        for sp in software_projects_store.list_all(tenant_id):
            items.append({
                "id": sp["id"],
                "module": "Software",
                "entity_type": "software_project",
                "title": f"Project: {sp.get('client_name', 'Client')} — {sp.get('software_category', 'Software')}",
                "subtitle": f"Stack: {', '.join(sp.get('technologies', []))} | Est. Cost: {sp.get('estimated_cost_etb', 0):,.2f} ETB",
                "status": sp.get("status", "Pending Review"),
                "email": sp.get("client_email"),
                "phone": sp.get("client_phone"),
                "amount": float(sp.get("estimated_cost_etb", 0)),
                "currency": "ETB",
                "priority": "High",
                "category": sp.get("software_category"),
                "created_at": sp.get("created_at"),
                "updated_at": sp.get("created_at"),
                "reference_code": sp.get("reference_code") or f"PRJ-{sp['id'][:6].upper()}",
                "detail_url": f"/dashboard/admin/reviews",
                "metadata": {"scope": sp.get("project_scope"), "timeline": sp.get("timeline_weeks")},
            })

        # 9. Knowledge Base & Documents
        for kb in knowledge_base_store.list_all(tenant_id):
            items.append({
                "id": kb["id"],
                "module": "Knowledge",
                "entity_type": "knowledge_doc",
                "title": f"Doc: {kb.get('title', 'Article')}",
                "subtitle": f"Category: {kb.get('category', 'General')} | Tags: {', '.join(kb.get('tags', []))}",
                "status": kb.get("status", "Published"),
                "email": None,
                "phone": None,
                "amount": None,
                "currency": None,
                "priority": "Normal",
                "category": kb.get("category"),
                "created_at": kb.get("created_at"),
                "updated_at": kb.get("created_at"),
                "reference_code": f"DOC-{kb['id'][:6].upper()}",
                "detail_url": f"/dashboard/admin/packages",
                "metadata": {"slug": kb.get("slug")},
            })

        # 10. Staff & HR Employees
        for emp in employees_store.list_all(tenant_id):
            items.append({
                "id": emp["id"],
                "module": "Staff",
                "entity_type": "employee",
                "title": f"Staff: {emp.get('name', 'Staff Member')}",
                "subtitle": f"Role: {emp.get('role', 'Team')} | Dept: {emp.get('department', 'General')} | Salary: {emp.get('salary', 0):,.2f} ETB",
                "status": emp.get("status", "Active"),
                "email": emp.get("email"),
                "phone": emp.get("phone"),
                "amount": float(emp.get("salary", 0)),
                "currency": "ETB",
                "priority": "Normal",
                "category": emp.get("department"),
                "created_at": emp.get("created_at") or "2026-01-01T00:00:00Z",
                "updated_at": emp.get("created_at") or "2026-01-01T00:00:00Z",
                "reference_code": f"EMP-{emp['id'][:6].upper()}",
                "detail_url": f"/dashboard/people",
                "metadata": {"department": emp.get("department")},
            })

        # 11. Platform Users
        for u in admin_users_store.list_all(tenant_id):
            items.append({
                "id": u["id"],
                "module": "Users",
                "entity_type": "user",
                "title": f"User: {u.get('full_name', 'User')} ({u.get('role', 'client')})",
                "subtitle": f"Email: {u.get('email')} | Tenant: {u.get('tenant_id')}",
                "status": u.get("status", "active"),
                "email": u.get("email"),
                "phone": u.get("phone"),
                "amount": None,
                "currency": None,
                "priority": "High" if u.get("role") == "admin" else "Normal",
                "category": u.get("role"),
                "created_at": u.get("created_at") or "2026-01-01T00:00:00Z",
                "updated_at": u.get("created_at") or "2026-01-01T00:00:00Z",
                "reference_code": f"USR-{u['id'][:6].upper()}",
                "detail_url": f"/dashboard/admin/users",
                "metadata": {"role": u.get("role")},
            })

        # 12. Automation Jobs
        for aj in automation_jobs_store.list_all(tenant_id):
            items.append({
                "id": aj["id"],
                "module": "Automation",
                "entity_type": "automation_job",
                "title": f"Job: {aj.get('job_type', 'Task')} — {aj.get('entity_type', 'entity')}/{aj.get('entity_id', '')}",
                "subtitle": f"Status: {aj.get('status')} | Retries: {aj.get('retry_count', 0)}/{aj.get('max_retries', 3)}",
                "status": aj.get("status", "pending"),
                "email": None,
                "phone": None,
                "amount": None,
                "currency": None,
                "priority": "High" if aj.get("status") in ["failed", "retry"] else "Normal",
                "category": aj.get("job_type"),
                "created_at": aj.get("created_at"),
                "updated_at": aj.get("updated_at") or aj.get("created_at"),
                "reference_code": f"JOB-{aj['id'][:6].upper()}",
                "detail_url": f"/dashboard/admin/reviews",
                "metadata": {"job_type": aj.get("job_type"), "entity_type": aj.get("entity_type")},
            })

        return items

    @classmethod
    def search(
        cls,
        tenant_id: str,
        query: Optional[str] = None,
        module: Optional[str] = "all",
        status: Optional[str] = "all",
        category: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None,
        sort_by: str = "newest",
        page: int = 1,
        page_size: int = 25,
    ) -> AdminSearchResponse:
        """Execute full multi-domain filtered search with sorting, facets, and pagination."""
        all_items = cls._collect_all_items(tenant_id)
        filtered = list(all_items)

        # 1. Multi-Field Partial / Keyword Matching
        if query and query.strip():
            tokens = [t.lower().strip() for t in query.strip().split() if t.strip()]
            
            def matches_query(item: dict[str, Any]) -> bool:
                searchable_text = " ".join([
                    str(item.get("title") or ""),
                    str(item.get("subtitle") or ""),
                    str(item.get("email") or ""),
                    str(item.get("phone") or ""),
                    str(item.get("reference_code") or ""),
                    str(item.get("id") or ""),
                    str(item.get("status") or ""),
                    str(item.get("category") or ""),
                    str(item.get("module") or ""),
                    str(item.get("metadata") or ""),
                ]).lower()
                return all(token in searchable_text for token in tokens)

            filtered = [item for item in filtered if matches_query(item)]

        # 2. Module Filter
        if module and module.lower() not in {"all", "*", ""}:
            mod_target = module.lower().strip()
            def matches_module(item: dict[str, Any]) -> bool:
                m_str = (item.get("module") or "").lower()
                e_str = (item.get("entity_type") or "").lower()
                if mod_target == "crm":
                    return "crm" in m_str or "deal" in m_str or "contact" in m_str
                if mod_target == "people":
                    return "people" in m_str or "organization" in m_str or "staff" in m_str or "employee" in m_str
                if mod_target in {"training", "students"}:
                    return "training" in m_str or "student" in m_str
                if mod_target in {"travel", "bookings"}:
                    return "travel" in m_str or "booking" in m_str
                if mod_target in {"payments", "invoices"}:
                    return "payment" in m_str or "invoice" in m_str
                return mod_target in m_str or mod_target in e_str or m_str == mod_target

            filtered = [item for item in filtered if matches_module(item)]

        # 3. Status Filter
        if status and status.lower() not in {"all", "*", ""}:
            stat_target = status.lower().strip()
            filtered = [item for item in filtered if (item.get("status") or "").lower() == stat_target]

        # 4. Category Filter
        if category and category.strip():
            cat_target = category.lower().strip()
            filtered = [item for item in filtered if cat_target in (item.get("category") or "").lower()]

        # 5. Date Range Filter
        if date_from:
            try:
                dt_from = date_from[:10]
                filtered = [item for item in filtered if item.get("created_at") and item["created_at"][:10] >= dt_from]
            except Exception:
                pass

        if date_to:
            try:
                dt_to = date_to[:10]
                filtered = [item for item in filtered if item.get("created_at") and item["created_at"][:10] <= dt_to]
            except Exception:
                pass

        # 6. Amount Range Filter
        if min_amount is not None:
            filtered = [item for item in filtered if item.get("amount") is not None and item["amount"] >= min_amount]

        if max_amount is not None:
            filtered = [item for item in filtered if item.get("amount") is not None and item["amount"] <= max_amount]

        # 7. Facet Counts Calculation (Before pagination)
        module_counts: dict[str, int] = {}
        status_counts: dict[str, int] = {}
        for it in filtered:
            m = it.get("module", "Other")
            s = it.get("status") or "Unknown"
            module_counts[m] = module_counts.get(m, 0) + 1
            status_counts[s] = status_counts.get(s, 0) + 1

        module_facets = [
            AdminSearchFacet(key=k.lower(), label=k, count=v)
            for k, v in sorted(module_counts.items(), key=lambda x: x[1], reverse=True)
        ]
        status_facets = [
            AdminSearchFacet(key=k.lower(), label=k, count=v)
            for k, v in sorted(status_counts.items(), key=lambda x: x[1], reverse=True)
        ]

        # 8. Dynamic Sorting Engine
        def get_sort_key(item: dict[str, Any]):
            if sort_by in {"newest", "created_desc"}:
                return item.get("created_at") or ""
            elif sort_by in {"oldest", "created_asc"}:
                return item.get("created_at") or ""
            elif sort_by == "name_asc":
                return (item.get("title") or "").lower()
            elif sort_by == "name_desc":
                return (item.get("title") or "").lower()
            elif sort_by == "amount_desc":
                return item.get("amount") or 0.0
            elif sort_by == "amount_asc":
                return item.get("amount") or 0.0
            elif sort_by == "status":
                return (item.get("status") or "").lower()
            elif sort_by == "priority":
                prio_rank = {"high": 3, "medium": 2, "normal": 1, "low": 0}
                return prio_rank.get((item.get("priority") or "").lower(), 1)
            elif sort_by in {"recent_activity", "updated_desc"}:
                return item.get("updated_at") or item.get("created_at") or ""
            return item.get("created_at") or ""

        reverse_sort = sort_by in {"newest", "created_desc", "name_desc", "amount_desc", "priority", "recent_activity", "updated_desc"}
        
        try:
            filtered.sort(key=get_sort_key, reverse=reverse_sort)
        except Exception as e:
            logger.debug("Sorting fallback due to key comparison error: %s", e)

        # 9. Server-Side Pagination
        total_count = len(filtered)
        p = max(1, page)
        ps = max(1, min(100, page_size))
        total_pages = max(1, (total_count + ps - 1) // ps)
        start_idx = (p - 1) * ps
        end_idx = start_idx + ps
        paginated_items = filtered[start_idx:end_idx]

        results = [AdminSearchResultItem(**item) for item in paginated_items]

        return AdminSearchResponse(
            query=query,
            count=total_count,
            module_filter=module,
            status_filter=status,
            sort_by=sort_by,
            pagination=AdminSearchPagination(
                page=p,
                page_size=ps,
                total_count=total_count,
                total_pages=total_pages,
                has_next=p < total_pages,
                has_prev=p > 1,
            ),
            module_facets=module_facets,
            status_facets=status_facets,
            results=results,
        )

    @classmethod
    def ai_natural_search(
        cls,
        tenant_id: str,
        natural_query: str,
        max_results: int = 20,
    ) -> AdminAiSearchResponse:
        """Process natural language admin queries into structured filters + AI insights."""
        q_clean = natural_query.strip().lower()
        now_dt = datetime.now(timezone.utc)
        current_year = now_dt.strftime("%Y")
        current_month = now_dt.strftime("%Y-%m")

        # 1. Intent Detection & Filter Mapping
        target_module = "all"
        target_status = "all"
        date_from = None
        date_to = None
        keywords: list[str] = []

        if "visa" in q_clean:
            target_module = "visa"
        elif "training" in q_clean or "student" in q_clean or "course" in q_clean:
            target_module = "training"
        elif "travel" in q_clean or "flight" in q_clean or "hotel" in q_clean or "booking" in q_clean:
            target_module = "travel"
        elif "payment" in q_clean or "invoice" in q_clean or "unpaid" in q_clean or "paid" in q_clean or "money" in q_clean:
            target_module = "payments"
        elif "support" in q_clean or "ticket" in q_clean or "complaint" in q_clean:
            target_module = "support"
        elif "deal" in q_clean or "lead" in q_clean or "pipeline" in q_clean or "opportunity" in q_clean:
            target_module = "crm"
        elif "people" in q_clean or "contact" in q_clean or "person" in q_clean or "staff" in q_clean or "employee" in q_clean:
            target_module = "people"
        elif "software" in q_clean or "project" in q_clean or "app" in q_clean:
            target_module = "software"

        # Status intent
        if "unpaid" in q_clean:
            target_status = "unpaid"
        elif "cancelled" in q_clean or "canceled" in q_clean:
            target_status = "cancelled"
        elif "successful" in q_clean or "completed" in q_clean or "paid" in q_clean:
            target_status = "successful"
        elif "pending" in q_clean:
            target_status = "pending"
        elif "active" in q_clean:
            target_status = "active"
        elif "open" in q_clean:
            target_status = "open"

        # Date intent
        if "this month" in q_clean:
            date_from = f"{current_month}-01"
        elif "today" in q_clean:
            date_from = now_dt.strftime("%Y-%m-%d")
        elif "this year" in q_clean:
            date_from = f"{current_year}-01-01"

        # Extract specific keyword phrases (e.g., Dubai, Canada, Python, Chapa)
        dest_match = re.search(r"\b(dubai|canada|usa|schengen|italy|germany|uk|qatar|saudi|turkey)\b", q_clean)
        if dest_match:
            keywords.append(dest_match.group(1))

        search_q = " ".join(keywords) if keywords else None

        # 2. Execute Structured Search with Tenant Isolation
        search_res = cls.search(
            tenant_id=tenant_id,
            query=search_q,
            module=target_module,
            status=target_status,
            date_from=date_from,
            date_to=date_to,
            sort_by="newest",
            page=1,
            page_size=max_results,
        )

        matched_modules = [f.label for f in search_res.module_facets]
        total_found = search_res.pagination.total_count

        # 3. Generate Grounded AI Insights
        total_amount = sum(r.amount for r in search_res.results if r.amount is not None)
        status_breakdown = ", ".join([f"{f.count} {f.label}" for f in search_res.status_facets[:3]])

        if total_found == 0:
            ai_summary = (
                f"No matching records found for query: '{natural_query}'. "
                f"Searched module '{target_module}' with status filter '{target_status}'. "
                f"Try broadening your search criteria or resetting filters."
            )
        else:
            summary_parts = [
                f"Found {total_found} record(s) matching your request.",
                f"Breakdown: {status_breakdown}." if status_breakdown else "",
                f"Total aggregated monetary volume: {total_amount:,.2f} ETB." if total_amount > 0 else "",
                f"Records are sorted with newest activity first.",
            ]
            ai_summary = " ".join([p for p in summary_parts if p])

        return AdminAiSearchResponse(
            original_query=natural_query,
            parsed_intent=f"Module: {target_module.upper()} | Status: {target_status} | Keyword: {search_q or 'None'} | Date: {date_from or 'All'}",
            ai_summary=ai_summary,
            total_found=total_found,
            matched_modules=matched_modules,
            results=search_res.results,
        )
