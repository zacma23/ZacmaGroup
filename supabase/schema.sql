-- ============================================================================
-- ZACMA TECHNOLOGY GROUP — COMPLETE SUPABASE DATABASE SCHEMA
-- Consolidated production schema for Supabase SQL Editor execution
-- ============================================================================

-- 1. Enable Extensions
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2. Schemas
CREATE SCHEMA IF NOT EXISTS public;
CREATE SCHEMA IF NOT EXISTS audit;
CREATE SCHEMA IF NOT EXISTS rag;
CREATE SCHEMA IF NOT EXISTS ai;
CREATE SCHEMA IF NOT EXISTS admin;

-- 3. Automatic updated_at Function
CREATE OR REPLACE FUNCTION public.set_current_timestamp_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = clock_timestamp();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 4. Tenants
CREATE TABLE IF NOT EXISTS public.tenants (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  slug TEXT NOT NULL,
  plan TEXT NOT NULL DEFAULT 'free',
  status TEXT NOT NULL DEFAULT 'active',
  metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by UUID,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT uq_tenants_slug UNIQUE (slug)
);
CREATE INDEX IF NOT EXISTS idx_tenants_slug ON public.tenants(slug);

DROP TRIGGER IF EXISTS trg_tenants_updated_at ON public.tenants;
CREATE TRIGGER trg_tenants_updated_at
  BEFORE UPDATE ON public.tenants
  FOR EACH ROW EXECUTE FUNCTION public.set_current_timestamp_updated_at();

INSERT INTO public.tenants (id, name, slug, plan, status)
VALUES ('00000000-0000-0000-0000-000000000001', 'Zacma Default Tenant', 'zacma-demo', 'enterprise', 'active')
ON CONFLICT (slug) DO NOTHING;

-- 5. Profiles & Roles
CREATE TABLE IF NOT EXISTS public.profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  tenant_id UUID NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
  email TEXT NOT NULL,
  full_name TEXT NOT NULL DEFAULT '',
  phone TEXT,
  avatar_url TEXT,
  role TEXT NOT NULL DEFAULT 'student' CHECK (role IN ('admin', 'staff', 'finance', 'student', 'client')),
  status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'suspended', 'pending', 'inactive')),
  metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_profiles_tenant_id ON public.profiles(tenant_id);
CREATE INDEX IF NOT EXISTS idx_profiles_role ON public.profiles(role);

DROP TRIGGER IF EXISTS trg_profiles_updated_at ON public.profiles;
CREATE TRIGGER trg_profiles_updated_at
  BEFORE UPDATE ON public.profiles
  FOR EACH ROW EXECUTE FUNCTION public.set_current_timestamp_updated_at();

-- Auth Helper Functions
CREATE OR REPLACE FUNCTION public.get_current_tenant_id()
RETURNS UUID AS $$
  SELECT COALESCE(
    (NULLIF(current_setting('request.jwt.claim.tenant_id', true), ''))::uuid,
    (SELECT tenant_id FROM public.profiles WHERE id = auth.uid() LIMIT 1),
    '00000000-0000-0000-0000-000000000001'::uuid
  );
$$ LANGUAGE sql STABLE SECURITY DEFINER;

CREATE OR REPLACE FUNCTION public.get_user_role()
RETURNS TEXT AS $$
  SELECT COALESCE(
    NULLIF(current_setting('request.jwt.claim.role', true), ''),
    (SELECT role FROM public.profiles WHERE id = auth.uid() LIMIT 1),
    'anon'
  );
$$ LANGUAGE sql STABLE SECURITY DEFINER;

CREATE OR REPLACE FUNCTION public.is_admin()
RETURNS BOOLEAN AS $$
  SELECT public.get_user_role() = 'admin';
$$ LANGUAGE sql STABLE SECURITY DEFINER;

CREATE OR REPLACE FUNCTION public.is_staff_or_admin()
RETURNS BOOLEAN AS $$
  SELECT public.get_user_role() IN ('admin', 'staff', 'finance');
$$ LANGUAGE sql STABLE SECURITY DEFINER;

-- Auth User Creation Trigger
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
DECLARE
  v_tenant_id UUID;
  v_role TEXT;
  v_name TEXT;
BEGIN
  v_tenant_id := COALESCE(
    (NEW.raw_user_meta_data->>'tenant_id')::uuid,
    '00000000-0000-0000-0000-000000000001'::uuid
  );
  v_role := COALESCE(NEW.raw_user_meta_data->>'role', 'student');
  v_name := COALESCE(NEW.raw_user_meta_data->>'full_name', NEW.raw_user_meta_data->>'name', split_part(NEW.email, '@', 1));

  INSERT INTO public.profiles (id, tenant_id, email, full_name, role, status, metadata)
  VALUES (NEW.id, v_tenant_id, NEW.email, v_name, v_role, 'active', NEW.raw_user_meta_data)
  ON CONFLICT (id) DO UPDATE SET
    email = EXCLUDED.email,
    full_name = CASE WHEN profiles.full_name = '' THEN EXCLUDED.full_name ELSE profiles.full_name END,
    updated_at = now();

  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- 6. Course Categories & Courses
