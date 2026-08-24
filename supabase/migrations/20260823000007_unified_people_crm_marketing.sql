-- ============================================================================
-- Migration: 20260823000007_unified_people_crm_marketing.sql
-- Description: Unified People, Organizations, CRM Opportunities, Activities,
--              Marketing Segments, Campaigns, and Communication Logs.
-- ============================================================================

-- 1. Table: public.organizations
CREATE TABLE IF NOT EXISTS public.organizations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  business_type TEXT NOT NULL DEFAULT 'Company',
  email TEXT,
  phone TEXT,
  website TEXT,
  industry TEXT,
  address TEXT,
  city TEXT,
  country TEXT NOT NULL DEFAULT 'Ethiopia',
  status TEXT NOT NULL DEFAULT 'Active' CHECK (status IN ('Active', 'Prospect', 'Partner', 'Vendor', 'Inactive')),
  source TEXT DEFAULT 'Inquiry',
  owner_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  notes TEXT,
  metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_organizations_tenant ON public.organizations(tenant_id);
CREATE INDEX IF NOT EXISTS idx_organizations_name ON public.organizations(name);
CREATE INDEX IF NOT EXISTS idx_organizations_status ON public.organizations(status);

-- 2. Table: public.people
CREATE TABLE IF NOT EXISTS public.people (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
  full_name TEXT NOT NULL,
  email TEXT,
  phone TEXT,
  alt_phone TEXT,
  organization_id UUID REFERENCES public.organizations(id) ON DELETE SET NULL,
  job_title TEXT,
  person_type TEXT NOT NULL DEFAULT 'Individual' CHECK (person_type IN ('Individual', 'Customer', 'Lead', 'Student', 'Staff', 'Partner', 'Vendor', 'Other')),
  status TEXT NOT NULL DEFAULT 'Active' CHECK (status IN ('Active', 'Lead', 'Prospect', 'Enrolled', 'Customer', 'Alumni', 'Inactive')),
  tags TEXT[] DEFAULT ARRAY[]::TEXT[],
  address TEXT,
  city TEXT,
  country TEXT NOT NULL DEFAULT 'Ethiopia',
  source TEXT DEFAULT 'Direct',
  notes TEXT,
  metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_people_tenant ON public.people(tenant_id);
CREATE INDEX IF NOT EXISTS idx_people_email ON public.people(email);
CREATE INDEX IF NOT EXISTS idx_people_phone ON public.people(phone);
CREATE INDEX IF NOT EXISTS idx_people_org ON public.people(organization_id);
CREATE INDEX IF NOT EXISTS idx_people_type ON public.people(person_type);
CREATE INDEX IF NOT EXISTS idx_people_status ON public.people(status);

-- 3. Table: public.crm_opportunities
CREATE TABLE IF NOT EXISTS public.crm_opportunities (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  person_id UUID REFERENCES public.people(id) ON DELETE SET NULL,
  organization_id UUID REFERENCES public.organizations(id) ON DELETE SET NULL,
  value NUMERIC(14, 2) NOT NULL DEFAULT 0.00,
  currency TEXT NOT NULL DEFAULT 'ETB',
  pipeline_stage TEXT NOT NULL DEFAULT 'New Lead' CHECK (pipeline_stage IN ('New Lead', 'Contacted', 'Qualified', 'Needs Analysis', 'Proposal', 'Negotiation', 'Won', 'Lost')),
  probability INT NOT NULL DEFAULT 20 CHECK (probability >= 0 AND probability <= 100),
  expected_close_date DATE,
  owner_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  source TEXT DEFAULT 'Inquiry',
  notes TEXT,
  status TEXT NOT NULL DEFAULT 'Open' CHECK (status IN ('Open', 'Won', 'Lost', 'Archived')),
  metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_crm_opportunities_tenant ON public.crm_opportunities(tenant_id);
CREATE INDEX IF NOT EXISTS idx_crm_opportunities_person ON public.crm_opportunities(person_id);
CREATE INDEX IF NOT EXISTS idx_crm_opportunities_org ON public.crm_opportunities(organization_id);
CREATE INDEX IF NOT EXISTS idx_crm_opportunities_stage ON public.crm_opportunities(pipeline_stage);
CREATE INDEX IF NOT EXISTS idx_crm_opportunities_status ON public.crm_opportunities(status);

-- 4. Table: public.crm_activities
CREATE TABLE IF NOT EXISTS public.crm_activities (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
  activity_type TEXT NOT NULL DEFAULT 'Note' CHECK (activity_type IN ('Call', 'Email', 'SMS', 'WhatsApp', 'Meeting', 'Task', 'Note', 'Follow-up')),
  subject TEXT NOT NULL,
  description TEXT,
  person_id UUID REFERENCES public.people(id) ON DELETE CASCADE,
  organization_id UUID REFERENCES public.organizations(id) ON DELETE SET NULL,
  opportunity_id UUID REFERENCES public.crm_opportunities(id) ON DELETE SET NULL,
  due_date TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  status TEXT NOT NULL DEFAULT 'Pending' CHECK (status IN ('Pending', 'Completed', 'Cancelled', 'Overdue')),
  actor TEXT NOT NULL DEFAULT 'system',
  metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_crm_activities_tenant ON public.crm_activities(tenant_id);
CREATE INDEX IF NOT EXISTS idx_crm_activities_person ON public.crm_activities(person_id);
CREATE INDEX IF NOT EXISTS idx_crm_activities_type ON public.crm_activities(activity_type);
CREATE INDEX IF NOT EXISTS idx_crm_activities_status ON public.crm_activities(status);

-- 5. Table: public.marketing_segments
CREATE TABLE IF NOT EXISTS public.marketing_segments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  description TEXT,
  filter_criteria JSONB NOT NULL DEFAULT '{}'::jsonb,
  is_dynamic BOOLEAN NOT NULL DEFAULT true,
  member_count INT NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_marketing_segments_tenant ON public.marketing_segments(tenant_id);

-- 6. Table: public.marketing_campaigns
CREATE TABLE IF NOT EXISTS public.marketing_campaigns (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  campaign_type TEXT NOT NULL DEFAULT 'Email' CHECK (campaign_type IN ('Email', 'SMS', 'Notification', 'WhatsApp', 'Other')),
  segment_id UUID REFERENCES public.marketing_segments(id) ON DELETE SET NULL,
  subject TEXT,
  message_body TEXT NOT NULL,
  template_id TEXT,
  sender TEXT DEFAULT 'Zacma Marketing <marketing@zacma.com>',
  status TEXT NOT NULL DEFAULT 'Draft' CHECK (status IN ('Draft', 'Scheduled', 'Sending', 'Sent', 'Cancelled')),
  scheduled_at TIMESTAMPTZ,
  sent_at TIMESTAMPTZ,
  total_recipients INT NOT NULL DEFAULT 0,
  delivered_count INT NOT NULL DEFAULT 0,
  opened_count INT NOT NULL DEFAULT 0,
  stats JSONB DEFAULT '{}'::jsonb,
  created_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_marketing_campaigns_tenant ON public.marketing_campaigns(tenant_id);
CREATE INDEX IF NOT EXISTS idx_marketing_campaigns_status ON public.marketing_campaigns(status);

-- 7. Table: public.communication_logs
CREATE TABLE IF NOT EXISTS public.communication_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
  channel TEXT NOT NULL DEFAULT 'Email',
  sender TEXT NOT NULL,
  recipient TEXT NOT NULL,
  person_id UUID REFERENCES public.people(id) ON DELETE SET NULL,
  organization_id UUID REFERENCES public.organizations(id) ON DELETE SET NULL,
  campaign_id UUID REFERENCES public.marketing_campaigns(id) ON DELETE SET NULL,
  subject TEXT,
  message_body TEXT,
  status TEXT NOT NULL DEFAULT 'Sent' CHECK (status IN ('Sent', 'Delivered', 'Failed', 'Opened', 'Clicked')),
  metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_communication_logs_tenant ON public.communication_logs(tenant_id);
CREATE INDEX IF NOT EXISTS idx_communication_logs_person ON public.communication_logs(person_id);
CREATE INDEX IF NOT EXISTS idx_communication_logs_campaign ON public.communication_logs(campaign_id);
