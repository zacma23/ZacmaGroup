"""In-memory demo data for all ZACMA platform modules and shared engines.

When Supabase is not configured (demo mode), these datasets provide realistic
sample records so the platform is immediately demonstrable without a database.
Stores are mutable — CRUD operations during a server session will persist in
memory until the process restarts.
"""

import copy
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

DEMO_TENANT_ID = "zacma-demo"

def _id() -> str:
    return str(uuid.uuid4())

def _ts(days_ago: int = 0) -> str:
    return (datetime.now(timezone.utc) - timedelta(days=days_ago)).isoformat()


# ---------------------------------------------------------------------------
# Demo Data Store generic class
# ---------------------------------------------------------------------------

class DemoStore:
    """Simple in-memory key-value store that holds demo data for one entity."""

    def __init__(self, seed: list[dict[str, Any]]):
        self._data: dict[str, dict[str, Any]] = {}
        for record in seed:
            self._data[record["id"]] = copy.deepcopy(record)

    def list_all(self, tenant_id: str) -> list[dict[str, Any]]:
        return [
            r for r in self._data.values()
            if r.get("tenant_id") == tenant_id
        ]

    def get(self, record_id: str, tenant_id: str) -> dict[str, Any] | None:
        record = self._data.get(record_id)
        if record and record.get("tenant_id") == tenant_id:
            return record
        return None

    def create(self, data: dict[str, Any], tenant_id: str) -> dict[str, Any]:
        record = copy.deepcopy(data)
        if "id" not in record or not record["id"]:
            record["id"] = _id()
        record["tenant_id"] = tenant_id
        if "created_at" not in record:
            record["created_at"] = _ts(0)
        record["updated_at"] = _ts(0)
        self._data[record["id"]] = record
        return record

    def update(self, record_id: str, updates: dict[str, Any], tenant_id: str) -> dict[str, Any] | None:
        record = self.get(record_id, tenant_id)
        if record is None:
            return None
        for key, value in updates.items():
            if value is not None:
                record[key] = value
        record["updated_at"] = _ts(0)
        return record

    def delete(self, record_id: str, tenant_id: str) -> bool:
        record = self.get(record_id, tenant_id)
        if record is None:
            return False
        del self._data[record_id]
        return True

    def count(self, tenant_id: str) -> int:
        return len(self.list_all(tenant_id))


# ---------------------------------------------------------------------------
# 3.1 CRM Engine Contacts Seed
# ---------------------------------------------------------------------------

_CRM_CONTACTS_SEED: list[dict[str, Any]] = [
    {
        "id": "c-001",
        "tenant_id": DEMO_TENANT_ID,
        "full_name": "Abebe Bikila",
        "email": "abebe.bikila@example.com",
        "phone": "+251911223344",
        "address": "Bole Sub-City, Addis Ababa",
        "country": "Ethiopia",
        "source_module": "Student",
        "status": "Active",
        "tags": ["Student", "Web Design", "Paid"],
        "assigned_admin_id": "admin@zacma.com",
        "timeline": [
            {"id": _id(), "timestamp": _ts(5), "action": "Registration", "description": "Enrolled in Web Design", "actor": "client"},
            {"id": _id(), "timestamp": _ts(4), "action": "Invoice", "description": "Generated invoice INV-2026-001 for 4,500 ETB", "actor": "system"},
            {"id": _id(), "timestamp": _ts(3), "action": "Payment", "description": "Confirmed TeleBirr payment", "actor": "admin@zacma.com"},
            {"id": _id(), "timestamp": _ts(2), "action": "Approval", "description": "Student registration approved", "actor": "admin@zacma.com"},
        ],
        "notes_list": [
            {"id": _id(), "author": "admin@zacma.com", "content": "Fast learner, completed onboarding.", "created_at": _ts(2)}
        ],
        "linked_registration_ids": ["reg-001"],
        "linked_invoice_ids": ["inv-001"],
        "linked_ticket_ids": [],
        "created_at": _ts(5),
        "updated_at": _ts(2),
    },
    {
        "id": "c-002",
        "tenant_id": DEMO_TENANT_ID,
        "full_name": "Tigist Assefa",
        "email": "tigist.a@example.com",
        "phone": "+251922334455",
        "address": "Kazanchis, Addis Ababa",
        "country": "Ethiopia",
        "source_module": "Visa",
        "status": "Active",
        "tags": ["Visa", "Tourist", "Germany"],
        "assigned_admin_id": "admin@zacma.com",
        "timeline": [
            {"id": _id(), "timestamp": _ts(3), "action": "Visa Application", "description": "Applied for Germany Tourist Visa", "actor": "client"},
            {"id": _id(), "timestamp": _ts(3), "action": "Invoice", "description": "Generated advance invoice INV-2026-002 for 5,000 ETB", "actor": "system"},
        ],
        "notes_list": [],
        "linked_registration_ids": ["visa-001"],
        "linked_invoice_ids": ["inv-002"],
        "linked_ticket_ids": [],
        "created_at": _ts(3),
        "updated_at": _ts(3),
    },
    {
        "id": "c-003",
        "tenant_id": DEMO_TENANT_ID,
        "full_name": "Yonas Mulugeta",
        "email": "yonas.m@example.com",
        "phone": "+251933445566",
        "address": "Hawassa",
        "country": "Ethiopia",
        "source_module": "Travel",
        "status": "Lead",
        "tags": ["Travel", "Dubai", "Flight"],
        "assigned_admin_id": None,
        "timeline": [
            {"id": _id(), "timestamp": _ts(2), "action": "Travel Request", "description": "Trip to Dubai requested (Budget: 35,000 ETB)", "actor": "client"}
        ],
        "notes_list": [],
        "linked_registration_ids": ["trv-001"],
        "linked_invoice_ids": [],
        "linked_ticket_ids": [],
        "created_at": _ts(2),
        "updated_at": _ts(2),
    },
    {
        "id": "c-004",
        "tenant_id": DEMO_TENANT_ID,
        "full_name": "Sara Haile",
        "email": "sara.h@example.com",
        "phone": "+251944556677",
        "address": "Bishoftu",
        "country": "Ethiopia",
        "source_module": "Support",
        "status": "Active",
        "tags": ["Support", "Course Inquiry"],
        "assigned_admin_id": "staff@zacma.com",
        "timeline": [
            {"id": _id(), "timestamp": _ts(1), "action": "Support Ticket", "description": "Opened ticket: Inquiry on AI course schedule", "actor": "client"}
        ],
        "notes_list": [],
        "linked_registration_ids": [],
        "linked_invoice_ids": [],
        "linked_ticket_ids": ["tkt-001"],
        "created_at": _ts(1),
        "updated_at": _ts(1),
    }
]


# ---------------------------------------------------------------------------
# 3.2 Payment Engine Invoices Seed
# ---------------------------------------------------------------------------

_INVOICES_SEED: list[dict[str, Any]] = [
    {
        "id": "inv-001",
        "tenant_id": DEMO_TENANT_ID,
        "customer_name": "Abebe Bikila",
        "customer_email": "abebe.bikila@example.com",
        "contact_id": "c-001",
        "module_type": "Student",
        "amount": 4500.00,
        "currency": "ETB",
        "payment_method": "TeleBirr",
        "receiving_account": None,
        "reference_code": "ZAC-STU-8821",
        "due_date": _ts(-5),
        "description": "Enrollment Fee: Web Design Course",
        "status": "confirmed",
        "payment_attempts": [
            {"gateway": "TeleBirr", "reference_number": "TB-998877", "timestamp": _ts(3), "status": "confirmed"}
        ],
        "confirmed_by": "admin@zacma.com",
        "confirmed_at": _ts(3),
        "created_at": _ts(4),
        "updated_at": _ts(3),
    },
    {
        "id": "inv-002",
        "tenant_id": DEMO_TENANT_ID,
        "customer_name": "Tigist Assefa",
        "customer_email": "tigist.a@example.com",
        "contact_id": "c-002",
        "module_type": "Visa",
        "amount": 5000.00,
        "currency": "ETB",
        "payment_method": "CBE",
        "receiving_account": None,
        "reference_code": "ZAC-VIS-4419",
        "due_date": _ts(-2),
        "description": "Advance Processing Fee: Germany Tourist Visa",
        "status": "sent",
        "payment_attempts": [],
        "created_at": _ts(3),
        "updated_at": _ts(3),
    },
    {
        "id": "inv-003",
        "tenant_id": DEMO_TENANT_ID,
        "customer_name": "Dawit Tesfaye",
        "customer_email": "dawit.t@example.com",
        "contact_id": "c-003",
        "module_type": "Travel",
        "amount": 12000.00,
        "currency": "ETB",
        "payment_method": "Awash",
        "receiving_account": None,
        "reference_code": "ZAC-TRV-1044",
        "due_date": _ts(-7),
        "description": "Advance Booking Deposit: Dubai Trip",
        "status": "paid",
        "payment_attempts": [
            {"gateway": "Awash", "reference_number": "AW-554433", "timestamp": _ts(1), "status": "pending_confirmation"}
        ],
        "created_at": _ts(7),
        "updated_at": _ts(1),
    }
]


