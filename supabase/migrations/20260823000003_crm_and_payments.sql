-- ============================================================================
-- Migration: 20260823000003_crm_and_payments.sql
-- Description: CRM Engine (Contacts, Lifecycle Timeline, Internal Notes) and
--              Payment Engine (Invoices, Payment Attempts, Verification).
-- ============================================================================

-- ============================================================================
-- Table: public.crm_contacts
-- Centralized customer directory across all operational modules
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.crm_contacts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
  full_name TEXT NOT NULL,
  email TEXT,
  phone TEXT,
  address TEXT,
  country TEXT NOT NULL DEFAULT 'Ethiopia',
  source_module TEXT NOT NULL DEFAULT 'Custom' CHECK (source_module IN ('Student', 'Visa', 'Travel', 'Marketing', 'Support', 'Custom')),
  status TEXT NOT NULL DEFAULT 'Lead' CHECK (status IN ('Lead', 'Active', 'Completed', 'Cancelled')),
  tags TEXT[] DEFAULT ARRAY[]::TEXT[],
  assigned_admin_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  linked_entity_id UUID,
  metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_crm_contacts_tenant ON public.crm_contacts(tenant_id);
CREATE INDEX IF NOT EXISTS idx_crm_contacts_email ON public.crm_contacts(email);
CREATE INDEX IF NOT EXISTS idx_crm_contacts_phone ON public.crm_contacts(phone);
CREATE INDEX IF NOT EXISTS idx_crm_contacts_status ON public.crm_contacts(status);
CREATE INDEX IF NOT EXISTS idx_crm_contacts_source ON public.crm_contacts(source_module);

DROP TRIGGER IF EXISTS trg_crm_contacts_updated_at ON public.crm_contacts;
CREATE TRIGGER trg_crm_contacts_updated_at
  BEFORE UPDATE ON public.crm_contacts
  FOR EACH ROW
  EXECUTE FUNCTION public.set_current_timestamp_updated_at();

-- ============================================================================
-- Table: public.crm_timeline
-- Chronological event history for CRM contacts
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.crm_timeline (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
  contact_id UUID NOT NULL REFERENCES public.crm_contacts(id) ON DELETE CASCADE,
  action TEXT NOT NULL,
  description TEXT NOT NULL,
  actor TEXT NOT NULL DEFAULT 'system',
  metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_crm_timeline_contact ON public.crm_timeline(contact_id);
CREATE INDEX IF NOT EXISTS idx_crm_timeline_created_at ON public.crm_timeline(created_at);

-- ============================================================================
-- Table: public.crm_notes
-- Internal notes on contacts by staff/admins
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.crm_notes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
  contact_id UUID NOT NULL REFERENCES public.crm_contacts(id) ON DELETE CASCADE,
  author_email TEXT NOT NULL,
  author_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  content TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_crm_notes_contact ON public.crm_notes(contact_id);

-- ============================================================================
-- Table: public.invoices
-- Multi-tenant invoices with official CBE receiving account 1000140145797
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.invoices (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
  reference_code TEXT NOT NULL,
  customer_name TEXT NOT NULL,
  customer_email TEXT,
  contact_id UUID REFERENCES public.crm_contacts(id) ON DELETE SET NULL,
  module_type TEXT NOT NULL DEFAULT 'general' CHECK (module_type IN ('Student', 'Visa', 'Travel', 'Marketing', 'general', 'support')),
  amount NUMERIC(12, 2) NOT NULL,
  currency TEXT NOT NULL DEFAULT 'ETB',
  payment_method TEXT NOT NULL DEFAULT 'CBE',
  receiving_account TEXT NOT NULL DEFAULT '1000140145797',
  due_date DATE,
  description TEXT,
  status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'sent', 'paid', 'confirmed', 'overdue', 'cancelled', 'rejected')),
  confirmed_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  confirmed_at TIMESTAMPTZ,
  rejection_reason TEXT,
  metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT uq_invoices_ref_code UNIQUE (tenant_id, reference_code)
);

CREATE INDEX IF NOT EXISTS idx_invoices_tenant ON public.invoices(tenant_id);
CREATE INDEX IF NOT EXISTS idx_invoices_ref_code ON public.invoices(reference_code);
CREATE INDEX IF NOT EXISTS idx_invoices_status ON public.invoices(status);
CREATE INDEX IF NOT EXISTS idx_invoices_contact ON public.invoices(contact_id);

DROP TRIGGER IF EXISTS trg_invoices_updated_at ON public.invoices;
CREATE TRIGGER trg_invoices_updated_at
  BEFORE UPDATE ON public.invoices
  FOR EACH ROW
  EXECUTE FUNCTION public.set_current_timestamp_updated_at();

-- ============================================================================
-- Table: public.payment_attempts
-- Payment proof submissions & receipt verification logs
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.payment_attempts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
  invoice_id UUID NOT NULL REFERENCES public.invoices(id) ON DELETE CASCADE,
  gateway TEXT NOT NULL,
  reference_number TEXT NOT NULL,
  proof_file_url TEXT,
  amount NUMERIC(12, 2),
  currency TEXT NOT NULL DEFAULT 'ETB',
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'rejected')),
  notes TEXT,
  verified_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  verified_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_payment_attempts_invoice ON public.payment_attempts(invoice_id);
CREATE INDEX IF NOT EXISTS idx_payment_attempts_ref ON public.payment_attempts(reference_number);
