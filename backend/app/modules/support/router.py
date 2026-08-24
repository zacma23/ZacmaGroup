"""Customer Support Module.

Handles support tickets, threaded conversations, admin replies, AI-suggested
responses, auto-categorization, CRM lead conversion, and interactive customer chatbot.
"""

import re
import uuid
from datetime import datetime, timezone
from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.core.config import settings
from app.core.demo_data import (
    crm_contacts_store,
    invoices_store,
    module_submissions_store,
    students_store,
    support_tickets_store,
    travel_requests_store,
    visa_applications_store,
)
from app.core.permissions import require_role
from app.core.tenancy import get_tenant_id
from app.models import (
    SupportTicketCreate,
    SupportTicketReplyRequest,
    SupportTicketResponse,
)
from app.services.ai_assistant_service import AiAssistantService
from app.services.crm_service import CrmService

router = APIRouter(prefix="/support", tags=["support"])


class ChatbotMessageRequest(BaseModel):
    message: str
    user_email: Optional[str] = None
    user_name: Optional[str] = None
    session_id: Optional[str] = None


class ChatbotMessageResponse(BaseModel):
    reply: str
    suggested_actions: list[dict[str, str]]
    category: str


def _contains_any_word(text: str, keywords: list[str]) -> bool:
    """Check for whole-word or specific keyword matching."""
    for kw in keywords:
        pattern = r"\b" + re.escape(kw) + r"\b"
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False


# ---------------------------------------------------------------------------
# Interactive Customer Support Chatbot
# ---------------------------------------------------------------------------

@router.post("/chat", response_model=ChatbotMessageResponse)
def customer_chatbot(
    payload: ChatbotMessageRequest,
    tenant_id: str = Depends(get_tenant_id),
):
    """Interactive Customer Support AI Bot providing guidance on all Zacma services and platforms."""
    result = AiAssistantService.consult_zacma_ai(
        query=payload.message,
        session_id=payload.session_id,
        tenant_id=tenant_id,
    )

    return ChatbotMessageResponse(
        reply=result["reply"],
        suggested_actions=result.get("actions", []),
        category=result.get("category", "General"),
    )


# ---------------------------------------------------------------------------
# Support Tickets (Queue, Conversation Threads, Agent Replies)
# ---------------------------------------------------------------------------

@router.get("/tickets", response_model=list[SupportTicketResponse])
def list_tickets(
    category: str | None = None,
    priority: str | None = None,
    status_filter: str | None = None,
    tenant_id: str = Depends(get_tenant_id),
):
    """List support tickets with queue and priority filtering."""
    tickets = support_tickets_store.list_all(tenant_id)
    if category:
        tickets = [t for t in tickets if t.get("category", "").lower() == category.lower()]
    if priority:
        tickets = [t for t in tickets if t.get("priority", "").lower() == priority.lower()]
    if status_filter:
        tickets = [t for t in tickets if t.get("status", "").lower() == status_filter.lower()]
    return sorted(tickets, key=lambda x: x.get("created_at", ""), reverse=True)


@router.post("/tickets", response_model=SupportTicketResponse, status_code=status.HTTP_201_CREATED)
def create_ticket(
    payload: SupportTicketCreate,
    tenant_id: str = Depends(get_tenant_id),
):
    """Create a new support ticket."""
    now = datetime.now(timezone.utc).isoformat()

    ai_eval = AiAssistantService.suggest_ticket_reply(payload.subject, payload.message)

    initial_thread = [
        {
            "id": str(uuid.uuid4()),
            "sender_type": "client",
            "sender_name": payload.full_name,
            "message": payload.message,
            "created_at": now,
        }
    ]

    data = payload.model_dump()
    data["thread"] = initial_thread
    data["ai_suggested_reply"] = ai_eval["draft_reply"]
    data["status"] = "Open"
    if payload.category == "general":
        data["category"] = ai_eval["suggested_category"]
    data["created_at"] = now
    data["updated_at"] = now

    created = support_tickets_store.create(data, tenant_id)
    tkt_id = created["id"]

    contact = CrmService.sync_contact(
        tenant_id=tenant_id,
        full_name=payload.full_name,
        email=payload.email,
        phone=payload.phone,
        source_module="Support",
        status="Active",
        tags=["Support", data["category"]],
        initial_action=f"Ticket opened: {payload.subject}",
        linked_entity_id=tkt_id,
    )
    contact_id = contact.get("id")

    support_tickets_store.update(tkt_id, {"linked_crm_contact_id": contact_id}, tenant_id)
    return support_tickets_store.get(tkt_id, tenant_id)