CREATE TABLE IF NOT EXISTS public.course_categories (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
  code TEXT NOT NULL,
  name TEXT NOT NULL,
  description TEXT,
  display_order INT NOT NULL DEFAULT 0,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT uq_categories_tenant_code UNIQUE (tenant_id, code)
);

CREATE TABLE IF NOT EXISTS public.courses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
  category_id UUID REFERENCES public.course_categories(id) ON DELETE SET NULL,
  code TEXT NOT NULL,
  title TEXT NOT NULL,
  description TEXT,
  level TEXT NOT NULL DEFAULT 'All Levels' CHECK (level IN ('Beginner', 'Intermediate', 'Advanced', 'All Levels')),
  duration_hours INT NOT NULL DEFAULT 40,
  price NUMERIC(12, 2) NOT NULL DEFAULT 4500.00,
  currency TEXT NOT NULL DEFAULT 'ETB',
  instructor_name TEXT,
  capacity INT NOT NULL DEFAULT 30,
  enrolled_count INT NOT NULL DEFAULT 0,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT uq_courses_tenant_code UNIQUE (tenant_id, code)
);

DROP TRIGGER IF EXISTS trg_course_categories_updated_at ON public.course_categories;
CREATE TRIGGER trg_course_categories_updated_at
  BEFORE UPDATE ON public.course_categories
  FOR EACH ROW EXECUTE FUNCTION public.set_current_timestamp_updated_at();

DROP TRIGGER IF EXISTS trg_courses_updated_at ON public.courses;
CREATE TRIGGER trg_courses_updated_at
  BEFORE UPDATE ON public.courses
  FOR EACH ROW EXECUTE FUNCTION public.set_current_timestamp_updated_at();

-- 7. Students, Registrations & Attendance
CREATE TABLE IF NOT EXISTS public.students (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
  user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  full_name TEXT NOT NULL,
  email TEXT NOT NULL,
  phone TEXT,
  address TEXT,
  country TEXT NOT NULL DEFAULT 'Ethiopia',
  education_level TEXT NOT NULL DEFAULT 'Diploma' CHECK (education_level IN ('High School', 'Diploma', 'Bachelor''s Degree', 'Master''s Degree', 'Other')),
  emergency_contact TEXT,
  notes TEXT,
  metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT uq_students_tenant_email UNIQUE (tenant_id, email)
);

CREATE TABLE IF NOT EXISTS public.student_registrations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
  reference_code TEXT NOT NULL,
  student_id UUID NOT NULL REFERENCES public.students(id) ON DELETE CASCADE,
  course_id UUID REFERENCES public.courses(id) ON DELETE RESTRICT,
  course_title TEXT NOT NULL,
  education_level TEXT NOT NULL DEFAULT 'Diploma',
  maintenance_sub_type TEXT CHECK (maintenance_sub_type IN ('Mobile', 'Computer', 'Printer', 'Electronics', NULL)),
  schedule_preference TEXT NOT NULL DEFAULT 'Standard',
  payment_method TEXT NOT NULL DEFAULT 'TeleBirr',
  application_status TEXT NOT NULL DEFAULT 'Pending' CHECK (application_status IN ('Pending', 'UnderReview', 'Approved', 'Rejected', 'Completed', 'Cancelled')),
  payment_status TEXT NOT NULL DEFAULT 'Pending' CHECK (payment_status IN ('Pending', 'Paid', 'Partial', 'Refunded', 'Cancelled')),
  tuition_amount NUMERIC(12, 2) NOT NULL DEFAULT 4500.00,
  currency TEXT NOT NULL DEFAULT 'ETB',
  ai_course_recommendation TEXT,
  interests TEXT,
  notes TEXT,
  reviewed_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  reviewed_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT uq_student_reg_ref UNIQUE (tenant_id, reference_code)
);

CREATE TABLE IF NOT EXISTS public.student_attendance (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
  registration_id UUID NOT NULL REFERENCES public.student_registrations(id) ON DELETE CASCADE,
  session_date DATE NOT NULL,
  session_title TEXT NOT NULL,
  present BOOLEAN NOT NULL DEFAULT TRUE,
  notes TEXT,
  marked_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT uq_attendance_session UNIQUE (registration_id, session_date, session_title)
);

