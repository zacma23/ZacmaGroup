"""Travel Agent Module.

Handles travel booking requests, advance payments, budget vs. quote analysis,
itinerary confirmations, and AI-suggested travel plans.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.demo_data import bookings_store, travel_requests_store
from app.core.permissions import require_role
from app.core.tenancy import get_tenant_id
from app.models import (
    BookingCreate,
    BookingResponse,
    BookingUpdate,
    TravelRequestCreate,
    TravelRequestResponse,
    TravelRequestUpdate,
)
from app.services.ai_assistant_service import AiAssistantService
from app.services.approval_service import ApprovalService
from app.services.crm_service import CrmService
from app.services.payment_service import PaymentService

router = APIRouter(prefix="/travel", tags=["travel"])


# ---------------------------------------------------------------------------
# 4.3 Travel Requests (New Core API)
# ---------------------------------------------------------------------------

@router.get("/requests", response_model=list[TravelRequestResponse])
def list_travel_requests(
    destination: str | None = None,
    status_filter: str | None = None,
    tenant_id: str = Depends(get_tenant_id),
):
    """List all travel requests with optional filtering."""
    requests = travel_requests_store.list_all(tenant_id)
    if destination:
        requests = [r for r in requests if destination.lower() in r.get("destination_country", "").lower()]
    if status_filter:
        requests = [r for r in requests if r.get("status", "").lower() == status_filter.lower()]
    return requests


@router.post("/requests", response_model=TravelRequestResponse, status_code=status.HTTP_201_CREATED)
def create_travel_request(
    payload: TravelRequestCreate,
    tenant_id: str = Depends(get_tenant_id),
):
    """Submit a new travel request.

    Automatically:
    1. Generates an AI-suggested itinerary and budget breakdown.
    2. Syncs/creates a CRM Contact with timeline history.
    3. Enters Planning approval workflow.
    """
    # 1. AI Itinerary
    ai_itinerary = AiAssistantService.suggest_itinerary(
        payload.destination_country, payload.budget, payload.travel_date_preference
    )

    data = payload.model_dump()
    data["ai_itinerary_suggestion"] = ai_itinerary["suggested_itinerary"]
    data["status"] = "Planning"
    data["quoted_price"] = payload.budget  # default initial quote

    created = travel_requests_store.create(data, tenant_id)
    trv_id = created["id"]

    # 2. CRM Contact Sync
    contact = CrmService.sync_contact(
        tenant_id=tenant_id,
        full_name=payload.full_name,
        email=payload.email,
        phone=payload.phone,
        address=payload.address,
        country=payload.country,
        source_module="Travel",
        status="Lead",
        tags=["Travel", payload.destination_country],
        initial_action=f"Requested travel to {payload.destination_country}",
        linked_entity_id=trv_id,
    )
    contact_id = contact.get("id")

    # 3. Advance Booking Invoice
    invoice = PaymentService.generate_invoice(
        tenant_id=tenant_id,
        customer_name=payload.full_name,
        customer_email=payload.email,
        contact_id=contact_id,
        module_type="Travel",
        amount=round(payload.budget * 0.20, 2),  # 20% advance deposit
        currency="ETB",
        description=f"Travel Advance Deposit: {payload.destination_country}",
        payment_method=payload.advance_payment_method,
    )

    # Link IDs
    travel_requests_store.update(
        trv_id,
        {
            "linked_crm_contact_id": contact_id,
            "linked_invoice_id": invoice.get("id"),
        },
        tenant_id,
    )

    return travel_requests_store.get(trv_id, tenant_id)


@router.get("/requests/{req_id}", response_model=TravelRequestResponse)
def get_travel_request(req_id: str, tenant_id: str = Depends(get_tenant_id)):
    """Get single travel request details."""
    req = travel_requests_store.get(req_id, tenant_id)
    if not req:
        raise HTTPException(status_code=404, detail="Travel request not found")
    return req


@router.put("/requests/{req_id}", response_model=TravelRequestResponse)
def update_travel_request(
    req_id: str,
    payload: TravelRequestUpdate,
    tenant_id: str = Depends(get_tenant_id),
):
    """Update travel request fields or set quoted price."""
    updates = payload.model_dump(exclude_unset=True)
    updated = travel_requests_store.update(req_id, updates, tenant_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Travel request not found")
    return updated


@router.post("/requests/{req_id}/approve")
def approve_travel_request(
    req_id: str,
    comment: str = "Travel request approved and booked",
    tenant_id: str = Depends(get_tenant_id),
    user: dict = Depends(require_role(["admin", "superadmin"])),
):
    """Admin approval and confirmation of travel itinerary."""
    admin_email = user.get("email", "admin@zacma.com")
    res = ApprovalService.approve(tenant_id, "travel", req_id, admin_email, comment)
    if not res:
        raise HTTPException(status_code=404, detail="Travel request not found")
    return {"status": "success", "message": "Travel request approved", "data": res}


@router.post("/requests/{req_id}/deny")
def deny_travel_request(
    req_id: str,
    reason: str,
    tenant_id: str = Depends(get_tenant_id),
    user: dict = Depends(require_role(["admin", "superadmin"])),
):
    """Admin rejection of travel request."""
    admin_email = user.get("email", "admin@zacma.com")
    res = ApprovalService.deny(tenant_id, "travel", req_id, admin_email, reason)
    if not res:
        raise HTTPException(status_code=404, detail="Travel request not found")
    return {"status": "success", "message": "Travel request denied", "data": res}


# ---------------------------------------------------------------------------
# Legacy Bookings Endpoints (Backward Compatibility)
# ---------------------------------------------------------------------------

@router.get("/bookings", response_model=list[BookingResponse])
def list_bookings(tenant_id: str = Depends(get_tenant_id)):
    return bookings_store.list_all(tenant_id)


@router.post("/bookings", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(payload: BookingCreate, tenant_id: str = Depends(get_tenant_id)):
    return bookings_store.create(payload.model_dump(), tenant_id)


@router.get("/bookings/{booking_id}", response_model=BookingResponse)
def get_booking(booking_id: str, tenant_id: str = Depends(get_tenant_id)):
    b = bookings_store.get(booking_id, tenant_id)
    if not b:
        raise HTTPException(status_code=404, detail="Booking not found")
    return b


@router.put("/bookings/{booking_id}", response_model=BookingResponse)
def update_booking(booking_id: str, payload: BookingUpdate, tenant_id: str = Depends(get_tenant_id)):
    u = bookings_store.update(booking_id, payload.model_dump(exclude_unset=True), tenant_id)
    if not u:
        raise HTTPException(status_code=404, detail="Booking not found")
    return u


@router.delete("/bookings/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_booking(booking_id: str, tenant_id: str = Depends(get_tenant_id)):
    if not bookings_store.delete(booking_id, tenant_id):
        raise HTTPException(status_code=404, detail="Booking not found")
