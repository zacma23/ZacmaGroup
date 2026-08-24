-- ============================================================================
-- Migration: 20260823000004_services_and_support.sql
-- Description: Business services (Visa, Travel, Marketing, Dynamic Modules),
--              Approvals workflow, Support tickets & Telegram threads, Notifications,
--              System Settings, and System Audit Logs.
-- ============================================================================

-- ============================================================================
-- Table: public.visa_applications
-- Visa processing with passport uploads and embassy liaison status
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.visa_applications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
  reference_code TEXT NOT NULL,
  full_name TEXT NOT NULL,
  email TEXT NOT NULL,
  phone TEXT NOT NULL,
  address TEXT,
  country TEXT NOT NULL DEFAULT 'Ethiopia',
  destination_country TEXT NOT NULL,
  visa_type TEXT NOT NULL DEFAULT 'Tourist' CHECK (visa_type IN ('Tourist', 'Study', 'Work', 'Business', 'Medical', 'Other')),
  passport_upload_url TEXT,
  supporting_document_urls TEXT[] DEFAULT ARRAY[]::TEXT[],
  advance_payment_method TEXT NOT NULL DEFAULT 'CBE',
  advance_amount NUMERIC(12, 2) NOT NULL DEFAULT 5000.00,
  currency TEXT NOT NULL DEFAULT 'ETB',
  status TEXT NOT NULL DEFAULT 'Pending' CHECK (status IN ('Pending', 'UnderReview', 'DocumentsRequested', 'Approved', 'Rejected', 'Completed', 'Cancelled')),
  embassy_appointment_date TIMESTAMPTZ,
  assigned_officer_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  notes TEXT,
  metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT uq_visa_app_ref UNIQUE (tenant_id, reference_code)
);

CREATE INDEX IF NOT EXISTS idx_visa_tenant ON public.visa_applications(tenant_id);
CREATE INDEX IF NOT EXISTS idx_visa_ref ON public.visa_applications(reference_code);
CREATE INDEX IF NOT EXISTS idx_visa_email ON public.visa_applications(email);
CREATE INDEX IF NOT EXISTS idx_visa_status ON public.visa_applications(status);

DROP TRIGGER IF EXISTS trg_visa_applications_updated_at ON public.visa_applications;
CREATE TRIGGER trg_visa_applications_updated_at
  BEFORE UPDATE ON public.visa_applications
  FOR EACH ROW
  EXECUTE FUNCTION public.set_current_timestamp_updated_at();

-- ============================================================================
-- Table: public.travel_requests
-- Travel agency bookings, flight ticketing, and 5-day holiday itineraries
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.travel_requests (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
  reference_code TEXT NOT NULL,
  full_name TEXT NOT NULL,
  email TEXT NOT NULL,
  phone TEXT NOT NULL,
  address TEXT,
  destination_country TEXT NOT NULL,
  travel_date_preference TEXT NOT NULL,
  budget NUMERIC(12, 2) NOT NULL DEFAULT 8000.00,
  currency TEXT NOT NULL DEFAULT 'ETB',
  advance_payment_method TEXT NOT NULL DEFAULT 'Awash',
  advance_amount NUMERIC(12, 2) NOT NULL DEFAULT 8000.00,
  status TEXT NOT NULL DEFAULT 'Pending' CHECK (status IN ('Pending', 'UnderReview', 'Confirmed', 'Ticketed', 'Completed', 'Cancelled')),
  booking_type TEXT NOT NULL DEFAULT 'package' CHECK (booking_type IN ('flight', 'hotel', 'package', 'custom')),
  notes TEXT,
  itinerary_details JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT uq_travel_req_ref UNIQUE (tenant_id, reference_code)
);

CREATE INDEX IF NOT EXISTS idx_travel_tenant ON public.travel_requests(tenant_id);
CREATE INDEX IF NOT EXISTS idx_travel_ref ON public.travel_requests(reference_code);
CREATE INDEX IF NOT EXISTS idx_travel_status ON public.travel_requests(status);

DROP TRIGGER IF EXISTS trg_travel_requests_updated_at ON public.travel_requests;
CREATE TRIGGER trg_travel_requests_updated_at
  BEFORE UPDATE ON public.travel_requests
  FOR EACH ROW
  EXECUTE FUNCTION public.set_current_timestamp_updated_at();

-- ============================================================================
-- Table: public.marketing_campaigns
-- Marketing service management, advertising, and branding packages
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.marketing_campaigns (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  channel TEXT NOT NULL DEFAULT 'Social & Search Ads',
  budget NUMERIC(12, 2) NOT NULL DEFAULT 15000.00,
  currency TEXT NOT NULL DEFAULT 'ETB',
  start_date DATE,
  end_date DATE,
  status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('draft', 'active', 'paused', 'completed', 'cancelled')),
  description TEXT,
  metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_marketing_tenant ON public.marketing_campaigns(tenant_id);

DROP TRIGGER IF EXISTS trg_marketing_campaigns_updated_at ON public.marketing_campaigns;
CREATE TRIGGER trg_marketing_campaigns_updated_at
  BEFORE UPDATE ON public.marketing_campaigns
  FOR EACH ROW
  EXECUTE FUNCTION public.set_current_timestamp_updated_at();

-- ============================================================================
-- Table: public.business_modules & public.module_submissions
-- Dynamic module engine for custom lines of business
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.business_modules (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  slug TEXT NOT NULL,
  description TEXT,
  form_fields JSONB NOT NULL DEFAULT '[]'::jsonb,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT uq_biz_modules_slug UNIQUE (tenant_id, slug)
);