@router.get("/tickets/{tkt_id}", response_model=SupportTicketResponse)
def get_ticket(tkt_id: str, tenant_id: str = Depends(get_tenant_id)):
    """Get support ticket details and thread."""
    tkt = support_tickets_store.get(tkt_id, tenant_id)
    if not tkt:
        raise HTTPException(status_code=404, detail="Support ticket not found")
    return tkt


@router.post("/tickets/{tkt_id}/reply", response_model=SupportTicketResponse)
def reply_to_ticket(
    tkt_id: str,
    payload: SupportTicketReplyRequest,
    tenant_id: str = Depends(get_tenant_id),
    user: dict = Depends(require_role(["admin", "superadmin", "staff"])),
):
    """Admin/agent reply to support ticket."""
    tkt = support_tickets_store.get(tkt_id, tenant_id)
    if not tkt:
        raise HTTPException(status_code=404, detail="Support ticket not found")

    now = datetime.now(timezone.utc).isoformat()
    thread = tkt.get("thread", [])
    admin_name = user.get("full_name") or user.get("email") or "Zacma Agent"

    thread.append({
        "id": str(uuid.uuid4()),
        "sender_type": "admin",
        "sender_name": admin_name,
        "message": payload.message,
        "created_at": now,
    })

    new_status = payload.status_update.value if payload.status_update else "InProgress"
    support_tickets_store.update(tkt_id, {"thread": thread, "status": new_status, "updated_at": now}, tenant_id)

    contact_id = tkt.get("linked_crm_contact_id")
    if contact_id:
        CrmService.add_timeline_event(
            tenant_id=tenant_id,
            contact_id=contact_id,
            action="Support Ticket Reply",
            description=f"Agent {admin_name} replied to ticket: {tkt.get('subject')}",
            actor=admin_name,
        )

    return support_tickets_store.get(tkt_id, tenant_id)


@router.post("/tickets/{tkt_id}/assign")
def assign_ticket(
    tkt_id: str,
    assigned_admin_id: str,
    tenant_id: str = Depends(get_tenant_id),
    user: dict = Depends(require_role(["admin", "superadmin"])),
):
    """Assign ticket to a specific support agent."""
    tkt = support_tickets_store.update(tkt_id, {"assigned_admin_id": assigned_admin_id}, tenant_id)
    if not tkt:
        raise HTTPException(status_code=404, detail="Support ticket not found")
    return {"status": "success", "assigned_to": assigned_admin_id}


@router.post("/tickets/{tkt_id}/convert-lead")
def convert_ticket_to_lead(
    tkt_id: str,
    tenant_id: str = Depends(get_tenant_id),
    user: dict = Depends(require_role(["admin", "superadmin"])),
):
    """Explicitly convert ticket contact into an active CRM Sales Lead."""
    tkt = support_tickets_store.get(tkt_id, tenant_id)
    if not tkt:
        raise HTTPException(status_code=404, detail="Support ticket not found")

    contact = CrmService.sync_contact(
        tenant_id=tenant_id,
        full_name=tkt["full_name"],
        email=tkt["email"],
        phone=tkt.get("phone"),
        source_module="Support",
        status="Lead",
        tags=["Support Lead", tkt.get("category", "General")],
        initial_action=f"Converted from support ticket #{tkt_id}",
    )
    return {"status": "success", "message": "Client converted to CRM Lead", "contact": contact}


# ---------------------------------------------------------------------------
# Dynamic Service Packages API (Data-driven for Client Forms)
# ---------------------------------------------------------------------------