# ---------------------------------------------------------------------------
# 3.2.1 Multi-Provider Platform Seeds (Providers, Transactions, Balances)
# ---------------------------------------------------------------------------

_PAYMENT_PROVIDERS_SEED: list[dict[str, Any]] = [
    {
        "id": "prov-santimpay",
        "tenant_id": DEMO_TENANT_ID,
        "provider_name": "SantimPay Payment Gateway",
        "provider_code": "santimpay",
        "provider_type": "gateway",
        "is_active": True,
        "is_default": True,
        "priority": 1,
        "environment": "test",
        "currency": "ETB",
        "supported_currencies": ["ETB"],
        "account_name": "Zacma Technology Group",
        "account_number": None,
        "customer_payment_number": None,
        "instructions": "Instant online checkout via SantimPay (Telebirr, CBE Birr, Cards, Awash, Abyssinia).",
        "api_endpoint": "https://services.santimpay.com/api/v1/gateway",
        "callback_url": "/portal",
        "webhook_url": "/api/v1/payments/webhooks/santimpay",
        "supports_balance_api": True,
        "transaction_fee_percent": 2.5,
        "transaction_fee_fixed": 0.0,
        "has_secret_key": True,
        "secret_key": "santim_priv_mock_key",
        "api_key": "santim_pub_mock_key",
        "public_key": "-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEEcfE9DYOz/pkenjJ4Abdgr2BsYB5\nzhh+3RxlHA+ZDlQ63+RTJS2BA2vqUeASic2BPMd+LqrAlo+5nCLqdBm//g==\n-----END PUBLIC KEY-----",
        "webhook_secret": "santim_webhook_mock_secret",
        "merchant_id": "merchant-santim-01",
        "masked_secret_key": "santim_sec_••••••••••••",
        "masked_api_key": "santim_pub_••••••••••••",
        "created_at": _ts(30),
        "updated_at": _ts(1),
    },
    {
        "id": "prov-cbe",
        "tenant_id": DEMO_TENANT_ID,
        "provider_name": "Commercial Bank of Ethiopia (CBE)",
        "provider_code": "cbe",
        "provider_type": "bank_transfer",
        "is_active": True,
        "is_default": False,
        "priority": 2,
        "environment": "live",
        "currency": "ETB",
        "supported_currencies": ["ETB"],
        "account_name": "Zacma Technology Group PLC",
        "account_number": "1000000000001",
        "customer_payment_number": "CBE-ZACMA-PAY",
        "instructions": "Transfer to CBE Account, use transaction reference as payment description, and upload receipt in portal.",
        "api_endpoint": None,
        "callback_url": None,
        "webhook_url": None,
        "supports_balance_api": False,
        "transaction_fee_percent": 0.0,
        "transaction_fee_fixed": 0.0,
        "has_secret_key": False,
        "secret_key": None,
        "api_key": None,
        "webhook_secret": None,
        "merchant_id": None,
        "masked_secret_key": None,
        "masked_api_key": None,
        "created_at": _ts(30),
        "updated_at": _ts(1),
    },
    {
        "id": "prov-telebirr",
        "tenant_id": DEMO_TENANT_ID,
        "provider_name": "Telebirr Mobile Money",
        "provider_code": "telebirr",
        "provider_type": "mobile_money",
        "is_active": True,
        "is_default": False,
        "priority": 3,
        "environment": "live",
        "currency": "ETB",
        "supported_currencies": ["ETB"],
        "account_name": "Zacma Technology Group",
        "account_number": None,
        "customer_payment_number": "+251911000001",
        "instructions": "Send via Telebirr app or *127# to merchant number, enter reference code, and upload screenshot in portal.",
        "api_endpoint": None,
        "callback_url": None,
        "webhook_url": None,
        "supports_balance_api": False,
        "transaction_fee_percent": 0.0,
        "transaction_fee_fixed": 0.0,
        "has_secret_key": False,
        "secret_key": None,
        "api_key": None,
        "webhook_secret": None,
        "merchant_id": "TB-MERCHANT-8822",
        "masked_secret_key": None,
        "masked_api_key": None,
        "created_at": _ts(30),
        "updated_at": _ts(1),
    },
    {
        "id": "prov-awash",
        "tenant_id": DEMO_TENANT_ID,
        "provider_name": "Awash Bank",
        "provider_code": "awash",
        "provider_type": "bank_transfer",
        "is_active": True,
        "is_default": False,
        "priority": 4,
        "environment": "live",
        "currency": "ETB",
        "supported_currencies": ["ETB"],
        "account_name": "Zacma Technology Group PLC",
        "account_number": "0130000000000",
        "customer_payment_number": "AWASH-ZACMA",
        "instructions": "Transfer to Awash Bank Account and upload payment receipt in portal.",
        "api_endpoint": None,
        "callback_url": None,
        "webhook_url": None,
        "supports_balance_api": False,
        "transaction_fee_percent": 0.0,
        "transaction_fee_fixed": 0.0,
        "has_secret_key": False,
        "secret_key": None,
        "api_key": None,
        "webhook_secret": None,
        "merchant_id": None,
        "masked_secret_key": None,
        "masked_api_key": None,
        "created_at": _ts(30),
        "updated_at": _ts(1),
    }
]

_PAYMENT_TRANSACTIONS_SEED: list[dict[str, Any]] = [
    {
        "id": "tx-001",
        "tenant_id": DEMO_TENANT_ID,
        "public_reference": "ZACMA-2026-9A7B3E1F",
        "customer_id": "c-001",
        "customer_name": "Abebe Bikila",
        "customer_email": "abebe.bikila@example.com",
        "customer_phone": "+251911223344",
        "provider_id": "prov-telebirr",
        "provider_code": "telebirr",
        "payment_method": "TeleBirr",
        "amount": 4500.00,
        "fee": 0.00,
        "net_amount": 4500.00,
        "currency": "ETB",
        "status": "successful",
        "payment_purpose": "Training Course Tuition",
        "description": "Enrollment Fee: Web Design Course",
        "invoice_id": "inv-001",
        "provider_transaction_id": "TB-TX-882211",
        "provider_reference": "TB-REF-998877",
        "checkout_url": None,
        "callback_status": "received",
        "verification_status": "verified",
        "created_at": _ts(4),
        "updated_at": _ts(3),
        "completed_at": _ts(3),
    },
    {
        "id": "tx-002",
        "tenant_id": DEMO_TENANT_ID,
        "public_reference": "ZACMA-2026-4B8C1D2E",
        "customer_id": "c-002",
        "customer_name": "Tigist Assefa",
        "customer_email": "tigist.a@example.com",
        "customer_phone": "+251922334455",
        "provider_id": "prov-cbe",
        "provider_code": "cbe",
        "payment_method": "CBE",
        "amount": 5000.00,
        "fee": 0.00,
        "net_amount": 5000.00,
        "currency": "ETB",
        "status": "pending",
        "payment_purpose": "Visa Processing Advance",
        "description": "Advance Processing Fee: Germany Tourist Visa",
        "invoice_id": "inv-002",
        "provider_transaction_id": None,
        "provider_reference": None,
        "checkout_url": None,
        "callback_status": None,
        "verification_status": "unverified",
        "created_at": _ts(3),
        "updated_at": _ts(3),
        "completed_at": None,
    },
    {
        "id": "tx-003",
        "tenant_id": DEMO_TENANT_ID,
        "public_reference": "ZACMA-2026-7F3E5A1C",
        "customer_id": "c-003",
        "customer_name": "Dawit Tesfaye",
        "customer_email": "dawit.t@example.com",
        "customer_phone": "+251933445566",
        "provider_id": "prov-chapa",
        "provider_code": "chapa",
        "payment_method": "Chapa",
        "amount": 12000.00,
        "fee": 420.00,
        "net_amount": 11580.00,
        "currency": "ETB",
        "status": "successful",
        "payment_purpose": "Travel Booking Deposit",
        "description": "Advance Booking Deposit: Dubai Trip",
        "invoice_id": "inv-003",
        "provider_transaction_id": "chapa_tx_889900",
        "provider_reference": "chapa_ref_112233",
        "checkout_url": "https://checkout.chapa.co/checkout/payment/mock-tx-003",
        "callback_status": "success",
        "verification_status": "verified",
        "created_at": _ts(7),
        "updated_at": _ts(1),
        "completed_at": _ts(1),
    }
]

