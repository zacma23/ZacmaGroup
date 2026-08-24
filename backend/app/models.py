"""Pydantic request/response models for all ZACMA platform modules and core engines.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, EmailStr, Field, model_validator


# ---------------------------------------------------------------------------
# Common & Pagination
# ---------------------------------------------------------------------------

class PaginationParams(BaseModel):
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=100)


# ---------------------------------------------------------------------------
# Auth & Profile Models
# ---------------------------------------------------------------------------

class LoginRequest(BaseModel):
    email: str = Field(min_length=1, description="Email or phone number")
    password: str = Field(min_length=1)
    remember_me: bool = False

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str = Field(min_length=1, max_length=200)
    phone: Optional[str] = None
    address: Optional[str] = None
    education_level: Optional[str] = "Diploma"
    role: str = Field(default="client")

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    tenant_id: str
    email: str
    full_name: str
    user_id: Optional[str] = None

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(min_length=8)

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(min_length=8)

class VerifyAccountRequest(BaseModel):
    token: str
    type: str = "email_verify"

class FirebaseLoginRequest(BaseModel):
    id_token: str = Field(min_length=1)
    remember_me: bool = False

class PhoneOtpSendRequest(BaseModel):
    phone: str = Field(min_length=9, max_length=20)

class PhoneOtpVerifyRequest(BaseModel):
    phone: str = Field(min_length=9, max_length=20)
    otp: str = Field(min_length=4, max_length=10)

class EmailResendRequest(BaseModel):
    email: EmailStr

class ProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    education_level: Optional[str] = None
    avatar_url: Optional[str] = None

class UserProfile(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    tenant_id: str
    phone: Optional[str] = None
    address: Optional[str] = None
    education_level: Optional[str] = None
    avatar_url: Optional[str] = None
    status: str = "active"
    is_verified: bool = True
    created_at: Optional[str] = None


# ---------------------------------------------------------------------------
# Client Service & Payment Receipt Models
# ---------------------------------------------------------------------------

class PaymentReceiptUploadRequest(BaseModel):
    reference_code: str
    payment_method: str = "CBE"
    transaction_reference: str = Field(min_length=1)
    receipt_file_url: str = Field(min_length=1)
    amount: Optional[float] = None
    currency: str = "ETB"
    notes: Optional[str] = None

class AdminPaymentVerificationRequest(BaseModel):
    verified: bool
    comment: Optional[str] = "Payment verified by administrator"
    rejection_reason: Optional[str] = None

class AdminServiceApprovalRequest(BaseModel):
    status: str = "Approved"  # Approved, ServiceDelivered, NeedsCorrection, Rejected
    admin_response_message: Optional[str] = "Your application has been approved and processed."
    deliverable_payload: Optional[dict[str, Any]] = None

class AdminAiEditRequest(BaseModel):
    ai_generated_result: dict[str, Any]
    admin_notes: Optional[str] = None



# ---------------------------------------------------------------------------
# 3.1 People & Organizations (Central Directory Layer)
# ---------------------------------------------------------------------------

class PersonTypeEnum(str, Enum):
    INDIVIDUAL = "Individual"
    CUSTOMER = "Customer"
    LEAD = "Lead"
    STUDENT = "Student"
    STAFF = "Staff"
    PARTNER = "Partner"
    VENDOR = "Vendor"
    OTHER = "Other"

class PersonStatusEnum(str, Enum):
    ACTIVE = "Active"
    LEAD = "Lead"
    PROSPECT = "Prospect"
    ENROLLED = "Enrolled"
    CUSTOMER = "Customer"
    ALUMNI = "Alumni"
    INACTIVE = "Inactive"

class OrganizationCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    business_type: str = Field(default="Company", max_length=50)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, max_length=50)
    website: Optional[str] = None
    industry: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: str = "Ethiopia"
    status: str = "Active"
    source: str = "Inquiry"
    notes: Optional[str] = None

class OrganizationUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=200)
    business_type: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None

class OrganizationResponse(BaseModel):
    id: str
    tenant_id: str
    name: str
    business_type: str = "Company"
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: str = "Ethiopia"
    status: str = "Active"
    source: str = "Inquiry"
    owner_id: Optional[str] = None
    notes: Optional[str] = None
    people_count: int = 0
    created_at: str
    updated_at: str

class PersonCreate(BaseModel):
    full_name: str = Field(min_length=1, max_length=200)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, max_length=50)
    alt_phone: Optional[str] = Field(default=None, max_length=50)
    organization_id: Optional[str] = None
    job_title: Optional[str] = None
    person_type: PersonTypeEnum = PersonTypeEnum.INDIVIDUAL
    status: PersonStatusEnum = PersonStatusEnum.ACTIVE
    tags: list[str] = Field(default_factory=list)
    address: Optional[str] = None
    city: Optional[str] = None
    country: str = "Ethiopia"
    source: str = "Direct"
    notes: Optional[str] = None

class PersonUpdate(BaseModel):
    full_name: Optional[str] = Field(default=None, max_length=200)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    alt_phone: Optional[str] = None
    organization_id: Optional[str] = None
    job_title: Optional[str] = None
    person_type: Optional[PersonTypeEnum] = None
    status: Optional[PersonStatusEnum] = None
    tags: Optional[list[str]] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    source: Optional[str] = None
    notes: Optional[str] = None

class PersonResponse(BaseModel):
    id: str
    tenant_id: str
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    alt_phone: Optional[str] = None
    organization_id: Optional[str] = None
    organization_name: Optional[str] = None
    job_title: Optional[str] = None
    person_type: str = "Individual"
    status: str = "Active"
    tags: list[str] = Field(default_factory=list)
    address: Optional[str] = None
    city: Optional[str] = None
    country: str = "Ethiopia"
    source: str = "Direct"
    notes: Optional[str] = None
    created_at: str
    updated_at: str

class PersonDetailedProfile(BaseModel):
    person: PersonResponse
    organization: Optional[OrganizationResponse] = None
    crm_lead: Optional[dict[str, Any]] = None
    opportunities: list[dict[str, Any]] = Field(default_factory=list)
    activities: list[dict[str, Any]] = Field(default_factory=list)
    student_records: list[dict[str, Any]] = Field(default_factory=list)
    service_requests: list[dict[str, Any]] = Field(default_factory=list)
    invoices: list[dict[str, Any]] = Field(default_factory=list)
    payments: list[dict[str, Any]] = Field(default_factory=list)
    total_paid_volume: float = 0.0
    campaign_communications: list[dict[str, Any]] = Field(default_factory=list)
    timeline: list[dict[str, Any]] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# 3.2 CRM Opportunities, Pipelines & Activities
# ---------------------------------------------------------------------------

class PipelineStageEnum(str, Enum):
    NEW_LEAD = "New Lead"
    CONTACTED = "Contacted"
    QUALIFIED = "Qualified"
    NEEDS_ANALYSIS = "Needs Analysis"
    PROPOSAL = "Proposal"
    NEGOTIATION = "Negotiation"
    WON = "Won"
    LOST = "Lost"

class OpportunityCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    person_id: Optional[str] = None
    organization_id: Optional[str] = None
    value: float = Field(default=0.0, ge=0)
    currency: str = "ETB"
    pipeline_stage: PipelineStageEnum = PipelineStageEnum.NEW_LEAD
    probability: int = Field(default=20, ge=0, le=100)
    expected_close_date: Optional[str] = None
    source: str = "Inquiry"
    notes: Optional[str] = None

class OpportunityUpdate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=200)
    person_id: Optional[str] = None
    organization_id: Optional[str] = None
    value: Optional[float] = Field(default=None, ge=0)
    currency: Optional[str] = None
    pipeline_stage: Optional[PipelineStageEnum] = None
    probability: Optional[int] = Field(default=None, ge=0, le=100)
    expected_close_date: Optional[str] = None
    source: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None

class OpportunityResponse(BaseModel):
    id: str
    tenant_id: str
    title: str
    person_id: Optional[str] = None
    person_name: Optional[str] = None
    organization_id: Optional[str] = None
    organization_name: Optional[str] = None
    value: float = 0.0
    currency: str = "ETB"
    pipeline_stage: str = "New Lead"
    probability: int = 20
    expected_close_date: Optional[str] = None
    owner_id: Optional[str] = None
    source: str = "Inquiry"
    notes: Optional[str] = None
    status: str = "Open"
    created_at: str
    updated_at: str

class ActivityTypeEnum(str, Enum):
    CALL = "Call"
    EMAIL = "Email"
    SMS = "SMS"
    WHATSAPP = "WhatsApp"
    MEETING = "Meeting"
    TASK = "Task"
    NOTE = "Note"
    FOLLOW_UP = "Follow-up"

class ActivityCreate(BaseModel):
    activity_type: ActivityTypeEnum = ActivityTypeEnum.NOTE
    subject: str = Field(min_length=1, max_length=200)
    description: Optional[str] = None
    person_id: str
    organization_id: Optional[str] = None
    opportunity_id: Optional[str] = None
    due_date: Optional[str] = None
    actor: str = "admin"

class ActivityUpdate(BaseModel):
    subject: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None  # Pending, Completed, Cancelled
    due_date: Optional[str] = None
    completed_at: Optional[str] = None

class ActivityResponse(BaseModel):
    id: str
    tenant_id: str
    activity_type: str = "Note"
    subject: str
    description: Optional[str] = None
    person_id: str
    person_name: Optional[str] = None
    organization_id: Optional[str] = None
    opportunity_id: Optional[str] = None
    due_date: Optional[str] = None
    completed_at: Optional[str] = None
    status: str = "Pending"
    actor: str = "system"
    created_at: str
    updated_at: str


# ---------------------------------------------------------------------------
# 3.3 Marketing Segments, Campaigns & Communication Logs
# ---------------------------------------------------------------------------

class MarketingSegmentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: Optional[str] = None
    filter_criteria: dict[str, Any] = Field(default_factory=dict)
    is_dynamic: bool = True

class MarketingSegmentResponse(BaseModel):
    id: str
    tenant_id: str
    name: str
    description: Optional[str] = None
    filter_criteria: dict[str, Any] = Field(default_factory=dict)
    is_dynamic: bool = True
    member_count: int = 0
    created_at: str
    updated_at: str

class MarketingCampaignDispatch(BaseModel):
    channel: str = "Email"  # Email, SMS, Notification
    target_segment_id: Optional[str] = None
    custom_recipient_person_ids: Optional[list[str]] = None

class CommunicationLogResponse(BaseModel):
    id: str
    tenant_id: str
    channel: str
    sender: str
    recipient: str
    person_id: Optional[str] = None
    person_name: Optional[str] = None
    organization_id: Optional[str] = None
    campaign_id: Optional[str] = None
    subject: Optional[str] = None
    message_body: Optional[str] = None
    status: str = "Sent"
    created_at: str


# ---------------------------------------------------------------------------
# 3.4 Legacy CRM Contact & Lead Aliases (Backward-compatibility)
# ---------------------------------------------------------------------------

class CrmContactStatus(str, Enum):
    LEAD = "Lead"
    ACTIVE = "Active"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"

class CrmSourceModule(str, Enum):
    STUDENT = "Student"
    VISA = "Visa"
    TRAVEL = "Travel"
    SUPPORT = "Support"
    CUSTOM = "Custom"

class CrmTimelineItem(BaseModel):
    id: str
    timestamp: str
    action: str
    description: str
    actor: str = "system"
    metadata: dict[str, Any] = Field(default_factory=dict)

class CrmNoteCreate(BaseModel):
    content: str = Field(min_length=1)

class CrmNote(BaseModel):
    id: str
    author: str
    content: str
    created_at: str

class CrmContactCreate(BaseModel):
    full_name: str = Field(min_length=1, max_length=200)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, max_length=50)
    address: Optional[str] = None
    country: Optional[str] = Field(default="Ethiopia", max_length=100)
    source_module: CrmSourceModule = CrmSourceModule.CUSTOM
    status: CrmContactStatus = CrmContactStatus.LEAD
    tags: list[str] = Field(default_factory=list)
    assigned_admin_id: Optional[str] = None
    notes: Optional[str] = None

class CrmContactUpdate(BaseModel):
    full_name: Optional[str] = Field(default=None, max_length=200)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, max_length=50)
    address: Optional[str] = None
    country: Optional[str] = Field(default=None, max_length=100)
    status: Optional[CrmContactStatus] = None
    tags: Optional[list[str]] = None
    assigned_admin_id: Optional[str] = None

class CrmContact(BaseModel):
    id: str
    tenant_id: str
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    country: str = "Ethiopia"
    source_module: str = "Custom"
    status: str = "Lead"
    tags: list[str] = Field(default_factory=list)
    assigned_admin_id: Optional[str] = None
    timeline: list[CrmTimelineItem] = Field(default_factory=list)
    notes_list: list[CrmNote] = Field(default_factory=list)
    linked_registration_ids: list[str] = Field(default_factory=list)
    linked_invoice_ids: list[str] = Field(default_factory=list)
    linked_ticket_ids: list[str] = Field(default_factory=list)
    created_at: str
    updated_at: str

class LeadCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    email: Optional[EmailStr] = None
    company: Optional[str] = Field(default=None, max_length=200)
    phone: Optional[str] = Field(default=None, max_length=50)
    source: str = Field(default="manual", max_length=50)
    status: str = Field(default="new", max_length=30)
    notes: Optional[str] = None

class LeadUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=200)
    email: Optional[EmailStr] = None
    company: Optional[str] = Field(default=None, max_length=200)
    phone: Optional[str] = Field(default=None, max_length=50)
    source: Optional[str] = Field(default=None, max_length=50)
    status: Optional[str] = Field(default=None, max_length=30)
    notes: Optional[str] = None

class LeadResponse(BaseModel):
    id: str
    tenant_id: str
    name: str
    email: Optional[str] = None
    company: Optional[str] = None
    phone: Optional[str] = None
    source: str = "manual"
    status: str = "new"
    notes: Optional[str] = None
    created_at: Optional[str] = None


# ---------------------------------------------------------------------------
# 3.2 Payment & Invoicing Engine
# ---------------------------------------------------------------------------

class PaymentMethodEnum(str, Enum):
    SANTIMPAY = "SantimPay"
    TELEBIRR = "TeleBirr"
    CBE = "CBE"
    AWASH = "Awash"
    ABYSSINIA = "Abyssinia"
    CHAPA = "Chapa"

class InvoiceStatus(str, Enum):
    DRAFT = "draft"
    SENT = "sent"
    PAID = "paid"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    OVERDUE = "overdue"

class InvoiceCreate(BaseModel):
    customer_name: str = Field(min_length=1, max_length=200)
    customer_email: Optional[EmailStr] = None
    contact_id: Optional[str] = None
    module_type: str = Field(default="general", max_length=50)
    amount: float = Field(gt=0)
    currency: str = Field(default="ETB", max_length=5)
    payment_method: str = Field(default="CBE")
    receiving_account: Optional[str] = None
    due_date: Optional[str] = None
    description: Optional[str] = None
    reference_code: Optional[str] = None
    status: InvoiceStatus = InvoiceStatus.DRAFT

class InvoiceUpdate(BaseModel):
    customer_name: Optional[str] = Field(default=None, max_length=200)
    customer_email: Optional[EmailStr] = None
    amount: Optional[float] = Field(default=None, gt=0)
    currency: Optional[str] = Field(default=None, max_length=5)
    payment_method: Optional[str] = None
    receiving_account: Optional[str] = None
    due_date: Optional[str] = None
    description: Optional[str] = None
    status: Optional[InvoiceStatus] = None

class PaymentAttemptRequest(BaseModel):
    gateway: str
    reference_number: str
    proof_file_url: Optional[str] = None
    notes: Optional[str] = None

class PaymentConfirmationRequest(BaseModel):
    comment: Optional[str] = "Payment confirmed by admin"

class PaymentRejectionRequest(BaseModel):
    reason: str = Field(min_length=1)

class InvoiceResponse(BaseModel):
    id: str
    tenant_id: str
    customer_name: str
    customer_email: Optional[str] = None
    contact_id: Optional[str] = None
    module_type: str = "general"
    amount: float
    currency: str = "ETB"
    payment_method: str = "CBE"
    receiving_account: Optional[str] = None
    reference_code: str
    due_date: Optional[str] = None
    description: Optional[str] = None
    status: str = "draft"
    payment_attempts: list[dict[str, Any]] = Field(default_factory=list)
    confirmed_by: Optional[str] = None
    confirmed_at: Optional[str] = None
    rejection_reason: Optional[str] = None
    created_at: Optional[str] = None


# ---------------------------------------------------------------------------
# 3.2.1 Multi-Provider Payment Architecture Models
# ---------------------------------------------------------------------------

class PaymentProviderType(str, Enum):
    GATEWAY = "gateway"
    BANK_TRANSFER = "bank_transfer"
    MOBILE_MONEY = "mobile_money"
    CUSTOM = "custom"

class PaymentEnvironmentEnum(str, Enum):
    TEST = "test"
    LIVE = "live"
    SANDBOX = "sandbox"

class PaymentTransactionStatusEnum(str, Enum):
    PENDING = "pending"
    INITIATED = "initiated"
    PROCESSING = "processing"
    SUCCESSFUL = "successful"
    FAILED = "failed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"

class PaymentProviderPublic(BaseModel):
    id: str
    provider_name: str
    provider_code: str
    provider_type: str
    is_active: bool
    is_default: bool
    currency: str
    supported_currencies: list[str] = Field(default_factory=lambda: ["ETB"])
    account_name: Optional[str] = None
    account_number: Optional[str] = None
    customer_payment_number: Optional[str] = None
    instructions: Optional[str] = None
    environment: str = "test"
    transaction_fee_percent: float = 0.0
    transaction_fee_fixed: float = 0.0

class PaymentProviderCreate(BaseModel):
    provider_name: str = Field(min_length=1, max_length=100)
    provider_code: str = Field(min_length=1, max_length=50)
    provider_type: PaymentProviderType = PaymentProviderType.BANK_TRANSFER
    is_active: bool = True
    is_default: bool = False
    priority: int = 1
    environment: PaymentEnvironmentEnum = PaymentEnvironmentEnum.TEST
    currency: str = "ETB"
    supported_currencies: list[str] = Field(default_factory=lambda: ["ETB"])
    account_name: Optional[str] = None
    account_number: Optional[str] = None
    customer_payment_number: Optional[str] = None
    instructions: Optional[str] = None
    api_endpoint: Optional[str] = None
    callback_url: Optional[str] = None
    webhook_url: Optional[str] = None
    supports_balance_api: bool = False
    transaction_fee_percent: float = 0.0
    transaction_fee_fixed: float = 0.0
    # Credentials (encrypted or securely handled server-side)
    api_key: Optional[str] = None
    secret_key: Optional[str] = None
    merchant_id: Optional[str] = None
    webhook_secret: Optional[str] = None
    public_key: Optional[str] = None
    additional_config: dict[str, Any] = Field(default_factory=dict)

class PaymentProviderUpdate(BaseModel):
    provider_name: Optional[str] = None
    provider_type: Optional[PaymentProviderType] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None
    priority: Optional[int] = None
    environment: Optional[PaymentEnvironmentEnum] = None
    currency: Optional[str] = None
    supported_currencies: Optional[list[str]] = None
    account_name: Optional[str] = None
    account_number: Optional[str] = None
    customer_payment_number: Optional[str] = None
    instructions: Optional[str] = None
    api_endpoint: Optional[str] = None
    callback_url: Optional[str] = None
    webhook_url: Optional[str] = None
    supports_balance_api: Optional[bool] = None
    transaction_fee_percent: Optional[float] = None
    transaction_fee_fixed: Optional[float] = None
    api_key: Optional[str] = None
    secret_key: Optional[str] = None
    merchant_id: Optional[str] = None
    webhook_secret: Optional[str] = None
    public_key: Optional[str] = None
    additional_config: Optional[dict[str, Any]] = None

class PaymentProviderResponse(BaseModel):
    id: str
    tenant_id: str
    provider_name: str
    provider_code: str
    provider_type: str
    is_active: bool
    is_default: bool
    priority: int
    environment: str
    currency: str
    supported_currencies: list[str] = Field(default_factory=lambda: ["ETB"])
    account_name: Optional[str] = None
    account_number: Optional[str] = None
    customer_payment_number: Optional[str] = None
    instructions: Optional[str] = None
    api_endpoint: Optional[str] = None
    callback_url: Optional[str] = None
    webhook_url: Optional[str] = None
    supports_balance_api: bool = False
    transaction_fee_percent: float = 0.0
    transaction_fee_fixed: float = 0.0
    has_secret_key: bool = False
    masked_secret_key: Optional[str] = None
    masked_api_key: Optional[str] = None
    merchant_id: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class PaymentInitRequest(BaseModel):
    amount: float = Field(gt=0)
    currency: str = "ETB"
    provider_code: str
    customer_name: str
    customer_email: Optional[EmailStr] = None
    customer_phone: Optional[str] = None
    payment_purpose: str = "Service Fee"
    description: Optional[str] = None
    invoice_id: Optional[str] = None
    return_url: Optional[str] = None
    callback_url: Optional[str] = None

class PaymentInitResponse(BaseModel):
    transaction_id: str
    public_reference: str
    provider_code: str
    amount: float
    currency: str
    status: str
    checkout_url: Optional[str] = None
    account_number: Optional[str] = None
    account_name: Optional[str] = None
    customer_payment_number: Optional[str] = None
    instructions: Optional[str] = None
    message: str = "Payment initialized"

class PaymentTransactionResponse(BaseModel):
    id: str
    tenant_id: str
    public_reference: str
    customer_id: Optional[str] = None
    customer_name: str
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    provider_id: Optional[str] = None
    provider_code: str
    payment_method: str
    amount: float
    fee: float = 0.0
    net_amount: float
    currency: str = "ETB"
    status: str
    payment_purpose: str = "Service Fee"
    description: Optional[str] = None
    invoice_id: Optional[str] = None
    provider_transaction_id: Optional[str] = None
    provider_reference: Optional[str] = None
    checkout_url: Optional[str] = None
    callback_status: Optional[str] = None
    verification_status: Optional[str] = None
    error_message: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    completed_at: Optional[str] = None

class PaymentVerificationRequest(BaseModel):
    transaction_reference: str

class PaymentVerificationResponse(BaseModel):
    success: bool
    status: str
    public_reference: Optional[str] = None
    amount: Optional[float] = None
    currency: Optional[str] = None
    provider_reference: Optional[str] = None
    message: str

class PaymentBalanceSummary(BaseModel):
    total_received: float = 0.0
    pending_balance: float = 0.0
    available_balance: float = 0.0
    total_transferred: float = 0.0
    total_refunded: float = 0.0
    total_volume: float = 0.0
    today_transactions_count: int = 0
    today_transactions_volume: float = 0.0
    month_transactions_count: int = 0
    month_transactions_volume: float = 0.0
    successful_count: int = 0
    failed_count: int = 0
    currency: str = "ETB"
    provider_balances: list[dict[str, Any]] = Field(default_factory=list)

class PaymentRefundRequest(BaseModel):
    amount: Optional[float] = None
    reason: str = Field(min_length=1)


# ---------------------------------------------------------------------------
# 3.3 Approval Workflow Engine
# ---------------------------------------------------------------------------

class WorkflowStatus(str, Enum):
    PENDING = "Pending"
    UNDER_REVIEW = "UnderReview"
    DOCUMENTS_REQUESTED = "DocumentsRequested"
    APPROVED = "Approved"
    DENIED = "Denied"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"

class ApprovalActionRequest(BaseModel):
    action: str = Field(description="approve, deny, request_info, submit")
    comment: Optional[str] = None
    reason: Optional[str] = None
    message: Optional[str] = None


# ---------------------------------------------------------------------------
# 3.4 Notification Engine
# ---------------------------------------------------------------------------

class NotificationTemplate(BaseModel):
    key: str
    subject: str
    body_template: str
    description: str

class NotificationSendRequest(BaseModel):
    to_email: EmailStr
    template_key: str
    model: dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# 3.5 File Storage Service
# ---------------------------------------------------------------------------

class FileUploadResponse(BaseModel):
    file_id: str
    file_name: str
    file_url: str
    content_type: str
    size_bytes: int
    category: str


# ---------------------------------------------------------------------------
# 4.1 Module: Student Registration (Training Institute)
# ---------------------------------------------------------------------------

class CourseCategoryEnum(str, Enum):
    GRAPHICS_DESIGN = "Graphics Design"
    VIDEO_EDITING = "Video Editing"
    WEB_DESIGN = "Web Design"
    PROGRAMMING = "Programming"
    AI = "AI"
    ACCOUNTING = "Accounting"
    MAINTENANCE = "Maintenance"

class MaintenanceSubType(str, Enum):
    MOBILE = "Mobile"
    COMPUTER = "Computer"
    PRINTER = "Printer"
    ELECTRONICS = "Electronics"

class EducationLevelEnum(str, Enum):
    HIGH_SCHOOL = "High School"
    DIPLOMA = "Diploma"
    BACHELORS = "Bachelor's Degree"
    MASTERS = "Master's Degree"
    OTHER = "Other"

class AttendanceRecord(BaseModel):
    session_date: str
    session_title: str
    present: bool
    notes: Optional[str] = None

class AttendanceMarkRequest(BaseModel):
    session_date: str
    session_title: str
    present: bool
    notes: Optional[str] = None

class StudentRegistrationCreate(BaseModel):
    full_name: str = Field(min_length=1, max_length=200)
    address: Optional[str] = "Addis Ababa"
    phone: Optional[str] = "+251900000000"
    email: str = Field(min_length=3, max_length=200)
    education_level: str = "Bachelor's Degree"
    course: str = "Maintenance"
    specialty: Optional[str] = None
    schedule: Optional[str] = None
    time_slot: Optional[str] = None
    time: Optional[str] = None
    maintenance_sub_type: Optional[str] = None
    payment_method: str = "TeleBirr"
    interests: Optional[str] = None

class StudentRegistrationUpdate(BaseModel):
    full_name: Optional[str] = Field(default=None, max_length=200)
    address: Optional[str] = None
    phone: Optional[str] = Field(default=None, max_length=50)
    email: Optional[EmailStr] = None
    education_level: Optional[str] = None
    course: Optional[str] = None
    specialty: Optional[str] = None
    schedule: Optional[str] = None
    time_slot: Optional[str] = None
    time: Optional[str] = None
    maintenance_sub_type: Optional[str] = None
    payment_method: Optional[str] = None
    status: Optional[str] = None

class StudentRegistration(BaseModel):
    id: str
    tenant_id: str
    reference_code: Optional[str] = None
    full_name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    email: str
    education_level: str
    course: str
    specialty: Optional[str] = None
    schedule: Optional[str] = None
    time_slot: Optional[str] = None
    time: Optional[str] = None
    maintenance_sub_type: Optional[str] = None
    payment_method: str
    status: str = "Pending"
    attendance: list[AttendanceRecord] = Field(default_factory=list)
    linked_crm_contact_id: Optional[str] = None
    linked_invoice_id: Optional[str] = None
    ai_course_recommendation: Optional[str] = None
    payment_receipt: Optional[dict[str, Any]] = None
    ai_generated_result: Optional[dict[str, Any]] = None
    admin_response: Optional[dict[str, Any]] = None
    created_at: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def set_student_defaults(cls, values: Any) -> Any:
        if isinstance(values, dict):
            if "id" in values and not values.get("reference_code"):
                values["reference_code"] = f"ZAC-STU-{abs(hash(values['id'])) % 9000 + 1000}"
            # Harmonize specialty and maintenance_sub_type
            if values.get("specialty") and not values.get("maintenance_sub_type"):
                values["maintenance_sub_type"] = values["specialty"]
            elif values.get("maintenance_sub_type") and not values.get("specialty"):
                values["specialty"] = values["maintenance_sub_type"]
            # Harmonize time and time_slot
            if values.get("time_slot") and not values.get("time"):
                values["time"] = values["time_slot"]
            elif values.get("time") and not values.get("time_slot"):
                values["time_slot"] = values["time"]
        return values



# Legacy Course aliases
class CourseCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = None
    instructor: Optional[str] = Field(default=None, max_length=200)
    capacity: int = Field(default=30, ge=1)
    enrolled: int = Field(default=0, ge=0)
    start_date: Optional[str] = None
    status: str = Field(default="active", max_length=30)

class CourseUpdate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = None
    instructor: Optional[str] = Field(default=None, max_length=200)
    capacity: Optional[int] = Field(default=None, ge=1)
    enrolled: Optional[int] = Field(default=None, ge=0)
    start_date: Optional[str] = None
    status: Optional[str] = Field(default=None, max_length=30)

class CourseResponse(BaseModel):
    id: str
    tenant_id: str
    title: str
    description: Optional[str] = None
    instructor: Optional[str] = None
    capacity: int = 30
    enrolled: int = 0
    start_date: Optional[str] = None
    status: str = "active"
    created_at: Optional[str] = None


# ---------------------------------------------------------------------------
# 4.2 Module: Visa Assistant
# ---------------------------------------------------------------------------

class VisaTypeEnum(str, Enum):
    TOURIST = "Tourist"
    WORK = "Work"
    STUDY = "Study"
    BUSINESS = "Business"

class VisaApplicationCreate(BaseModel):
    full_name: Optional[str] = None
    applicant_name: Optional[str] = None
    address: Optional[str] = "Addis Ababa"
    phone: Optional[str] = "+251900000000"
    email: Optional[EmailStr] = "applicant@test.com"
    country: str = Field(default="Ethiopia", max_length=100)
    destination_country: str = Field(min_length=1, max_length=100)
    visa_type: str = "Tourist"
    passport_number: Optional[str] = None
    nationality: Optional[str] = None
    passport_upload_url: Optional[str] = None
    supporting_document_urls: list[str] = Field(default_factory=list)
    advance_payment_method: str = "TeleBirr"
    advance_amount: float = Field(default=5000.0, ge=0)
    status: Optional[str] = "draft"
    notes: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def reconcile_names(cls, values: Any) -> Any:
        if isinstance(values, dict):
            if "applicant_name" in values and "full_name" not in values:
                values["full_name"] = values["applicant_name"]
            elif "full_name" in values and "applicant_name" not in values:
                values["applicant_name"] = values["full_name"]
            if not values.get("full_name") and not values.get("applicant_name"):
                values["full_name"] = "Visa Applicant"
                values["applicant_name"] = "Visa Applicant"
        return values

class VisaApplicationUpdate(BaseModel):
    full_name: Optional[str] = Field(default=None, max_length=200)
    applicant_name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = Field(default=None, max_length=50)
    email: Optional[EmailStr] = None
    country: Optional[str] = None
    destination_country: Optional[str] = None
    visa_type: Optional[str] = None
    passport_upload_url: Optional[str] = None
    supporting_document_urls: Optional[list[str]] = None
    advance_payment_method: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None

class RequestMoreInfoRequest(BaseModel):
    message: str = Field(min_length=1)
    requested_documents: list[str] = Field(default_factory=list)

class VisaApplicationResponse(BaseModel):
    id: str
    tenant_id: str
    reference_code: Optional[str] = None
    full_name: Optional[str] = None
    applicant_name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    country: str = "Ethiopia"
    destination_country: str
    visa_type: str = "Tourist"
    passport_number: Optional[str] = None
    nationality: Optional[str] = None
    passport_upload_url: Optional[str] = None
    supporting_document_urls: list[str] = Field(default_factory=list)
    advance_payment_method: str = "TeleBirr"
    advance_amount: float = 5000.0
    status: str = "draft"
    linked_crm_contact_id: Optional[str] = None
    linked_invoice_id: Optional[str] = None
    notes: Optional[str] = None
    ai_document_check_summary: Optional[str] = None
    payment_receipt: Optional[dict[str, Any]] = None
    ai_generated_result: Optional[dict[str, Any]] = None
    created_at: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def reconcile_response_names(cls, values: Any) -> Any:
        if isinstance(values, dict):
            if "applicant_name" in values and "full_name" not in values:
                values["full_name"] = values["applicant_name"]
            elif "full_name" in values and "applicant_name" not in values:
                values["applicant_name"] = values["full_name"]
            if "id" in values and not values.get("reference_code"):
                values["reference_code"] = f"ZAC-VIS-{abs(hash(values['id'])) % 9000 + 1000}"
        return values


# ---------------------------------------------------------------------------
# 4.3 Module: Travel Agent
# ---------------------------------------------------------------------------

class TravelRequestCreate(BaseModel):
    full_name: str = Field(min_length=1, max_length=200)
    address: Optional[str] = "Addis Ababa"
    phone: Optional[str] = "+251900000000"
    email: Optional[EmailStr] = None
    country: str = Field(default="Ethiopia", max_length=100)
    destination_country: str = Field(min_length=1, max_length=100)
    budget: float = Field(gt=0)
    passport_upload_url: Optional[str] = None
    advance_payment_method: str = "TeleBirr"
    travel_date_preference: Optional[str] = None
    notes: Optional[str] = None

class TravelRequestUpdate(BaseModel):
    full_name: Optional[str] = Field(default=None, max_length=200)
    address: Optional[str] = None
    phone: Optional[str] = Field(default=None, max_length=50)
    email: Optional[EmailStr] = None
    country: Optional[str] = None
    destination_country: Optional[str] = None
    budget: Optional[float] = Field(default=None, gt=0)
    quoted_price: Optional[float] = None
    passport_upload_url: Optional[str] = None
    advance_payment_method: Optional[str] = None
    travel_date_preference: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None

class TravelRequestResponse(BaseModel):
    id: str
    tenant_id: str
    reference_code: Optional[str] = None
    full_name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    country: str = "Ethiopia"
    destination_country: str
    budget: float
    quoted_price: Optional[float] = None
    passport_upload_url: Optional[str] = None
    advance_payment_method: str = "TeleBirr"
    travel_date_preference: Optional[str] = None
    status: str = "Pending"
    linked_crm_contact_id: Optional[str] = None
    linked_invoice_id: Optional[str] = None
    notes: Optional[str] = None
    ai_itinerary_suggestion: Optional[str] = None
    payment_receipt: Optional[dict[str, Any]] = None
    ai_generated_result: Optional[dict[str, Any]] = None
    created_at: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def set_travel_ref(cls, values: Any) -> Any:
        if isinstance(values, dict):
            if "id" in values and not values.get("reference_code"):
                values["reference_code"] = f"ZAC-TRV-{abs(hash(values['id'])) % 9000 + 1000}"
        return values


# ---------------------------------------------------------------------------
# 4.4 Module: Software Development
# ---------------------------------------------------------------------------

class SoftwareProjectCreate(BaseModel):
    project_name: str = Field(min_length=1, max_length=200)
    client_name: str = Field(min_length=1, max_length=200)
    email: EmailStr
    phone: Optional[str] = "+251900000000"
    industry: Optional[str] = "Technology"
    platforms: list[str] = Field(default_factory=lambda: ["Web", "Android", "iOS"])
    project_description: str = Field(min_length=1)
    problem_to_solve: Optional[str] = None
    required_features: list[str] = Field(default_factory=list)
    target_users: Optional[str] = None
    ai_requirements: Optional[str] = None
    integration_requirements: Optional[str] = None
    design_requirements: Optional[str] = None
    expected_timeline: Optional[str] = "8-12 Weeks"
    budget: float = Field(default=50000.0, ge=0)
    currency: str = "ETB"
    advance_payment_method: str = "CBE"
    advance_amount: float = Field(default=15000.0, ge=0)
    supporting_document_urls: list[str] = Field(default_factory=list)
    notes: Optional[str] = None

class SoftwareProjectUpdate(BaseModel):
    project_name: Optional[str] = None
    client_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    industry: Optional[str] = None
    platforms: Optional[list[str]] = None
    project_description: Optional[str] = None
    problem_to_solve: Optional[str] = None
    required_features: Optional[list[str]] = None
    target_users: Optional[str] = None
    ai_requirements: Optional[str] = None
    integration_requirements: Optional[str] = None
    design_requirements: Optional[str] = None
    expected_timeline: Optional[str] = None
    budget: Optional[float] = None
    status: Optional[str] = None
    notes: Optional[str] = None

class SoftwareProjectResponse(BaseModel):
    id: str
    tenant_id: str
    reference_code: Optional[str] = None
    project_name: str
    client_name: str
    email: str
    phone: Optional[str] = None
    industry: Optional[str] = None
    platforms: list[str] = Field(default_factory=list)
    project_description: str
    problem_to_solve: Optional[str] = None
    required_features: list[str] = Field(default_factory=list)
    target_users: Optional[str] = None
    ai_requirements: Optional[str] = None
    integration_requirements: Optional[str] = None
    design_requirements: Optional[str] = None
    expected_timeline: Optional[str] = None
    budget: float
    currency: str = "ETB"
    advance_payment_method: str = "CBE"
    advance_amount: float = 15000.0
    status: str = "Pending"
    payment_status: str = "Pending"
    linked_crm_contact_id: Optional[str] = None
    linked_invoice_id: Optional[str] = None
    supporting_document_urls: list[str] = Field(default_factory=list)
    notes: Optional[str] = None
    payment_receipt: Optional[dict[str, Any]] = None
    ai_generated_result: Optional[dict[str, Any]] = None
    admin_response: Optional[dict[str, Any]] = None
    created_at: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def set_software_ref(cls, values: Any) -> Any:
        if isinstance(values, dict):
            if "id" in values and not values.get("reference_code"):
                values["reference_code"] = f"ZAC-DEV-{abs(hash(values['id'])) % 9000 + 1000}"
        return values


# Legacy Booking aliases
class BookingCreate(BaseModel):
    traveler_name: str = Field(min_length=1, max_length=200)
    destination: str = Field(min_length=1, max_length=200)
    departure_date: Optional[str] = None
    return_date: Optional[str] = None
    booking_type: str = Field(default="flight", max_length=50)
    status: str = Field(default="pending", max_length=30)
    notes: Optional[str] = None

class BookingUpdate(BaseModel):
    traveler_name: Optional[str] = Field(default=None, max_length=200)
    destination: Optional[str] = Field(default=None, max_length=200)
    departure_date: Optional[str] = None
    return_date: Optional[str] = None
    booking_type: Optional[str] = Field(default=None, max_length=50)
    status: Optional[str] = Field(default=None, max_length=30)
    notes: Optional[str] = None

class BookingResponse(BaseModel):
    id: str
    tenant_id: str
    traveler_name: str
    destination: str
    departure_date: Optional[str] = None
    return_date: Optional[str] = None
    booking_type: str = "flight"
    status: str = "pending"
    notes: Optional[str] = None
    created_at: Optional[str] = None


# ---------------------------------------------------------------------------
# 4.4 Module: Customer Support
# ---------------------------------------------------------------------------

class TicketPriority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    URGENT = "Urgent"

class TicketStatus(str, Enum):
    OPEN = "Open"
    IN_PROGRESS = "InProgress"
    WAITING_ON_CLIENT = "WaitingOnClient"
    RESOLVED = "Resolved"
    CLOSED = "Closed"

class TicketMessage(BaseModel):
    id: str
    sender_type: str = "client"  # client, admin, ai
    sender_name: str
    message: str
    created_at: str

class SupportTicketCreate(BaseModel):
    full_name: str = Field(min_length=1, max_length=200)
    email: EmailStr
    phone: Optional[str] = None
    subject: str = Field(min_length=1, max_length=200)
    message: str = Field(min_length=1)
    category: str = Field(default="general", max_length=50)
    priority: TicketPriority = TicketPriority.MEDIUM
    linked_crm_contact_id: Optional[str] = None

class SupportTicketReplyRequest(BaseModel):
    message: str = Field(min_length=1)
    status_update: Optional[TicketStatus] = None

class SupportTicketResponse(BaseModel):
    id: str
    tenant_id: str
    full_name: str
    email: str
    phone: Optional[str] = None
    subject: str
    message: str
    category: str = "general"
    priority: str = "Medium"
    status: str = "Open"
    assigned_admin_id: Optional[str] = None
    thread: list[TicketMessage] = Field(default_factory=list)
    ai_suggested_reply: Optional[str] = None
    linked_crm_contact_id: Optional[str] = None
    created_at: str
    updated_at: str


# ---------------------------------------------------------------------------
# 6. Dynamic Module System (for future business lines)
# ---------------------------------------------------------------------------

class FieldTypeEnum(str, Enum):
    TEXT = "text"
    NUMBER = "number"
    DROPDOWN = "dropdown"
    FILE = "file"
    DATE = "date"
    BOOLEAN = "boolean"
    TEXTAREA = "textarea"

class ModuleFieldDefinition(BaseModel):
    id: str
    field_name: str
    label: str
    field_type: FieldTypeEnum = FieldTypeEnum.TEXT
    is_required: bool = True
    options: list[str] = Field(default_factory=list)
    help_text: Optional[str] = None
    order: int = 0

class BusinessModuleCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    key: str = Field(min_length=1, max_length=50, pattern="^[a-z0-9_]+$")
    description: Optional[str] = None
    icon_url: Optional[str] = "Layers"
    requires_payment: bool = False
    base_amount: float = 0.0
    fields: list[ModuleFieldDefinition] = Field(default_factory=list)

class BusinessModule(BaseModel):
    id: str
    tenant_id: str
    name: str
    key: str
    description: Optional[str] = None
    is_active: bool = True
    icon_url: Optional[str] = "Layers"
    requires_payment: bool = False
    base_amount: float = 0.0
    fields: list[ModuleFieldDefinition] = Field(default_factory=list)
    created_at: str

class ModuleSubmissionCreate(BaseModel):
    full_name: str = Field(min_length=1, max_length=200)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    data_json: dict[str, Any] = Field(default_factory=dict)
    payment_method: Optional[str] = "TeleBirr"

class ModuleSubmissionUpdate(BaseModel):
    status: Optional[str] = None
    data_json: Optional[dict[str, Any]] = None

class ModuleSubmission(BaseModel):
    id: str
    tenant_id: str
    module_id: str
    module_key: str
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    data_json: dict[str, Any] = Field(default_factory=dict)
    status: str = "Pending"
    linked_crm_contact_id: Optional[str] = None
    linked_invoice_id: Optional[str] = None
    created_at: str
    updated_at: str


# ---------------------------------------------------------------------------
# 8. AI-Enhanced Features
# ---------------------------------------------------------------------------

class AiCourseRecommendationRequest(BaseModel):
    education_level: str
    interests: str

class AiDocumentCheckRequest(BaseModel):
    visa_type: str
    provided_documents: list[str]

class AiItineraryRequest(BaseModel):
    destination: str
    budget: float
    travel_dates: Optional[str] = None

class AiTicketReplyRequest(BaseModel):
    ticket_id: str
    subject: str
    message: str


# ---------------------------------------------------------------------------
# HRM & Marketing (Retained for backwards compatibility)
# ---------------------------------------------------------------------------

class EmployeeCreate(BaseModel):
    full_name: str = Field(min_length=1, max_length=200)
    email: EmailStr
    department: str = Field(default="general", max_length=100)
    role: str = Field(default="staff", max_length=50)
    status: str = Field(default="active", max_length=30)

class EmployeeUpdate(BaseModel):
    full_name: Optional[str] = Field(default=None, max_length=200)
    email: Optional[EmailStr] = None
    department: Optional[str] = Field(default=None, max_length=100)
    role: Optional[str] = Field(default=None, max_length=50)
    status: Optional[str] = Field(default=None, max_length=30)

class EmployeeResponse(BaseModel):
    id: str
    tenant_id: str
    full_name: str
    email: str
    department: str = "general"
    role: str = "staff"
    status: str = "active"
    created_at: Optional[str] = None


# ---------------------------------------------------------------------------
# HRM Leave, Attendance & Payroll Models
# ---------------------------------------------------------------------------

class LeaveRequestCreate(BaseModel):
    employee_id: str
    leave_type: str = Field(default="Annual", description="Annual, Sick, Maternity, Paternity, Unpaid")
    start_date: str
    end_date: str
    reason: Optional[str] = None

class LeaveRequestUpdate(BaseModel):
    status: str = Field(description="approved, rejected, pending")
    admin_comment: Optional[str] = None

class LeaveRequestResponse(BaseModel):
    id: str
    tenant_id: str
    employee_id: str
    employee_name: Optional[str] = None
    leave_type: str
    start_date: str
    end_date: str
    reason: Optional[str] = None
    status: str = "pending"
    admin_comment: Optional[str] = None
    created_at: Optional[str] = None

class AttendanceRecordCreate(BaseModel):
    employee_id: str
    date: str
    status: str = Field(default="Present", description="Present, Absent, Late, HalfDay")
    check_in: Optional[str] = None
    check_out: Optional[str] = None
    notes: Optional[str] = None

class AttendanceRecordResponse(BaseModel):
    id: str
    tenant_id: str
    employee_id: str
    employee_name: Optional[str] = None
    date: str
    status: str
    check_in: Optional[str] = None
    check_out: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[str] = None

class PayrollRunCreate(BaseModel):
    month: str = Field(description="YYYY-MM format e.g. 2026-08")
    base_salaries_override: Optional[dict[str, float]] = None

class PayrollRecordResponse(BaseModel):
    id: str
    tenant_id: str
    employee_id: str
    employee_name: str
    month: str
    gross_salary: float
    tax_deduction: float
    pension_deduction: float
    net_salary: float
    currency: str = "ETB"
    status: str = "paid"
    disbursed_at: Optional[str] = None
    created_at: Optional[str] = None

class CampaignCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    channel: str = Field(default="email", max_length=50)
    budget: float = Field(default=0, ge=0)
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    status: str = Field(default="draft", max_length=30)
    description: Optional[str] = None

class CampaignUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=200)
    channel: Optional[str] = Field(default=None, max_length=50)
    budget: Optional[float] = Field(default=None, ge=0)
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    status: Optional[str] = Field(default=None, max_length=30)
    description: Optional[str] = None

class CampaignResponse(BaseModel):
    id: str
    tenant_id: str
    name: str
    channel: str = "email"
    budget: float = 0
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    status: str = "draft"
    description: Optional[str] = None
    created_at: Optional[str] = None


# ---------------------------------------------------------------------------
# Admin & Settings
# ---------------------------------------------------------------------------

class AdminUserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=1, max_length=200)
    role: str = Field(default="client", max_length=30)
    password: str = Field(min_length=8)

class AdminUserUpdate(BaseModel):
    full_name: Optional[str] = Field(default=None, max_length=200)
    role: Optional[str] = Field(default=None, max_length=30)
    status: Optional[str] = Field(default=None, max_length=30)

class AuditLogResponse(BaseModel):
    id: str
    timestamp: str
    action: str
    user_email: str
    tenant_id: str
    resource: str
    details: Optional[str] = None

class SystemSettingsUpdate(BaseModel):
    default_receiving_account: Optional[str] = None
    default_payment_methods: Optional[list[str]] = None
    courses_list: Optional[list[str]] = None
    visa_types_list: Optional[list[str]] = None
    education_levels_list: Optional[list[str]] = None


# ---------------------------------------------------------------------------
# Automation & External Integration Models
# ---------------------------------------------------------------------------

class AutomationJobCreate(BaseModel):
    job_type: str = Field(min_length=1, max_length=100)  # e.g. service_activation, n8n_workflow, email_campaign
    entity_type: str = Field(min_length=1, max_length=100)  # student, visa, travel, software, custom
    entity_id: str = Field(min_length=1, max_length=100)
    payload: dict[str, Any] = Field(default_factory=dict)
    webhook_url: Optional[str] = None
    max_retries: int = Field(default=3, ge=0, le=10)

class AutomationJobResponse(BaseModel):
    id: str
    tenant_id: str
    job_type: str
    entity_type: str
    entity_id: str
    status: str  # pending, processing, completed, failed, retry, cancelled
    retry_count: int = 0
    max_retries: int = 3
    payload: dict[str, Any] = Field(default_factory=dict)
    result_data: Optional[dict[str, Any]] = None
    error_message: Optional[str] = None
    webhook_url: Optional[str] = None
    created_at: str
    updated_at: str
    completed_at: Optional[str] = None

class AutomationCallbackPayload(BaseModel):
    status: str  # completed, failed
    result_data: Optional[dict[str, Any]] = None
    error_message: Optional[str] = None
    deliverable_urls: Optional[list[str]] = None
    notes: Optional[str] = None

class AutomationWebhookPayload(BaseModel):
    event: str
    job_id: Optional[str] = None
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    data: dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Admin Search, Sort, Filter & AI Query Models
# ---------------------------------------------------------------------------

class AdminSearchResultItem(BaseModel):
    id: str
    module: str
    entity_type: str
    title: str
    subtitle: Optional[str] = None
    status: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    amount: Optional[float] = None
    currency: Optional[str] = None
    priority: Optional[str] = None
    category: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    reference_code: Optional[str] = None
    detail_url: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class AdminSearchPagination(BaseModel):
    page: int = 1
    page_size: int = 25
    total_count: int = 0
    total_pages: int = 1
    has_next: bool = False
    has_prev: bool = False


class AdminSearchFacet(BaseModel):
    key: str
    label: str
    count: int


class AdminSearchResponse(BaseModel):
    query: Optional[str] = None
    count: int = 0
    module_filter: Optional[str] = "all"
    status_filter: Optional[str] = "all"
    sort_by: str = "newest"
    pagination: AdminSearchPagination
    module_facets: list[AdminSearchFacet] = Field(default_factory=list)
    status_facets: list[AdminSearchFacet] = Field(default_factory=list)
    results: list[AdminSearchResultItem] = Field(default_factory=list)


class AdminAiSearchRequest(BaseModel):
    query: str = Field(min_length=2, max_length=500)
    max_results: int = Field(default=20, ge=1, le=100)


class AdminAiSearchResponse(BaseModel):
    original_query: str
    parsed_intent: str
    ai_summary: str
    total_found: int
    matched_modules: list[str] = Field(default_factory=list)
    results: list[AdminSearchResultItem] = Field(default_factory=list)