-- 8. CRM Engine
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

CREATE TABLE IF NOT EXISTS public.crm_notes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
  contact_id UUID NOT NULL REFERENCES public.crm_contacts(id) ON DELETE CASCADE,
  author_email TEXT NOT NULL,
  author_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  content TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 9. Payments & Invoices
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

-- 10. Visa, Travel & Marketing Services
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

-- 11. Approvals, Support & Telegram Messages
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

-- 12. Settings & Notifications
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

-- 13. Enable Row-Level Security
ALTER TABLE public.tenants ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.course_categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.courses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.students ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.student_registrations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.student_attendance ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.crm_contacts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.crm_timeline ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.crm_notes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.invoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.payment_attempts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.visa_applications ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.travel_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.marketing_campaigns ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.business_modules ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.module_submissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.approval_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.support_tickets ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.support_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.notification_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.notification_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.system_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit.system_audit_logs ENABLE ROW LEVEL SECURITY;

-- 14. Course Seed Data
DO $$
DECLARE
  v_tid UUID := '00000000-0000-0000-0000-000000000001';
BEGIN
  INSERT INTO public.course_categories (id, tenant_id, code, name, description, display_order)
  VALUES
    ('c0000000-0000-0000-0000-000000000001', v_tid, 'IT_PROG', 'Software & IT Engineering', 'Programming, Web & AI tracks', 1),
    ('c0000000-0000-0000-0000-000000000002', v_tid, 'CREATIVE', 'Creative & Digital Media', 'Graphics, motion and video editing', 2),
    ('c0000000-0000-0000-0000-000000000003', v_tid, 'HARDWARE', 'Hardware & Electronics', 'Mobile & computer hardware maintenance', 3),
    ('c0000000-0000-0000-0000-000000000004', v_tid, 'BUSINESS', 'Business & Accounting', 'Finance, accounting and commerce software', 4)
  ON CONFLICT (tenant_id, code) DO NOTHING;

  INSERT INTO public.courses (tenant_id, category_id, code, title, description, level, duration_hours, price, currency, instructor_name, capacity)
  VALUES
    (v_tid, 'c0000000-0000-0000-0000-000000000001', 'PROG_01', 'Programming (Python & Full-Stack)', 'Comprehensive hands-on programming with Python, REST APIs, and modern web architectures.', 'Beginner', 45, 4500.00, 'ETB', 'Senior Developer', 30),
    (v_tid, 'c0000000-0000-0000-0000-000000000001', 'AI_01', 'Artificial Intelligence & Applied ML', 'Practical machine learning, automation pipelines, and intelligent agent development.', 'Intermediate', 40, 4500.00, 'ETB', 'AI Specialist', 25),
    (v_tid, 'c0000000-0000-0000-0000-000000000001', 'WEB_01', 'Web Design & Frontend Development', 'Modern responsive UI engineering with Next.js, HTML5, CSS3, and Tailwind CSS.', 'Beginner', 40, 4500.00, 'ETB', 'Lead UI Engineer', 30),
    (v_tid, 'c0000000-0000-0000-0000-000000000002', 'GRAPH_01', 'Graphics Design & Brand Identity', 'Visual design principles, Adobe Photoshop, Illustrator, and corporate brand development.', 'Beginner', 40, 4500.00, 'ETB', 'Creative Art Director', 25),
    (v_tid, 'c0000000-0000-0000-0000-000000000002', 'VID_01', 'Video Editing & Motion Graphics', 'Professional video editing, Adobe Premiere Pro, After Effects, and color grading.', 'Beginner', 40, 4500.00, 'ETB', 'Media Producer', 25),
    (v_tid, 'c0000000-0000-0000-0000-000000000004', 'ACCT_01', 'Accounting & Financial Management', 'Practical accounting systems, Peachtree/QuickBooks, taxation, and financial reporting.', 'Beginner', 40, 4500.00, 'ETB', 'Certified Accountant', 30),
    (v_tid, 'c0000000-0000-0000-0000-000000000003', 'MAINT_MOB', 'Maintenance: Mobile Phone Repair', 'Diagnostic tools, smartphone screen replacement, motherboard circuit soldering & flashing.', 'Beginner', 50, 4500.00, 'ETB', 'Master Technician', 20),
    (v_tid, 'c0000000-0000-0000-0000-000000000003', 'MAINT_PC', 'Maintenance: Computer & Laptop Repair', 'Desktop/Laptop hardware diagnostics, BIOS repair, motherboard troubleshooting, and OS maintenance.', 'Beginner', 50, 4500.00, 'ETB', 'Hardware Engineer', 20)
  ON CONFLICT (tenant_id, code) DO NOTHING;
END $$;