SERVICE_PACKAGES = {
    "visa": [
        {
            "id": "pkg-vis-basic",
            "name": "Basic Guidance",
            "tier": "Basic",
            "price": 2500.0,
            "currency": "ETB",
            "description": "Standard visa document guidance and application self-submission kit.",
            "features": [
                "Embassy checklist verification",
                "Form completion template",
                "Email support within 48h",
            ],
            "popular": False,
        },
        {
            "id": "pkg-vis-std",
            "name": "Standard Review",
            "tier": "Standard",
            "price": 5000.0,
            "currency": "ETB",
            "description": "Comprehensive document review, AI completeness audit, and flight itinerary assistance.",
            "features": [
                "AI document verification & audit",
                "Hotel booking & flight reservation assistance",
                "Financial document review",
                "Dedicated visa case manager",
            ],
            "popular": True,
        },
        {
            "id": "pkg-vis-prem",
            "name": "Premium Concierge",
            "tier": "Premium",
            "price": 10000.0,
            "currency": "ETB",
            "description": "End-to-end embassy liaison, appointment booking, expedited review, and mock interview prep.",
            "features": [
                "Full embassy appointment liaison",
                "Priority expedited processing",
                "1-on-1 Visa Interview coaching session",
                "24/7 priority support on WhatsApp & Telegram",
            ],
            "popular": False,
        },
    ],
    "travel": [
        {
            "id": "pkg-trv-std",
            "name": "Standard Booking",
            "tier": "Standard",
            "price": 3500.0,
            "currency": "ETB",
            "description": "Direct flight ticketing and verified hotel accommodation bookings.",
            "features": [
                "Best flight fare search & ticketing",
                "Hotel booking with free cancellation options",
                "E-ticket issuance & confirmation",
            ],
            "popular": False,
        },
        {
            "id": "pkg-trv-itinerary",
            "name": "Full 5-Day Itinerary",
            "tier": "Full Itinerary",
            "price": 8000.0,
            "currency": "ETB",
            "description": "Personalized day-by-day travel plan, tours, airport transfers, and activity bookings.",
            "features": [
                "Customized 5-day daily travel itinerary",
                "Airport transfers and ground transit planning",
                "Guided tour & landmark ticket reservations",
                "24/7 emergency travel helpline",
            ],
            "popular": True,
        },
        {
            "id": "pkg-trv-vip",
            "name": "VIP Concierge",
            "tier": "VIP",
            "price": 15000.0,
            "currency": "ETB",
            "description": "Luxury travel concierge with premium lounge access, 5-star hotels, and dedicated agent.",
            "features": [
                "5-Star hotel suites & business class coordination",
                "VIP airport lounge passes",
                "Private chauffeur & bespoke experiences",
                "Dedicated travel concierge manager",
            ],
            "popular": False,
        },
    ],
    "training": [
        {
            "id": "pkg-trn-single",
            "name": "Single Course",
            "tier": "Single",
            "price": 4500.0,
            "currency": "ETB",
            "description": "Individual accredited training course with practical lab sessions and certificate.",
            "features": [
                "Complete course syllabus (40+ hours)",
                "Hands-on lab equipment access",
                "Course completion certificate",
                "Instructor Q&A access",
            ],
            "popular": False,
        },
        {
            "id": "pkg-trn-bundle",
            "name": "Professional Bundle",
            "tier": "Bundle",
            "price": 8000.0,
            "currency": "ETB",
            "description": "Dual-course bundle (e.g. AI + Programming, or Graphics + Video Editing).",
            "features": [
                "2 Comprehensive courses included",
                "Portfolio development guidance",
                "Internship placement recommendation",
                "15% Discount on bundle price",
            ],
            "popular": True,
        },
        {
            "id": "pkg-trn-track",
            "name": "Full Career Track",
            "tier": "Career Track",
            "price": 14000.0,
            "currency": "ETB",
            "description": "Mastery program covering foundational to advanced industry certifications.",
            "features": [
                "3-4 Comprehensive courses in chosen specialty",
                "1-on-1 Industry Mentorship",
                "Guaranteed project portfolio review",
                "Direct job referral network",
            ],
            "popular": False,
        },
    ],
    "marketing": [
        {
            "id": "pkg-mkt-starter",
            "name": "Social Media Starter",
            "tier": "Starter",
            "price": 6000.0,
            "currency": "ETB",
            "description": "Essential social media setup, brand positioning, and monthly content calendar.",
            "features": [
                "12 custom branded social media posts/month",
                "Facebook, Instagram & Telegram management",
                "Audience targeting & community engagement",
            ],
            "popular": False,
        },
        {
            "id": "pkg-mkt-full",
            "name": "Full Digital Marketing",
            "tier": "Growth",
            "price": 15000.0,
            "currency": "ETB",
            "description": "Multi-channel advertising, lead generation funnels, and performance reporting.",
            "features": [
                "Paid ad campaign management (Meta & Google Ads)",
                "High-converting landing page copywriting",
                "Weekly analytics & ROI reporting",
                "Dedicated marketing strategist",
            ],
            "popular": True,
        },
        {
            "id": "pkg-mkt-combo",
            "name": "Branding & Growth Combo",
            "tier": "Enterprise",
            "price": 25000.0,
            "currency": "ETB",
            "description": "Complete corporate visual identity, logo package, digital PR, and full-funnel marketing.",
            "features": [
                "Full Brand Identity (Logo, Typography, Brand Book)",
                "Complete multi-channel marketing campaigns",
                "Video production and commercial reels",
                "Continuous conversion optimization",
            ],
            "popular": False,
        },
    ],
}