_PAYMENT_WEBHOOKS_SEED: list[dict[str, Any]] = []

_PAYMENT_LOGS_SEED: list[dict[str, Any]] = [
    {
        "id": "plog-001",
        "tenant_id": DEMO_TENANT_ID,
        "actor": "system",
        "action": "Provider Initialized",
        "resource_type": "payment_provider",
        "resource_id": "prov-santimpay",
        "details": {"provider_code": "santimpay", "status": "active"},
        "ip_address": "127.0.0.1",
        "created_at": _ts(30),
    }
]


# ---------------------------------------------------------------------------
# 4.1 Student Registrations Seed (Training Institute)
# ---------------------------------------------------------------------------

_STUDENTS_SEED: list[dict[str, Any]] = [
    {
        "id": "reg-001",
        "tenant_id": DEMO_TENANT_ID,
        "reference_code": "ZAC-STU-1001",
        "full_name": "Abebe Bikila",
        "address": "Bole Sub-City, Addis Ababa",
        "phone": "+251911223344",
        "email": "abebe.bikila@example.com",
        "education_level": "Bachelor's Degree",
        "course": "Web Design",
        "specialty": None,
        "schedule": "Monday + Wednesday + Thursday",
        "time_slot": "09:00 – 11:00",
        "time": "09:00 – 11:00",
        "maintenance_sub_type": None,
        "payment_method": "TeleBirr",
        "status": "Approved",
        "attendance": [
            {"session_date": _ts(3), "session_title": "HTML5 & Modern Layouts", "present": True, "notes": "On time"},
            {"session_date": _ts(1), "session_title": "CSS Grid & Flexbox", "present": True, "notes": "Active in lab"}
        ],
        "linked_crm_contact_id": "c-001",
        "linked_invoice_id": "inv-001",
        "ai_course_recommendation": "Recommended Web Design based on interest in digital marketing and UI.",
        "created_at": _ts(5),
        "updated_at": _ts(2),
    },
    {
        "id": "reg-002",
        "tenant_id": DEMO_TENANT_ID,
        "reference_code": "ZAC-STU-1002",
        "full_name": "Marta Gebre",
        "address": "Megenagna, Addis Ababa",
        "phone": "+251922889900",
        "email": "marta.g@example.com",
        "education_level": "Diploma",
        "course": "Maintenance",
        "specialty": "Hardware Specialty",
        "schedule": "Monday + Wednesday + Thursday",
        "time_slot": "03:00 – 05:00",
        "time": "03:00 – 05:00",
        "maintenance_sub_type": "Hardware Specialty",
        "payment_method": "CBE",
        "status": "Pending",
        "attendance": [],
        "linked_crm_contact_id": None,
        "linked_invoice_id": None,
        "ai_course_recommendation": "Recommended Maintenance (Hardware Specialty) based on interest in electronics diagnostics.",
        "created_at": _ts(1),
        "updated_at": _ts(1),
    }
]


# ---------------------------------------------------------------------------
# 4.2 Visa Applications Seed
# ---------------------------------------------------------------------------

_VISA_APPLICATIONS_SEED: list[dict[str, Any]] = [
    {
        "id": "visa-001",
        "tenant_id": DEMO_TENANT_ID,
        "full_name": "Tigist Assefa",
        "address": "Kazanchis, Addis Ababa",
        "phone": "+251922334455",
        "email": "tigist.a@example.com",
        "country": "Ethiopia",
        "destination_country": "Germany",
        "visa_type": "Tourist",
        "passport_upload_url": "/uploads/passports/passport_tigist.pdf",
        "supporting_document_urls": [
            "/uploads/docs/bank_statement_tigist.pdf",
            "/uploads/docs/hotel_booking_tigist.pdf"
        ],
        "advance_payment_method": "CBE",
        "advance_amount": 5000.0,
        "status": "UnderReview",
        "linked_crm_contact_id": "c-002",
        "linked_invoice_id": "inv-002",
        "notes": "Flight itinerary verified. Bank balance meets embassy criteria.",
        "ai_document_check_summary": "All required documents present. Passport expiry is > 6 months (valid).",
        "created_at": _ts(3),
        "updated_at": _ts(2),
    },
    {
        "id": "visa-002",
        "tenant_id": DEMO_TENANT_ID,
        "full_name": "Kiros Alemayehu",
        "address": "Adama",
        "phone": "+251933778899",
        "email": "kiros.a@example.com",
        "country": "Ethiopia",
        "destination_country": "Canada",
        "visa_type": "Study",
        "passport_upload_url": "/uploads/passports/passport_kiros.pdf",
        "supporting_document_urls": ["/uploads/docs/acceptance_letter_ubc.pdf"],
        "advance_payment_method": "TeleBirr",
        "advance_amount": 7500.0,
        "status": "DocumentsRequested",
        "linked_crm_contact_id": None,
        "linked_invoice_id": None,
        "notes": "Requested certified bank statement and police clearance.",
        "ai_document_check_summary": "Missing police clearance certificate and proof of tuition deposit.",
        "created_at": _ts(2),
        "updated_at": _ts(1),
    }
]


# ---------------------------------------------------------------------------
# 4.3 Travel Requests Seed
# ---------------------------------------------------------------------------

_TRAVEL_REQUESTS_SEED: list[dict[str, Any]] = [
    {
        "id": "trv-001",
        "tenant_id": DEMO_TENANT_ID,
        "full_name": "Yonas Mulugeta",
        "address": "Hawassa",
        "phone": "+251933445566",
        "email": "yonas.m@example.com",
        "country": "Ethiopia",
        "destination_country": "United Arab Emirates (Dubai)",
        "budget": 35000.0,
        "quoted_price": 32500.0,
        "passport_upload_url": "/uploads/passports/passport_yonas.pdf",
        "advance_payment_method": "TeleBirr",
        "travel_date_preference": "2026-10-15 to 2026-10-25",
        "status": "Planning",
        "linked_crm_contact_id": "c-003",
        "linked_invoice_id": None,
        "notes": "Prefers Emirates or Ethiopian Airlines. 4-star hotel in Deira.",
        "ai_itinerary_suggestion": "5-day Dubai City Tour + Desert Safari. Estimated flights: 22,000 ETB, Hotel: 10,500 ETB.",
        "created_at": _ts(2),
        "updated_at": _ts(1),
    }
]


# ---------------------------------------------------------------------------
# 4.4 Customer Support Tickets Seed
# ---------------------------------------------------------------------------