CREATE TABLE IF NOT EXISTS public.module_submissions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
  module_slug TEXT NOT NULL,
  reference_code TEXT NOT NULL,
  customer_name TEXT NOT NULL,
  customer_email TEXT,
  customer_phone TEXT,
  form_data JSONB NOT NULL DEFAULT '{}'::jsonb,
  status TEXT NOT NULL DEFAULT 'Pending' CHECK (status IN ('Pending', 'Approved', 'Rejected', 'Completed')),
  notes TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT uq_mod_sub_ref UNIQUE (tenant_id, reference_code)
);

CREATE INDEX IF NOT EXISTS idx_mod_submissions_tenant ON public.module_submissions(tenant_id);
CREATE INDEX IF NOT EXISTS idx_mod_submissions_slug ON public.module_submissions(module_slug);

-- ============================================================================
-- Table: public.approval_requests
-- Approval workflow engine for multi-tier management sign-offs
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.approval_requests (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
  entity_type TEXT NOT NULL,
  entity_id UUID NOT NULL,
  reference_code TEXT NOT NULL,
  current_status TEXT NOT NULL DEFAULT 'Pending' CHECK (current_status IN ('Pending', 'UnderReview', 'Approved', 'Denied', 'Completed', 'Cancelled')),
  requested_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  assigned_to UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  decision_comment TEXT,
  decided_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  decided_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_approval_tenant ON public.approval_requests(tenant_id);
CREATE INDEX IF NOT EXISTS idx_approval_entity ON public.approval_requests(entity_type, entity_id);

-- ============================================================================
-- Table: public.support_tickets & public.support_messages
-- Support desk & Telegram conversation thread integration
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.support_tickets (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
  reference_code TEXT NOT NULL,
  subject TEXT NOT NULL,
  full_name TEXT NOT NULL,
  email TEXT NOT NULL,
  phone TEXT,
  category TEXT NOT NULL DEFAULT 'General',
  priority TEXT NOT NULL DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
  channel TEXT NOT NULL DEFAULT 'web' CHECK (channel IN ('web', 'telegram', 'email', 'phone', 'chatbot')),
  status TEXT NOT NULL DEFAULT 'Open' CHECK (status IN ('Open', 'InProgress', 'WaitingClient', 'Resolved', 'Closed')),
  assigned_admin_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  ai_suggested_reply TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT uq_tickets_ref UNIQUE (tenant_id, reference_code)
);

CREATE INDEX IF NOT EXISTS idx_support_tickets_tenant ON public.support_tickets(tenant_id);
CREATE INDEX IF NOT EXISTS idx_support_tickets_status ON public.support_tickets(status);

CREATE TABLE IF NOT EXISTS public.support_messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
  ticket_id UUID NOT NULL REFERENCES public.support_tickets(id) ON DELETE CASCADE,
  reference_code TEXT NOT NULL,
  sender_type TEXT NOT NULL CHECK (sender_type IN ('client', 'ai', 'admin', 'system')),
  sender_name TEXT NOT NULL DEFAULT 'User',
  message TEXT NOT NULL,
  talk_to_human BOOLEAN NOT NULL DEFAULT FALSE,
  metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_support_messages_ticket ON public.support_messages(ticket_id);
CREATE INDEX IF NOT EXISTS idx_support_messages_ref ON public.support_messages(reference_code);

-- ============================================================================
-- Table: public.notification_templates & public.notification_logs
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.notification_templates (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
  template_key TEXT NOT NULL,
  subject TEXT NOT NULL,
  body_template TEXT NOT NULL,
  description TEXT,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT uq_notif_tmpl_key UNIQUE (tenant_id, template_key)
);

CREATE TABLE IF NOT EXISTS public.notification_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
  recipient_email TEXT,
  recipient_phone TEXT,
  template_key TEXT NOT NULL,
  subject TEXT NOT NULL,
  body TEXT NOT NULL,
  channel TEXT NOT NULL DEFAULT 'email' CHECK (channel IN ('email', 'sms', 'telegram', 'push')),
  status TEXT NOT NULL DEFAULT 'sent' CHECK (status IN ('pending', 'sent', 'failed')),
  error_message TEXT,
  sent_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_notif_logs_tenant ON public.notification_logs(tenant_id);

-- ============================================================================
-- Table: public.system_settings & audit.system_audit_logs
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.system_settings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
  default_receiving_account TEXT NOT NULL DEFAULT '1000140145797',
  default_payment_methods TEXT[] DEFAULT ARRAY['TeleBirr', 'CBE', 'Awash', 'Abyssinia', 'Chapa']::TEXT[],
  courses_list TEXT[] DEFAULT ARRAY['Graphics Design', 'Video Editing', 'Web Design', 'Programming', 'AI', 'Accounting', 'Maintenance']::TEXT[],
  visa_types_list TEXT[] DEFAULT ARRAY['Tourist', 'Work', 'Study', 'Business']::TEXT[],
  education_levels_list TEXT[] DEFAULT ARRAY['High School', 'Diploma', 'Bachelor''s Degree', 'Master''s Degree', 'Other']::TEXT[],
  metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT uq_system_settings_tenant UNIQUE (tenant_id)
);

CREATE TABLE IF NOT EXISTS audit.system_audit_logs (
  id BIGSERIAL PRIMARY KEY,
  tenant_id UUID NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
  user_id UUID,
  user_email TEXT,
  action TEXT NOT NULL,
  resource TEXT NOT NULL,
  details TEXT,
  ip_address TEXT,
  metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_system_audit_tenant ON audit.system_audit_logs(tenant_id);
CREATE INDEX IF NOT EXISTS idx_system_audit_action ON audit.system_audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_system_audit_time ON audit.system_audit_logs(created_at);