@router.get("/packages")
def get_service_packages(service: Optional[str] = None):
    """Retrieve data-driven package tiers for client forms."""
    if service:
        srv = service.lower().strip()
        if srv in SERVICE_PACKAGES:
            return {srv: SERVICE_PACKAGES[srv]}
    return SERVICE_PACKAGES


# ---------------------------------------------------------------------------
# Public Unified Request Tracking API
# ---------------------------------------------------------------------------

@router.get("/track/{reference_code}")
def track_request(
    reference_code: str,
    tenant_id: str = Depends(get_tenant_id),
):
    """Unified tracker for Visa, Travel, Student, Dynamic submissions, and Invoices."""
    ref = reference_code.strip()
    ref_lower = ref.lower()

    # 1. Search in Visa Applications
    visas = visa_applications_store.list_all(tenant_id)
    matched_visa = next((v for v in visas if v.get("id", "").lower() == ref_lower or ref_lower in v.get("full_name", "").lower() or v.get("linked_invoice_id") == ref), None)
    if matched_visa:
        inv = invoices_store.get(matched_visa.get("linked_invoice_id", ""), tenant_id)
        return {
            "reference_code": ref,
            "id": matched_visa["id"],
            "service_type": "Visa Assistant",
            "customer_name": matched_visa.get("full_name"),
            "status": matched_visa.get("status", "UnderReview"),
            "submission_date": matched_visa.get("created_at"),
            "package": matched_visa.get("visa_type", "Tourist Visa"),
            "details": {
                "destination": matched_visa.get("destination_country"),
                "visa_type": matched_visa.get("visa_type"),
                "ai_check": matched_visa.get("ai_document_check_summary"),
                "notes": matched_visa.get("notes"),
            },
            "invoice": inv or {
                "amount": matched_visa.get("advance_amount", 5000.0),
                "currency": "ETB",
                "status": "sent",
                "receiving_account": settings.default_receiving_account,
                "payment_method": matched_visa.get("advance_payment_method", "CBE"),
                "reference_code": f"ZAC-VIS-{matched_visa['id'][:4]}",
            },
            "timeline": [
                {"status": "Submitted", "timestamp": matched_visa.get("created_at"), "description": f"Visa application submitted for {matched_visa.get('destination_country')}"},
                {"status": "Document Verification", "timestamp": matched_visa.get("updated_at"), "description": matched_visa.get("ai_document_check_summary", "Documents uploaded and verified.")},
                {"status": matched_visa.get("status"), "timestamp": matched_visa.get("updated_at"), "description": f"Current status: {matched_visa.get('status')}"},
            ],
            "messages": [
                {
                    "id": "msg-1",
                    "sender_type": "ai",
                    "sender_name": "Zacma AI Assistant",
                    "message": f"Hello {matched_visa.get('full_name')}! We have received your {matched_visa.get('destination_country')} visa application. Our team is currently reviewing your uploaded documents.",
                    "created_at": matched_visa.get("created_at"),
                }
            ],
        }

    # 2. Search in Student Registrations
    students = students_store.list_all(tenant_id)
    matched_student = next((s for s in students if s.get("id", "").lower() == ref_lower or ref_lower in s.get("full_name", "").lower()), None)
    if matched_student:
        inv = invoices_store.get(matched_student.get("linked_invoice_id", ""), tenant_id)
        return {
            "reference_code": ref,
            "id": matched_student["id"],
            "service_type": "Training Institute",
            "customer_name": matched_student.get("full_name"),
            "status": matched_student.get("status", "Pending"),
            "submission_date": matched_student.get("created_at"),
            "package": matched_student.get("course"),
            "details": {
                "course": matched_student.get("course"),
                "education_level": matched_student.get("education_level"),
                "ai_recommendation": matched_student.get("ai_course_recommendation"),
            },
            "invoice": inv or {
                "amount": 4500.0,
                "currency": "ETB",
                "status": "confirmed" if matched_student.get("status") == "Approved" else "sent",
                "receiving_account": settings.default_receiving_account,
                "payment_method": matched_student.get("payment_method", "TeleBirr"),
                "reference_code": f"ZAC-STU-{matched_student['id'][:4]}",
            },
            "timeline": [
                {"status": "Submitted", "timestamp": matched_student.get("created_at"), "description": f"Course enrollment submitted for {matched_student.get('course')}"},
                {"status": matched_student.get("status"), "timestamp": matched_student.get("updated_at"), "description": f"Registration status: {matched_student.get('status')}"},
            ],
            "messages": [
                {
                    "id": "msg-1",
                    "sender_type": "ai",
                    "sender_name": "Zacma AI Assistant",
                    "message": f"Welcome {matched_student.get('full_name')}! You are enrolled in {matched_student.get('course')}. Classes and orientation details will be shared once approval is finalized.",
                    "created_at": matched_student.get("created_at"),
                }
            ],
        }

    # 3. Search in Travel Requests
    travels = travel_requests_store.list_all(tenant_id)
    matched_travel = next((t for t in travels if t.get("id", "").lower() == ref_lower or ref_lower in t.get("full_name", "").lower()), None)
    if matched_travel:
        inv = invoices_store.get(matched_travel.get("linked_invoice_id", ""), tenant_id)
        return {
            "reference_code": ref,
            "id": matched_travel["id"],
            "service_type": "Travel Agent",
            "customer_name": matched_travel.get("full_name"),
            "status": matched_travel.get("status", "Pending"),
            "submission_date": matched_travel.get("created_at"),
            "package": f"Trip to {matched_travel.get('destination_country')}",
            "details": {
                "destination": matched_travel.get("destination_country"),
                "dates": matched_travel.get("preferred_travel_dates"),
                "budget": matched_travel.get("budget"),
                "ai_itinerary": matched_travel.get("ai_itinerary_draft"),
            },
            "invoice": inv or {
                "amount": matched_travel.get("advance_amount", 12000.0),
                "currency": "ETB",
                "status": "paid",
                "receiving_account": settings.default_receiving_account,
                "payment_method": matched_travel.get("advance_payment_method", "Awash"),
                "reference_code": f"ZAC-TRV-{matched_travel['id'][:4]}",
            },
            "timeline": [
                {"status": "Submitted", "timestamp": matched_travel.get("created_at"), "description": f"Travel itinerary requested for {matched_travel.get('destination_country')}"},
                {"status": matched_travel.get("status"), "timestamp": matched_travel.get("updated_at"), "description": f"Status: {matched_travel.get('status')}"},
            ],
            "messages": [
                {
                    "id": "msg-1",
                    "sender_type": "ai",
                    "sender_name": "Zacma AI Assistant",
                    "message": f"Hello {matched_travel.get('full_name')}! We are finalizing the best flight and hotel options for your journey to {matched_travel.get('destination_country')}.",
                    "created_at": matched_travel.get("created_at"),
                }
            ],
        }

    # 4. Search in Invoices by Reference Code
    invoices = invoices_store.list_all(tenant_id)
    matched_inv = next((i for i in invoices if i.get("reference_code", "").lower() == ref_lower or i.get("id", "").lower() == ref_lower), None)
    if matched_inv:
        return {
            "reference_code": matched_inv.get("reference_code", ref),
            "id": matched_inv["id"],
            "service_type": f"{matched_inv.get('module_type', 'Zacma')} Service",
            "customer_name": matched_inv.get("customer_name"),
            "status": "Confirmed" if matched_inv.get("status") == "confirmed" else "Pending Payment",
            "submission_date": matched_inv.get("created_at"),
            "package": matched_inv.get("description"),
            "details": {
                "description": matched_inv.get("description"),
                "currency": matched_inv.get("currency"),
                "amount": matched_inv.get("amount"),
            },
            "invoice": matched_inv,
            "timeline": [
                {"status": "Invoice Issued", "timestamp": matched_inv.get("created_at"), "description": f"Invoice issued for {matched_inv.get('amount')} {matched_inv.get('currency')}"},
                {"status": matched_inv.get("status", "sent").title(), "timestamp": matched_inv.get("updated_at"), "description": f"Payment status: {matched_inv.get('status')}"},
            ],
            "messages": [],
        }

    # Fallback response for newly submitted request reference
    return {
        "reference_code": ref,
        "id": ref,
        "service_type": "Zacma Service",
        "customer_name": "Valued Client",
        "status": "UnderReview",
        "submission_date": datetime.now(timezone.utc).isoformat(),
        "package": "Standard Service Request",
        "details": {"notes": "Your request has been received and is queued for verification by a Zacma specialist."},
        "invoice": {
            "amount": 5000.0,
            "currency": "ETB",
            "status": "sent",
            "receiving_account": settings.default_receiving_account,
            "payment_method": "CBE",
            "reference_code": ref,
        },
        "timeline": [
            {"status": "Submitted", "timestamp": datetime.now(timezone.utc).isoformat(), "description": "Request submitted to Zacma Platform"},
            {"status": "Under Review", "timestamp": datetime.now(timezone.utc).isoformat(), "description": "Assigned to Zacma Operations Team"},
        ],
        "messages": [
            {
                "id": "msg-welcome",
                "sender_type": "ai",
                "sender_name": "Zacma AI Assistant",
                "message": f"Welcome! We are processing your request reference #{ref}. How can we assist you today?",
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
        ],
    }


class ClientThreadMessageRequest(BaseModel):
    message: str
    sender_name: Optional[str] = "Client"
    talk_to_human: bool = False


@router.post("/track/{reference_code}/message")
def send_request_thread_message(
    reference_code: str,
    payload: ClientThreadMessageRequest,
    tenant_id: str = Depends(get_tenant_id),
):
    """Handle client messages on a request thread with Gemini AI and escalation."""
    now = datetime.now(timezone.utc).isoformat()
    client_msg = payload.message.strip()

    ai_reply_text = ""
    if payload.talk_to_human:
        ai_reply_text = (
            "🔔 Your request to speak with a human specialist has been escalated to our senior supervisor. "
            "A team member will review this thread and respond shortly during business hours (8:30 AM - 5:30 PM EAT)."
        )
    else:
        # Generate context-aware AI reply
        ai_eval = AiAssistantService.suggest_ticket_reply(
            f"Request #{reference_code}", client_msg
        )
        ai_reply_text = ai_eval.get("draft_reply") or (
            f"Thank you for your inquiry regarding request #{reference_code}. "
            "Our operations team is actively processing your files. "
            "If you need to make changes or upload additional documents, you may reply here directly."
        )

    return {
        "status": "success",
        "client_message": {
            "id": str(uuid.uuid4()),
            "sender_type": "client",
            "sender_name": payload.sender_name or "Client",
            "message": client_msg,
            "created_at": now,
        },
        "ai_response": {
            "id": str(uuid.uuid4()),
            "sender_type": "ai",
            "sender_name": "Zacma AI Assistant",
            "message": ai_reply_text,
            "created_at": now,
            "escalated_to_human": payload.talk_to_human,
        },
    }


# ---------------------------------------------------------------------------
# Telegram Bot Webhook Integration Layer (Section 9)
# ---------------------------------------------------------------------------

from app.services.telegram_bot_service import TelegramPaymentBotService


class TelegramWebhookPayload(BaseModel):
    update_id: Optional[int] = 0
    message: Optional[dict[str, Any]] = None


@router.get("/telegram/bot-info")
def get_telegram_bot_info(tenant_id: str = Depends(get_tenant_id)):
    """Get live status and identity of Zacma Telegram Bot."""
    return TelegramPaymentBotService.get_bot_info()


@router.post("/telegram/send-invoice-alert")
def send_telegram_invoice_alert(
    payload: dict[str, Any],
    tenant_id: str = Depends(get_tenant_id),
):
    """Dispatch interactive payment invoice alert via Telegram Bot."""
    chat_id = payload.get("chat_id")
    transaction = payload.get("transaction", {})
    checkout_url = payload.get("checkout_url")
    return TelegramPaymentBotService.send_payment_invoice_notification(
        transaction=transaction,
        checkout_url=checkout_url,
        chat_id=chat_id,
    )


@router.post("/telegram")
@router.post("/telegram/webhook")
def telegram_bot_webhook(
    payload: TelegramWebhookPayload,
    tenant_id: str = Depends(get_tenant_id),
):
    """Telegram Bot webhook handler for Zacma Services, Support & Payments."""
    msg = payload.message or {}
    text = (msg.get("text") or "").strip()
    chat_id = msg.get("chat", {}).get("id")
    user = msg.get("from", {})
    username = user.get("username") or user.get("first_name") or "Friend"

    reply_text = ""
    keyboard = []

    if text.startswith("/start"):
        reply_text = (
            f"👋 Hello {username}!\n\n"
            "Welcome to *Zacma Technology Group* official Telegram Bot.\n\n"
            "We provide:\n"
            "• 🎓 *Training Institute* (Programming, AI, Media, Maintenance)\n"
            "• 🛂 *Visa Assistant* (Tourist, Study, Work Visas)\n"
            "• ✈️ *Travel Agency* (Flights, Hotels, 5-Day Itineraries)\n"
            "• 📢 *Marketing Services* (Branding & Ads)\n"
            "• 💳 *Payments & Invoicing* (Chapa, Telebirr, CBE)\n\n"
            "Type a command or choose an option below:"
        )
        keyboard = [
            ["🎓 Courses", "🛂 Visa Assistance"],
            ["✈️ Travel Booking", "📢 Marketing"],
            ["💳 Payment Status", "🔍 Track My Request"],
            ["👤 Talk to Human Agent"],
        ]
    elif text.startswith("/pay") or "pay" in text.lower() or "invoice" in text.lower():
        reply_text = (
            "💳 *Zacma Payment Engine:*\n\n"
            "Supported channels:\n"
            "• 🟢 *Chapa Gateway* (Cards, CBE Birr, Telebirr)\n"
            "• 📱 *TeleBirr* Direct / USSD / QR\n"
            "• 🏦 *Commercial Bank of Ethiopia (CBE)* Account Transfer\n\n"
            "To view or pay your invoices, access: https://zacmaa.net/portal"
        )
    elif text.startswith("/courses") or "course" in text.lower() or "training" in text.lower():
        reply_text = (
            "🎓 *Zacma Training Institute Courses:*\n\n"
            "1. 💻 Programming & Full-Stack Development (4,500 ETB)\n"
            "2. 🤖 Artificial Intelligence & Machine Learning (4,500 ETB)\n"
            "3. 🎨 Graphics Design & Brand Identity (4,500 ETB)\n"
            "4. 🎬 Video Editing & Motion Graphics (4,500 ETB)\n"
            "5. 🌐 Web Design & Frontend (4,500 ETB)\n"
            "6. 🔧 Hardware Maintenance (Mobile / PC / Printer / Electronics)\n\n"
            "Apply directly on our portal: https://zacmaa.net/training"
        )
    elif text.startswith("/visa") or "visa" in text.lower():
        reply_text = (
            "🛂 *Zacma Visa Assistant:*\n\n"
            "We handle Tourist, Study, Work & Business visas for Germany, Canada, UAE, UK, Schengen & more.\n\n"
            "• Basic Guidance: 2,500 ETB\n"
            "• Standard Review: 5,000 ETB\n"
            "• Premium Concierge: 10,000 ETB\n\n"
            "Start your application at: https://zacmaa.net/visa"
        )
    elif text.startswith("/travel") or "travel" in text.lower() or "flight" in text.lower():
        reply_text = (
            "✈️ *Zacma Travel Agent:*\n\n"
            "• Flight bookings with all major carriers\n"
            "• 5-day Dubai, Istanbul, Zanzibar holiday packages\n"
            "• Hotel reservations and airport transfers\n\n"
            "Book your trip at: https://zacmaa.net/travel"
        )
    elif text.startswith("/status") or text.startswith("/track") or "track" in text.lower():
        reply_text = (
            "🔍 *Track Your Request:*\n\n"
            "Please send your Reference Number (e.g. `ZAC-VIS-4419` or `ZACMA-2026-XXXXXXXX`) or visit our web tracker at:\n"
            "https://zacmaa.net/track"
        )
    elif "human" in text.lower() or "agent" in text.lower() or text.startswith("/human"):
        reply_text = (
            "👤 *Live Agent Support:*\n\n"
            "Your message has been queued for our support staff.\n"
            "You can also call us directly at +251-911-223344 or visit our office in Addis Ababa."
        )
    else:
        # Default AI answer
        ai_res = customer_chatbot(ChatbotMessageRequest(message=text, user_name=username), tenant_id)
        reply_text = ai_res.reply

    return {
        "ok": True,
        "chat_id": chat_id,
        "reply_text": reply_text,
        "reply_markup": {"keyboard": keyboard, "resize_keyboard": True} if keyboard else None,
    }