_SUPPORT_TICKETS_SEED: list[dict[str, Any]] = [
    {
        "id": "tkt-001",
        "tenant_id": DEMO_TENANT_ID,
        "full_name": "Sara Haile",
        "email": "sara.h@example.com",
        "phone": "+251944556677",
        "subject": "Inquiry on AI Course Schedule and Prerequisites",
        "message": "Hello Zacma team, I would like to know if the AI course is available on weekends and what the prerequisites are.",
        "category": "Training",
        "priority": "Medium",
        "status": "Open",
        "assigned_admin_id": "staff@zacma.com",
        "thread": [
            {"id": _id(), "sender_type": "client", "sender_name": "Sara Haile", "message": "Hello Zacma team, I would like to know if the AI course is available on weekends and what the prerequisites are.", "created_at": _ts(1)}
        ],
        "ai_suggested_reply": "Dear Sara, thank you for reaching out! Our AI fundamentals course is offered every Saturday (9:00 AM - 1:00 PM). Basic computer skills and high school math are recommended prerequisites.",
        "linked_crm_contact_id": "c-004",
        "created_at": _ts(1),
        "updated_at": _ts(1),
    }
]


# ---------------------------------------------------------------------------
# 6. Dynamic Module System Seed (BusinessModule & FieldDefinitions)
# ---------------------------------------------------------------------------

_BUSINESS_MODULES_SEED: list[dict[str, Any]] = [
    {
        "id": "mod-001",
        "tenant_id": DEMO_TENANT_ID,
        "name": "Real Estate Listing & Rental",
        "key": "real_estate",
        "description": "Property buy, sell, and rental listing intake service.",
        "is_active": True,
        "icon_url": "Home",
        "requires_payment": True,
        "base_amount": 1500.0,
        "fields": [
            {"id": _id(), "field_name": "property_type", "label": "Property Type", "field_type": "dropdown", "is_required": True, "options": ["Apartment", "Villa", "Commercial Building", "Land"], "help_text": "Select property category", "order": 1},
            {"id": _id(), "field_name": "listing_purpose", "label": "Listing Purpose", "field_type": "dropdown", "is_required": True, "options": ["For Sale", "For Rent"], "help_text": "Sale or rental", "order": 2},
            {"id": _id(), "field_name": "location", "label": "Property Location (City / Sub-city)", "field_type": "text", "is_required": True, "options": [], "help_text": "e.g., Bole, Addis Ababa", "order": 3},
            {"id": _id(), "field_name": "target_price", "label": "Target Price (ETB)", "field_type": "number", "is_required": True, "options": [], "help_text": "Expected price in ETB", "order": 4},
            {"id": _id(), "field_name": "property_document", "label": "Ownership Title Deed (PDF/Image)", "field_type": "file", "is_required": False, "options": [], "help_text": "Upload property proof", "order": 5},
        ],
        "created_at": _ts(10),
    },
    {
        "id": "mod-002",
        "tenant_id": DEMO_TENANT_ID,
        "name": "Business Legal & Trademark Consultancy",
        "key": "legal_consulting",
        "description": "Company registration, TIN, and trademark filing consultancy.",
        "is_active": True,
        "icon_url": "Briefcase",
        "requires_payment": True,
        "base_amount": 3000.0,
        "fields": [
            {"id": _id(), "field_name": "service_type", "label": "Consultancy Type", "field_type": "dropdown", "is_required": True, "options": ["New Company Registration", "Trademark Filing", "Tax/TIN Setup", "Contract Review"], "help_text": "Desired legal service", "order": 1},
            {"id": _id(), "field_name": "business_sector", "label": "Business Sector", "field_type": "text", "is_required": True, "options": [], "help_text": "e.g., Tech, Import/Export, Hospitality", "order": 2},
            {"id": _id(), "field_name": "notes", "label": "Additional Requirements", "field_type": "textarea", "is_required": False, "options": [], "help_text": "Describe your business needs", "order": 3},
        ],
        "created_at": _ts(8),
    }
]

_MODULE_SUBMISSIONS_SEED: list[dict[str, Any]] = [
    {
        "id": "sub-001",
        "tenant_id": DEMO_TENANT_ID,
        "module_id": "mod-001",
        "module_key": "real_estate",
        "full_name": "Kassahun Tadesse",
        "email": "kassahun.t@example.com",
        "phone": "+251955667788",
        "data_json": {
            "property_type": "Villa",
            "listing_purpose": "For Sale",
            "location": "CMC, Addis Ababa",
            "target_price": 18500000,
            "property_document": "/uploads/docs/title_deed_kassahun.pdf"
        },
        "status": "Pending",
        "linked_crm_contact_id": None,
        "linked_invoice_id": None,
        "created_at": _ts(1),
        "updated_at": _ts(1),
    }
]


# ---------------------------------------------------------------------------
# Notification Templates Seed
# ---------------------------------------------------------------------------

_NOTIFICATION_TEMPLATES_SEED: list[dict[str, Any]] = [
    {
        "id": "tmpl-invoice",
        "tenant_id": DEMO_TENANT_ID,
        "key": "invoice_created",
        "subject": "Zacma Invoice {reference_code} — {module_type} Service",
        "body_template": (
            "Dear {customer_name},\n\n"
            "Thank you for choosing Zacma. Your invoice #{reference_code} has been generated.\n\n"
            "Amount Due: {amount} {currency}\n"
            "Service: {description}\n"
            "Payment Method: {payment_method}\n"
            "Official Receiving Account: {receiving_account}\n\n"
            "Please include reference code '{reference_code}' when making your transfer.\n\n"
            "Best regards,\nZacma Management Team"
        ),
        "description": "Sent when an invoice is generated for any module.",
    },
    {
        "id": "tmpl-paid",
        "tenant_id": DEMO_TENANT_ID,
        "key": "payment_confirmed",
        "subject": "Payment Confirmed — Invoice {reference_code}",
        "body_template": (
            "Dear {customer_name},\n\n"
            "We have successfully received and confirmed your payment of {amount} {currency} for {description}.\n\n"
            "Your application/enrollment is now being processed.\n\n"
            "Best regards,\nZacma Operations"
        ),
        "description": "Sent when payment is marked confirmed by admin.",
    },
    {
        "id": "tmpl-approved",
        "tenant_id": DEMO_TENANT_ID,
        "key": "registration_approved",
        "subject": "Congratulations! Your Zacma Application has been Approved",
        "body_template": (
            "Dear {full_name},\n\n"
            "We are pleased to inform you that your {module_type} application ({item_title}) has been APPROVED.\n\n"
            "Details: {comment}\n\n"
            "Thank you for choosing Zacma!\nZacma Team"
        ),
        "description": "Sent upon approval of student, visa, travel, or dynamic module submissions.",
    }
]


# ---------------------------------------------------------------------------
# System Settings Seed
# ---------------------------------------------------------------------------

_SYSTEM_SETTINGS_SEED: list[dict[str, Any]] = [
    {
        "id": "sys-settings-001",
        "tenant_id": DEMO_TENANT_ID,
        "default_payment_methods": ["SantimPay", "CBE", "TeleBirr", "Awash", "Abyssinia"],
        "courses_list": [
            "Graphics Design", "Video Editing", "Web Design", "Programming", "AI", "Accounting", "Maintenance"
        ],
        "visa_types_list": ["Tourist", "Work", "Study", "Business"],
        "education_levels_list": ["High School", "Diploma", "Bachelor's Degree", "Master's Degree", "Other"],
        "created_at": _ts(30),
        "updated_at": _ts(0),
    }
]


# ---------------------------------------------------------------------------
# Legacy stores from Phase 1
# ---------------------------------------------------------------------------

_LEADS_SEED: list[dict[str, Any]] = [
    {"id": _id(), "tenant_id": DEMO_TENANT_ID, "name": "Sarah Johnson", "email": "sarah.j@techcorp.com", "company": "TechCorp", "phone": "+1-555-0101", "source": "website", "status": "new", "notes": "Interested in visa services", "created_at": _ts(1)},
    {"id": _id(), "tenant_id": DEMO_TENANT_ID, "name": "Michael Chen", "email": "m.chen@globalfin.co", "company": "Global Finance", "phone": "+1-555-0102", "source": "referral", "status": "contacted", "notes": "CFO referral, needs travel management", "created_at": _ts(2)},
]

_EMPLOYEES_SEED: list[dict[str, Any]] = [
    {"id": _id(), "tenant_id": DEMO_TENANT_ID, "full_name": "Alex Thompson", "email": "alex.t@zacma.com", "department": "engineering", "role": "senior_engineer", "status": "active", "created_at": _ts(90)},
    {"id": _id(), "tenant_id": DEMO_TENANT_ID, "full_name": "Maria Garcia", "email": "maria.g@zacma.com", "department": "operations", "role": "ops_manager", "status": "active", "created_at": _ts(120)},
]

_COURSES_SEED: list[dict[str, Any]] = [
    {"id": _id(), "tenant_id": DEMO_TENANT_ID, "title": "Web Design & Frontend Development", "description": "HTML5, CSS3, Tailwind, Next.js", "instructor": "Abebe Tech", "capacity": 30, "enrolled": 15, "start_date": _ts(-14), "status": "active", "created_at": _ts(45)},
    {"id": _id(), "tenant_id": DEMO_TENANT_ID, "title": "Artificial Intelligence & Applied ML", "description": "Practical AI applications and automation", "instructor": "Dr. Haile", "capacity": 25, "enrolled": 20, "start_date": _ts(-7), "status": "active", "created_at": _ts(30)},
]

_BOOKINGS_SEED: list[dict[str, Any]] = [
    {"id": _id(), "tenant_id": DEMO_TENANT_ID, "traveler_name": "Yonas Mulugeta", "destination": "Dubai, UAE", "departure_date": _ts(-5), "return_date": _ts(-1), "booking_type": "flight", "status": "confirmed", "notes": "Emirates flight", "created_at": _ts(14)},
]

_CAMPAIGNS_SEED: list[dict[str, Any]] = [
    {"id": _id(), "tenant_id": DEMO_TENANT_ID, "name": "Q3 Course Enrollment Drive", "channel": "social", "budget": 15000.00, "start_date": _ts(-30), "end_date": _ts(30), "status": "active", "description": "Facebook and Telegram campaigns", "created_at": _ts(35)},
]

_ADMIN_USERS_SEED: list[dict[str, Any]] = [
    {"id": "usr-admin-root", "tenant_id": DEMO_TENANT_ID, "email": "zacma@admin", "username": "zacma@admin", "full_name": "Zacma Administrator", "role": "admin", "status": "active", "created_at": _ts(365)},
    {"id": _id(), "tenant_id": DEMO_TENANT_ID, "email": "admin@zacma.com", "full_name": "Zacma Admin", "role": "admin", "status": "active", "created_at": _ts(365)},
    {"id": _id(), "tenant_id": DEMO_TENANT_ID, "email": "staff@zacma.com", "full_name": "Zacma Staff", "role": "staff", "status": "active", "created_at": _ts(180)},
    {"id": _id(), "tenant_id": DEMO_TENANT_ID, "email": "finance@zacma.com", "full_name": "Zacma Finance", "role": "finance", "status": "active", "created_at": _ts(120)},
    {"id": _id(), "tenant_id": DEMO_TENANT_ID, "email": "client@zacma.com", "full_name": "Demo Client", "role": "client", "status": "active", "created_at": _ts(90)},
]

_AUDIT_LOGS_SEED: list[dict[str, Any]] = [
    {"id": _id(), "timestamp": _ts(0), "action": "LOGIN", "user_email": "admin@zacma.com", "tenant_id": DEMO_TENANT_ID, "resource": "auth", "details": "Admin login from 192.168.1.1"},
    {"id": _id(), "timestamp": _ts(0), "action": "APPROVE", "user_email": "admin@zacma.com", "tenant_id": DEMO_TENANT_ID, "resource": "students/registrations", "details": "Approved student Abebe Bikila"},
    {"id": _id(), "timestamp": _ts(1), "action": "CONFIRM_PAYMENT", "user_email": "finance@zacma.com", "tenant_id": DEMO_TENANT_ID, "resource": "payments/invoices", "details": "Confirmed invoice INV-2026-001 (TeleBirr)"},
]


_SOFTWARE_PROJECTS_SEED: list[dict[str, Any]] = [
    {
        "id": _id(),
        "tenant_id": DEMO_TENANT_ID,
        "reference_code": "ZAC-DEV-1001",
        "project_name": "Healthcare Telemedicine & Pharmacy Mobile App",
        "client_name": "Abebe Telehealth Solutions",
        "email": "client@zacma.com",
        "phone": "+251911445566",
        "industry": "Healthcare & Pharmaceuticals",
        "platforms": ["Android", "iOS", "Web", "Cloud"],
        "project_description": "Cross-platform mobile application with doctor appointment scheduling, real-time video consultation, prescription management, and local payment integration.",
        "problem_to_solve": "Patients currently wait 3+ hours at clinics. Need automated booking, remote consultations, and TeleBirr/CBE payment for prescription deliveries.",
        "required_features": [
            "Patient & Doctor Onboarding & KYC",
            "Video Consultation via WebRTC",
            "Prescription Order & Delivery Tracking",
            "TeleBirr & CBE Birr Payment Gateways",
            "Admin & Clinic Analytics Dashboard",
        ],
        "target_users": "Patients, Specialist Physicians, Clinic Administrators, Pharmacists",
        "ai_requirements": "AI symptom pre-screening bot and auto-transcription for doctor notes.",
        "integration_requirements": "TeleBirr API, CBE Birr Merchant API, SMS OTP Gateway.",
        "design_requirements": "Clean, accessible mobile UI with Amharic and English language support.",
        "expected_timeline": "10-12 Weeks",
        "budget": 120000.0,
        "currency": "ETB",
        "advance_payment_method": "CBE",
        "advance_amount": 25000.0,
        "status": "Pending",
        "payment_status": "Pending",
        "created_at": _ts(2),
    },
    {
        "id": _id(),
        "tenant_id": DEMO_TENANT_ID,
        "reference_code": "ZAC-DEV-1002",
        "project_name": "Multi-Branch Retail Inventory & POS Cloud System",
        "client_name": "Addis Distribution Supermarkets",
        "email": "retail@addisdist.com",
        "phone": "+251911778899",
        "industry": "Retail & Supply Chain",
        "platforms": ["Desktop", "Web", "Cloud"],
        "project_description": "Custom ERP & Point of Sale with real-time barcode scanning, multi-warehouse stock sync, and automated reorder alerts.",
        "problem_to_solve": "Stock discrepancies between 5 branch stores and warehouse.",
        "required_features": [
            "Offline-capable Desktop POS",
            "Central Cloud Inventory Sync",
            "Barcode & Receipt Printing",
            "Sales & Tax Audit Reports",
        ],
        "target_users": "Cashiers, Store Managers, Warehouse Clerks, Financial Controllers",
        "ai_requirements": "Demand forecasting and stock optimization AI.",
        "integration_requirements": "Zacma ERP (https://erp.zacmaa.net/) integration, Thermal POS Printers.",
        "design_requirements": "High-contrast dark/light mode for touch monitors.",
        "expected_timeline": "8 Weeks",
        "budget": 85000.0,
        "currency": "ETB",
        "advance_payment_method": "TeleBirr",
        "advance_amount": 20000.0,
        "status": "PaymentApproved",
        "payment_status": "Paid",
        "created_at": _ts(5),
    }
]

_KNOWLEDGE_BASE_SEED: list[dict[str, Any]] = [
    {
        "id": "kb-company",
        "tenant_id": DEMO_TENANT_ID,
        "category": "Company Information",
        "title": "About Zacma Technology Group",
        "content": (
            "Zacma Technology Group is a leading technology, consulting, and multi-service enterprise headquartered in Addis Ababa, Ethiopia. "
            "The group operates 5 primary service divisions (Software Development, Visa Consulting, Travel Agency, Training Institute, Marketing Solutions) "
            "and 4 official enterprise platforms (ERP, MySchool, E-Commerce, Freelancer). "
            "Payment Methods: Instant Online Checkout via SantimPay, Commercial Bank of Ethiopia (CBE), TeleBirr, Awash Bank, and Bank of Abyssinia. "
            "Official Contact: +251-911-000000, support@zacma.com, info@zacma.com."
        ),
    },
    {
        "id": "kb-software",
        "tenant_id": DEMO_TENANT_ID,
        "category": "Services",
        "title": "Software Development Services",
        "content": (
            "Zacma Group provides full-cycle software engineering: Website Development, Modern Web Applications (Next.js, React, Tailwind), "
            "Mobile App Development (Android & iOS via Flutter/React Native), Desktop Applications, Custom Software, Enterprise ERP & CRM Development, "
            "School Management Systems (MySchool), E-Commerce Platforms, SaaS Development, REST APIs, Database Engineering (PostgreSQL, Supabase), "
            "Cloud Infrastructure (Docker, Kubernetes), AI-Powered Applications, Intelligent AI Agent Development, System Integration, and Software Maintenance."
        ),
    },
    {
        "id": "kb-visa",
        "tenant_id": DEMO_TENANT_ID,
        "category": "Services",
        "title": "Zacma Visa Assistant",
        "content": (
            "Zacma Visa Assistant provides end-to-end visa consultation and processing for Tourist, Work, Study, and Business visas across Schengen Area (Germany, France, etc.), UK, Canada, USA, UAE/Dubai, and Japan. "
            "Services include embassy cover letters, AI document completeness & risk analysis, appointment scheduling, and mock consular interview preparation."
        ),
    },
    {
        "id": "kb-travel",
        "tenant_id": DEMO_TENANT_ID,
        "category": "Services",
        "title": "Zacma Travel Agent",
        "content": (
            "Zacma Travel Agency provides international and domestic flight ticketing (Ethiopian Airlines, Emirates, FlyDubai, Qatar Airways), "
            "curated 5-day holiday & explorer tour packages, hotel reservations, airport VIP transfers, and bespoke travel budget planning."
        ),
    },
    {
        "id": "kb-training",
        "tenant_id": DEMO_TENANT_ID,
        "category": "Services",
        "title": "Zacma Training Institute",
        "content": (
            "Zacma Training Institute offers 15 accredited practical courses:\n"
            "1. Basic Computer\n"
            "2. Graphics\n"
            "3. Video Editing\n"
            "4. Videography\n"
            "5. Photography\n"
            "6. AI (Artificial Intelligence)\n"
            "7. Cloud Computing\n"
            "8. Spoken English\n"
            "9. Accounting\n"
            "10. IT Support\n"
            "11. AutoCAD\n"
            "12. ETABS\n"
            "13. Web Design\n"
            "14. Networking\n"
            "15. Maintenance (Specialty: Hardware Specialty)."
        ),
    },
    {
        "id": "kb-maintenance-hardware",
        "tenant_id": DEMO_TENANT_ID,
        "category": "Training",
        "title": "Maintenance Course - Hardware Specialty",
        "content": (
            "Maintenance is an official accredited course at Zacma Training Institute. Under Maintenance, students enroll in the 'Hardware Specialty'.\n\n"
            "Course: Maintenance\n"
            "Specialty: Hardware Specialty\n\n"
            "Description: Component-level hardware diagnostics, PCB soldering, motherboard & logic board repair, hardware assembly, power delivery diagnostics, and firmware flashing.\n\n"
            "Available Schedules:\n"
            "1. Monday + Wednesday + Thursday\n"
            "2. Tuesday + Thursday + Saturday\n"
            "3. Saturday + Sunday\n\n"
            "Available Time Slots:\n"
            "• 03:00 – 05:00\n"
            "• 05:00 – 07:00\n"
            "• 07:00 – 09:00\n"
            "• 09:00 – 11:00\n"
            "• 11:00 – 01:00\n"
            "• 12:00 – 02:00\n\n"
            "Students select one specific schedule and one time slot upon registration. Arbitrary day combinations are not permitted."
        ),
    },
    {
        "id": "kb-marketing",
        "tenant_id": DEMO_TENANT_ID,
        "category": "Services",
        "title": "Zacma Marketing Service",
        "content": (
            "Zacma Marketing Service delivers 30-day cross-channel digital growth campaigns, Meta (Facebook & Instagram) ads, Google Ads, "
            "Telegram community marketing, brand identity creation, conversion copywriting, and audience persona targeting."
        ),
    },
    {
        "id": "kb-platform-erp",
        "tenant_id": DEMO_TENANT_ID,
        "category": "Platforms",
        "title": "Zacma ERP Platform",
        "url": "https://erp.zacmaa.net/",
        "content": (
            "Zacma ERP (https://erp.zacmaa.net/) is a comprehensive cloud Enterprise Resource Planning platform for managing multi-branch operations: "
            "Financial accounting, procurement, multi-warehouse inventory management, human capital management (HRM & payroll), sales pipeline, and real-time executive analytics."
        ),
    },
    {
        "id": "kb-platform-myschool",
        "tenant_id": DEMO_TENANT_ID,
        "category": "Platforms",
        "title": "MySchool Platform",
        "url": "https://myschool.zacmaa.net/",
        "content": (
            "MySchool (https://myschool.zacmaa.net/) is Zacma's complete School Management System designed for K-12 schools, colleges, and academies: "
            "Student admissions, gradebook & report cards, attendance tracking, teacher schedules, automated tuition fee collection, parent communications, and student transcripts."
        ),
    },
    {
        "id": "kb-platform-ecommerce",
        "tenant_id": DEMO_TENANT_ID,
        "category": "Platforms",
        "title": "Zacma E-Commerce Platform",
        "url": "https://ecommerce.zacmaa.net/",
        "content": (
            "Zacma E-Commerce (https://ecommerce.zacmaa.net/) is a multi-vendor and standalone digital commerce platform featuring seamless Ethiopian payment gateways "
            "(TeleBirr, CBE Birr, SantimPay), product catalog management, order fulfillment, discount coupons, and real-time delivery tracking."
        ),
    },
    {
        "id": "kb-platform-freelancer",
        "tenant_id": DEMO_TENANT_ID,
        "category": "Platforms",
        "title": "Zacma Freelancer Platform",
        "url": "https://freelancer.zacmaa.net/",
        "content": (
            "Zacma Freelancer (https://freelancer.zacmaa.net/) is a premier talent marketplace connecting vetted software engineers, UI/UX designers, "
            "and digital marketers with local and international enterprise clients for project-based and contract work."
        ),
    },
    {
        "id": "kb-payments",
        "tenant_id": DEMO_TENANT_ID,
        "category": "Workflows",
        "title": "Payment & Invoicing Workflow",
        "content": (
            "Payment process:\n"
            "1. Client submits service request → Unique reference code (e.g. ZACMA-2026-XXXXXXXX, ZAC-DEV-XXXX) and invoice/payment transaction are generated.\n"
            "2. Client selects from available active payment options: Instant Online Checkout via SantimPay, Commercial Bank of Ethiopia (CBE), TeleBirr, Awash Bank, or Bank of Abyssinia.\n"
            "3. For bank transfers/mobile money, client transfers using their unique reference code and uploads payment receipt in the Client Portal (/portal).\n"
            "4. For online gateway (SantimPay), verification occurs automatically via server-side verification and webhooks.\n"
            "5. Upon verification, request transitions to 'PaymentApproved' → AI service execution and fulfillment begins."
        ),
    },
    {
        "id": "kb-tracking",
        "tenant_id": DEMO_TENANT_ID,
        "category": "Workflows",
        "title": "Request Tracking & Status Checking",
        "content": (
            "Clients can track any service request anytime by visiting '/track' and entering their reference code (e.g. ZAC-DEV-1001, ZACMA-2026-XXXXXXXX), "
            "or by logging into the Client Portal at '/portal' to view detailed timelines, payment receipts, case manager messages, and download official AI deliverables."
        ),
    },
]


# ---------------------------------------------------------------------------
# Organizations & People Seed Data
# ---------------------------------------------------------------------------

_ORGANIZATIONS_SEED: list[dict[str, Any]] = [
    {
        "id": "org-001",
        "tenant_id": DEMO_TENANT_ID,
        "name": "TechCorp Solutions PLC",
        "business_type": "Enterprise Company",
        "email": "contact@techcorp.et",
        "phone": "+251911223344",
        "website": "https://techcorp.et",
        "industry": "Information Technology",
        "address": "Bole Atlas, Addis Ababa",
        "city": "Addis Ababa",
        "country": "Ethiopia",
        "status": "Active",
        "source": "Organization Inquiry",
        "owner_id": "admin-id",
        "notes": "Enterprise client for software development and ERP automation.",
        "created_at": _ts(45),
        "updated_at": _ts(2),
    },
    {
        "id": "org-002",
        "tenant_id": DEMO_TENANT_ID,
        "name": "Addis Medical Center",
        "business_type": "Healthcare Group",
        "email": "admin@addismedical.com",
        "phone": "+251911445566",
        "website": "https://addismedical.com",
        "industry": "Healthcare",
        "address": "Sarbet, Addis Ababa",
        "city": "Addis Ababa",
        "country": "Ethiopia",
        "status": "Prospect",
        "source": "Software Request",
        "owner_id": "admin-id",
        "notes": "Telemedicine & pharmacy mobile app project.",
        "created_at": _ts(30),
        "updated_at": _ts(5),
    },
]

_PEOPLE_SEED: list[dict[str, Any]] = [
    {
        "id": "person-001",
        "tenant_id": DEMO_TENANT_ID,
        "full_name": "Abebe Bikila",
        "email": "abebe@example.com",
        "phone": "+251911001122",
        "alt_phone": None,
        "organization_id": "org-001",
        "job_title": "Senior Technical Lead",
        "person_type": "Customer",
        "status": "Active",
        "tags": ["Software", "VIP", "Student"],
        "address": "Bole Subcity, Woreda 03",
        "city": "Addis Ababa",
        "country": "Ethiopia",
        "source": "Direct",
        "notes": "Key technical decision maker at TechCorp. Enrolled in AI Course.",
        "created_at": _ts(60),
        "updated_at": _ts(1),
    },
    {
        "id": "person-002",
        "tenant_id": DEMO_TENANT_ID,
        "full_name": "Sara Johnson",
        "email": "sara.j@example.com",
        "phone": "+251922334455",
        "alt_phone": None,
        "organization_id": "org-001",
        "job_title": "HR Director",
        "person_type": "Customer",
        "status": "Active",
        "tags": ["Visa", "Corporate"],
        "address": "Kazanchis",
        "city": "Addis Ababa",
        "country": "Ethiopia",
        "source": "Visa Inquiry",
        "notes": "Processed Schengen Business visa.",
        "created_at": _ts(40),
        "updated_at": _ts(3),
    },
    {
        "id": "person-003",
        "tenant_id": DEMO_TENANT_ID,
        "full_name": "Dawit Bekele",
        "email": "dawit.b@example.com",
        "phone": "+251933445566",
        "alt_phone": None,
        "organization_id": "org-002",
        "job_title": "Operations Director",
        "person_type": "Lead",
        "status": "Prospect",
        "tags": ["Telemedicine", "Inquiry"],
        "address": "Sarbet",
        "city": "Addis Ababa",
        "country": "Ethiopia",
        "source": "Organization Inquiry",
        "notes": "Inquired for hospital workflow digitalization.",
        "created_at": _ts(15),
        "updated_at": _ts(1),
    },
    {
        "id": "person-004",
        "tenant_id": DEMO_TENANT_ID,
        "full_name": "Yonas Mulugeta",
        "email": "yonas.m@example.com",
        "phone": "+251944556677",
        "alt_phone": None,
        "organization_id": None,
        "job_title": "Freelance Consultant",
        "person_type": "Customer",
        "status": "Active",
        "tags": ["Travel", "Holiday"],
        "address": "CMC, Addis Ababa",
        "city": "Addis Ababa",
        "country": "Ethiopia",
        "source": "Travel Request",
        "notes": "Booked Dubai 5-day holiday package.",
        "created_at": _ts(20),
        "updated_at": _ts(2),
    },
]

_CRM_OPPORTUNITIES_SEED: list[dict[str, Any]] = [
    {
        "id": "opp-001",
        "tenant_id": DEMO_TENANT_ID,
        "title": "TechCorp Enterprise SaaS Platform",
        "person_id": "person-001",
        "organization_id": "org-001",
        "value": 150000.0,
        "currency": "ETB",
        "pipeline_stage": "Proposal",
        "probability": 70,
        "expected_close_date": "2026-09-30",
        "owner_id": "admin-id",
        "source": "Organization Inquiry",
        "notes": "Architecture proposal and SOW submitted. Waiting for board sign-off.",
        "status": "Open",
        "created_at": _ts(25),
        "updated_at": _ts(2),
    },
    {
        "id": "opp-002",
        "tenant_id": DEMO_TENANT_ID,
        "title": "Addis Medical Telehealth App",
        "person_id": "person-003",
        "organization_id": "org-002",
        "value": 220000.0,
        "currency": "ETB",
        "pipeline_stage": "Needs Analysis",
        "probability": 40,
        "expected_close_date": "2026-10-15",
        "owner_id": "admin-id",
        "source": "Software Request",
        "notes": "Requirements gathering on EHR and payment gateway integration.",
        "status": "Open",
        "created_at": _ts(10),
        "updated_at": _ts(1),
    },
    {
        "id": "opp-003",
        "tenant_id": DEMO_TENANT_ID,
        "title": "Corporate Visa & Relocation Package",
        "person_id": "person-002",
        "organization_id": "org-001",
        "value": 45000.0,
        "currency": "ETB",
        "pipeline_stage": "Won",
        "probability": 100,
        "expected_close_date": "2026-08-20",
        "owner_id": "admin-id",
        "source": "Visa Inquiry",
        "notes": "Deal closed and payment confirmed.",
        "status": "Won",
        "created_at": _ts(35),
        "updated_at": _ts(3),
    },
]

_CRM_ACTIVITIES_SEED: list[dict[str, Any]] = [
    {
        "id": "act-001",
        "tenant_id": DEMO_TENANT_ID,
        "activity_type": "Meeting",
        "subject": "Requirements Scope Presentation",
        "description": "Virtual meeting with TechCorp CTO and team to review Next.js & FastAPI architecture.",
        "person_id": "person-001",
        "organization_id": "org-001",
        "opportunity_id": "opp-001",
        "due_date": _ts(2),
        "completed_at": _ts(2),
        "status": "Completed",
        "actor": "admin@zacma.com",
        "created_at": _ts(5),
        "updated_at": _ts(2),
    },
    {
        "id": "act-002",
        "tenant_id": DEMO_TENANT_ID,
        "activity_type": "Call",
        "subject": "Follow-up on Telemedicine Project Proposal",
        "description": "Call Dr. Dawit to discuss Telebirr & CBE payment milestone schedule.",
        "person_id": "person-003",
        "organization_id": "org-002",
        "opportunity_id": "opp-002",
        "due_date": _ts(1),
        "completed_at": None,
        "status": "Pending",
        "actor": "admin@zacma.com",
        "created_at": _ts(3),
        "updated_at": _ts(3),
    },
    {
        "id": "act-003",
        "tenant_id": DEMO_TENANT_ID,
        "activity_type": "Email",
        "subject": "Visa Application Readiness Confirmation",
        "description": "Emailed embassy document checklist and appointment schedule to Sara.",
        "person_id": "person-002",
        "organization_id": "org-001",
        "opportunity_id": "opp-003",
        "due_date": _ts(10),
        "completed_at": _ts(10),
        "status": "Completed",
        "actor": "staff@zacma.com",
        "created_at": _ts(12),
        "updated_at": _ts(10),
    },
]

_MARKETING_SEGMENTS_SEED: list[dict[str, Any]] = [
    {
        "id": "seg-students",
        "tenant_id": DEMO_TENANT_ID,
        "name": "All Enrolled Students",
        "description": "Active students registered across training courses.",
        "filter_criteria": {"person_type": "Student"},
        "is_dynamic": True,
        "member_count": 4,
        "created_at": _ts(30),
        "updated_at": _ts(1),
    },
    {
        "id": "seg-leads",
        "tenant_id": DEMO_TENANT_ID,
        "name": "New & Uncontacted Leads",
        "description": "Prospective clients from web inquiries and software requests.",
        "filter_criteria": {"status": "Lead"},
        "is_dynamic": True,
        "member_count": 3,
        "created_at": _ts(25),
        "updated_at": _ts(1),
    },
    {
        "id": "seg-enterprises",
        "tenant_id": DEMO_TENANT_ID,
        "name": "Corporate & Enterprise Clients",
        "description": "B2B organizations and business executives.",
        "filter_criteria": {"has_organization": True},
        "is_dynamic": True,
        "member_count": 3,
        "created_at": _ts(20),
        "updated_at": _ts(1),
    },
]

_COMMUNICATION_LOGS_SEED: list[dict[str, Any]] = [
    {
        "id": "comm-001",
        "tenant_id": DEMO_TENANT_ID,
        "channel": "Email",
        "sender": "Zacma Support <support@zacma.com>",
        "recipient": "abebe@example.com",
        "person_id": "person-001",
        "organization_id": "org-001",
        "campaign_id": None,
        "subject": "Your Course Orientation & Architecture Proposal",
        "message_body": "Dear Abebe, we have confirmed your seat in the AI course and prepared your project SOW.",
        "status": "Delivered",
        "created_at": _ts(2),
    },
    {
        "id": "comm-002",
        "tenant_id": DEMO_TENANT_ID,
        "channel": "Email",
        "sender": "Zacma Marketing <marketing@zacma.com>",
        "recipient": "dawit.b@example.com",
        "person_id": "person-003",
        "organization_id": "org-002",
        "campaign_id": "camp-001",
        "subject": "Transforming Healthcare with Custom AI & SaaS",
        "message_body": "Explore our newly released case studies on enterprise telemedicine workflows.",
        "status": "Delivered",
        "created_at": _ts(5),
    },
]


# ---------------------------------------------------------------------------
# Exported Store Singletons
# ---------------------------------------------------------------------------

crm_contacts_store = DemoStore(_CRM_CONTACTS_SEED)
invoices_store = DemoStore(_INVOICES_SEED)
students_store = DemoStore(_STUDENTS_SEED)
visa_applications_store = DemoStore(_VISA_APPLICATIONS_SEED)
travel_requests_store = DemoStore(_TRAVEL_REQUESTS_SEED)
software_projects_store = DemoStore(_SOFTWARE_PROJECTS_SEED)
knowledge_base_store = DemoStore(_KNOWLEDGE_BASE_SEED)
support_tickets_store = DemoStore(_SUPPORT_TICKETS_SEED)
business_modules_store = DemoStore(_BUSINESS_MODULES_SEED)
module_submissions_store = DemoStore(_MODULE_SUBMISSIONS_SEED)
notification_templates_store = DemoStore(_NOTIFICATION_TEMPLATES_SEED)
system_settings_store = DemoStore(_SYSTEM_SETTINGS_SEED)

# Multi-Provider Payment Engine Stores
payment_providers_store = DemoStore(_PAYMENT_PROVIDERS_SEED)
payment_transactions_store = DemoStore(_PAYMENT_TRANSACTIONS_SEED)
payment_webhooks_store = DemoStore(_PAYMENT_WEBHOOKS_SEED)
payment_logs_store = DemoStore(_PAYMENT_LOGS_SEED)

# Unified People, Organizations, CRM & Marketing Stores
organizations_store = DemoStore(_ORGANIZATIONS_SEED)
people_store = DemoStore(_PEOPLE_SEED)
crm_opportunities_store = DemoStore(_CRM_OPPORTUNITIES_SEED)
crm_activities_store = DemoStore(_CRM_ACTIVITIES_SEED)
marketing_segments_store = DemoStore(_MARKETING_SEGMENTS_SEED)
communication_logs_store = DemoStore(_COMMUNICATION_LOGS_SEED)

# HRM Advanced Stores (Leaves, Attendance, Payroll)
_LEAVES_SEED: list[dict[str, Any]] = [
    {
        "id": "leave-001",
        "tenant_id": DEMO_TENANT_ID,
        "employee_id": "emp-001",
        "employee_name": "Abebe Kebede",
        "leave_type": "Annual",
        "start_date": "2026-09-01",
        "end_date": "2026-09-07",
        "reason": "Family vacation",
        "status": "approved",
        "admin_comment": "Approved by HR Director",
        "created_at": _ts(5),
    },
    {
        "id": "leave-002",
        "tenant_id": DEMO_TENANT_ID,
        "employee_id": "emp-002",
        "employee_name": "Tigist Alemu",
        "leave_type": "Sick",
        "start_date": "2026-08-20",
        "end_date": "2026-08-22",
        "reason": "Medical checkup",
        "status": "approved",
        "admin_comment": "Medical certificate verified",
        "created_at": _ts(3),
    },
]

_ATTENDANCE_SEED: list[dict[str, Any]] = [
    {
        "id": "att-001",
        "tenant_id": DEMO_TENANT_ID,
        "employee_id": "emp-001",
        "employee_name": "Abebe Kebede",
        "date": "2026-08-23",
        "status": "Present",
        "check_in": "08:30",
        "check_out": "17:30",
        "notes": "On-time arrival",
        "created_at": _ts(0),
    },
    {
        "id": "att-002",
        "tenant_id": DEMO_TENANT_ID,
        "employee_id": "emp-002",
        "employee_name": "Tigist Alemu",
        "date": "2026-08-23",
        "status": "Present",
        "check_in": "08:45",
        "check_out": "17:30",
        "notes": "HQ office",
        "created_at": _ts(0),
    },
]

_PAYROLL_SEED: list[dict[str, Any]] = [
    {
        "id": "pay-001",
        "tenant_id": DEMO_TENANT_ID,
        "employee_id": "emp-001",
        "employee_name": "Abebe Kebede",
        "month": "2026-07",
        "gross_salary": 45000.0,
        "tax_deduction": 8500.0,
        "pension_deduction": 3150.0,
        "net_salary": 33350.0,
        "currency": "ETB",
        "status": "paid",
        "disbursed_at": _ts(20),
        "created_at": _ts(20),
    },
    {
        "id": "pay-002",
        "tenant_id": DEMO_TENANT_ID,
        "employee_id": "emp-002",
        "employee_name": "Tigist Alemu",
        "month": "2026-07",
        "gross_salary": 38000.0,
        "tax_deduction": 6800.0,
        "pension_deduction": 2660.0,
        "net_salary": 28540.0,
        "currency": "ETB",
        "status": "paid",
        "disbursed_at": _ts(20),
        "created_at": _ts(20),
    },
]

leaves_store = DemoStore(_LEAVES_SEED)
attendance_store = DemoStore(_ATTENDANCE_SEED)
payroll_store = DemoStore(_PAYROLL_SEED)

# Backwards compatibility legacy store aliases
leads_store = DemoStore(_LEADS_SEED)
employees_store = DemoStore(_EMPLOYEES_SEED)
visa_apps_store = visa_applications_store
courses_store = DemoStore(_COURSES_SEED)
bookings_store = DemoStore(_BOOKINGS_SEED)
campaigns_store = DemoStore(_CAMPAIGNS_SEED)
admin_users_store = DemoStore(_ADMIN_USERS_SEED)
audit_logs_store = DemoStore(_AUDIT_LOGS_SEED)
automation_jobs_store = DemoStore([])


