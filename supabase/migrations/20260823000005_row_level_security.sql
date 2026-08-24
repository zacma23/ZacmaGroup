-- ============================================================================
-- Migration: 20260823000005_row_level_security.sql
-- Description: Complete Row-Level Security (RLS) policies for multi-tenancy,
--              role-based access control (Admin, Staff, Student, Client), and public intake.
-- ============================================================================

-- ============================================================================
-- 1. Enable Row Level Security on ALL Public Tables
-- ============================================================================
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

-- ============================================================================
-- 2. Profiles Policies
-- ============================================================================
DROP POLICY IF EXISTS "profiles_admin_all" ON public.profiles;
CREATE POLICY "profiles_admin_all" ON public.profiles
  FOR ALL
  USING (public.is_admin() AND tenant_id = public.get_current_tenant_id())
  WITH CHECK (public.is_admin() AND tenant_id = public.get_current_tenant_id());

DROP POLICY IF EXISTS "profiles_self_read" ON public.profiles;
CREATE POLICY "profiles_self_read" ON public.profiles
  FOR SELECT
  USING (id = auth.uid());

DROP POLICY IF EXISTS "profiles_self_update" ON public.profiles;
CREATE POLICY "profiles_self_update" ON public.profiles
  FOR UPDATE
  USING (id = auth.uid())
  WITH CHECK (id = auth.uid() AND role = (SELECT role FROM public.profiles WHERE id = auth.uid()));

-- ============================================================================
-- 3. Course Categories & Courses (Public Read, Admin/Staff Manage)
-- ============================================================================
DROP POLICY IF EXISTS "course_categories_public_read" ON public.course_categories;
CREATE POLICY "course_categories_public_read" ON public.course_categories
  FOR SELECT
  USING (is_active = TRUE);

DROP POLICY IF EXISTS "course_categories_admin_manage" ON public.course_categories;
CREATE POLICY "course_categories_admin_manage" ON public.course_categories
  FOR ALL
  USING (public.is_staff_or_admin() AND tenant_id = public.get_current_tenant_id())
  WITH CHECK (public.is_staff_or_admin() AND tenant_id = public.get_current_tenant_id());

DROP POLICY IF EXISTS "courses_public_read" ON public.courses;
CREATE POLICY "courses_public_read" ON public.courses
  FOR SELECT
  USING (is_active = TRUE);

DROP POLICY IF EXISTS "courses_admin_manage" ON public.courses;
CREATE POLICY "courses_admin_manage" ON public.courses
  FOR ALL
  USING (public.is_staff_or_admin() AND tenant_id = public.get_current_tenant_id())
  WITH CHECK (public.is_staff_or_admin() AND tenant_id = public.get_current_tenant_id());

-- ============================================================================
-- 4. Students & Registrations Policies
-- ============================================================================
DROP POLICY IF EXISTS "students_admin_all" ON public.students;
CREATE POLICY "students_admin_all" ON public.students
  FOR ALL
  USING (public.is_staff_or_admin() AND tenant_id = public.get_current_tenant_id())
  WITH CHECK (public.is_staff_or_admin() AND tenant_id = public.get_current_tenant_id());

DROP POLICY IF EXISTS "students_self_read" ON public.students;
CREATE POLICY "students_self_read" ON public.students
  FOR SELECT
  USING (user_id = auth.uid());

DROP POLICY IF EXISTS "students_public_insert" ON public.students;
CREATE POLICY "students_public_insert" ON public.students
  FOR INSERT
  WITH CHECK (TRUE);

-- Student Registrations
DROP POLICY IF EXISTS "student_reg_admin_all" ON public.student_registrations;
CREATE POLICY "student_reg_admin_all" ON public.student_registrations
  FOR ALL
  USING (public.is_staff_or_admin() AND tenant_id = public.get_current_tenant_id())
  WITH CHECK (public.is_staff_or_admin() AND tenant_id = public.get_current_tenant_id());

DROP POLICY IF EXISTS "student_reg_student_read" ON public.student_registrations;
CREATE POLICY "student_reg_student_read" ON public.student_registrations
  FOR SELECT
  USING (student_id IN (SELECT id FROM public.students WHERE user_id = auth.uid()));

DROP POLICY IF EXISTS "student_reg_public_insert" ON public.student_registrations;
CREATE POLICY "student_reg_public_insert" ON public.student_registrations
  FOR INSERT
  WITH CHECK (TRUE);

-- Attendance
DROP POLICY IF EXISTS "attendance_admin_manage" ON public.student_attendance;
CREATE POLICY "attendance_admin_manage" ON public.student_attendance
  FOR ALL
  USING (public.is_staff_or_admin() AND tenant_id = public.get_current_tenant_id())
  WITH CHECK (public.is_staff_or_admin() AND tenant_id = public.get_current_tenant_id());

DROP POLICY IF EXISTS "attendance_student_read" ON public.student_attendance;
CREATE POLICY "attendance_student_read" ON public.student_attendance
  FOR SELECT
  USING (registration_id IN (
    SELECT r.id FROM public.student_registrations r
    JOIN public.students s ON s.id = r.student_id
    WHERE s.user_id = auth.uid()
  ));

-- ============================================================================
-- 5. CRM Engine Policies
-- ============================================================================
DROP POLICY IF EXISTS "crm_contacts_admin_all" ON public.crm_contacts;
CREATE POLICY "crm_contacts_admin_all" ON public.crm_contacts
  FOR ALL
  USING (public.is_staff_or_admin() AND tenant_id = public.get_current_tenant_id())
  WITH CHECK (public.is_staff_or_admin() AND tenant_id = public.get_current_tenant_id());

DROP POLICY IF EXISTS "crm_timeline_admin_all" ON public.crm_timeline;
CREATE POLICY "crm_timeline_admin_all" ON public.crm_timeline
  FOR ALL
  USING (public.is_staff_or_admin() AND tenant_id = public.get_current_tenant_id())
  WITH CHECK (public.is_staff_or_admin() AND tenant_id = public.get_current_tenant_id());

DROP POLICY IF EXISTS "crm_notes_admin_all" ON public.crm_notes;
CREATE POLICY "crm_notes_admin_all" ON public.crm_notes
  FOR ALL
  USING (public.is_staff_or_admin() AND tenant_id = public.get_current_tenant_id())
  WITH CHECK (public.is_staff_or_admin() AND tenant_id = public.get_current_tenant_id());

-- ============================================================================
-- 6. Invoices & Payment Attempts Policies
-- ============================================================================
DROP POLICY IF EXISTS "invoices_admin_all" ON public.invoices;
CREATE POLICY "invoices_admin_all" ON public.invoices
  FOR ALL
  USING (public.is_staff_or_admin() AND tenant_id = public.get_current_tenant_id())
  WITH CHECK (public.is_staff_or_admin() AND tenant_id = public.get_current_tenant_id());

DROP POLICY IF EXISTS "invoices_customer_read" ON public.invoices;
CREATE POLICY "invoices_customer_read" ON public.invoices
  FOR SELECT
  USING (customer_email = (SELECT email FROM auth.users WHERE id = auth.uid()));

DROP POLICY IF EXISTS "payment_attempts_admin_all" ON public.payment_attempts;
CREATE POLICY "payment_attempts_admin_all" ON public.payment_attempts
  FOR ALL
  USING (public.is_staff_or_admin() AND tenant_id = public.get_current_tenant_id())
  WITH CHECK (public.is_staff_or_admin() AND tenant_id = public.get_current_tenant_id());

DROP POLICY IF EXISTS "payment_attempts_public_insert" ON public.payment_attempts;
CREATE POLICY "payment_attempts_public_insert" ON public.payment_attempts
  FOR INSERT
  WITH CHECK (TRUE);

-- ============================================================================
-- 7. Visa, Travel & Marketing Services Policies
-- ============================================================================
DROP POLICY IF EXISTS "visa_admin_all" ON public.visa_applications;
CREATE POLICY "visa_admin_all" ON public.visa_applications
  FOR ALL
  USING (public.is_staff_or_admin() AND tenant_id = public.get_current_tenant_id())
  WITH CHECK (public.is_staff_or_admin() AND tenant_id = public.get_current_tenant_id());

DROP POLICY IF EXISTS "visa_public_insert" ON public.visa_applications;
CREATE POLICY "visa_public_insert" ON public.visa_applications
  FOR INSERT
  WITH CHECK (TRUE);

DROP POLICY IF EXISTS "visa_self_read" ON public.visa_applications;
CREATE POLICY "visa_self_read" ON public.visa_applications
  FOR SELECT
  USING (email = (SELECT email FROM auth.users WHERE id = auth.uid()));

DROP POLICY IF EXISTS "travel_admin_all" ON public.travel_requests;
CREATE POLICY "travel_admin_all" ON public.travel_requests
  FOR ALL
  USING (public.is_staff_or_admin() AND tenant_id = public.get_current_tenant_id())
  WITH CHECK (public.is_staff_or_admin() AND tenant_id = public.get_current_tenant_id());

DROP POLICY IF EXISTS "travel_public_insert" ON public.travel_requests;
CREATE POLICY "travel_public_insert" ON public.travel_requests
  FOR INSERT
  WITH CHECK (TRUE);

DROP POLICY IF EXISTS "travel_self_read" ON public.travel_requests;
CREATE POLICY "travel_self_read" ON public.travel_requests
  FOR SELECT
  USING (email = (SELECT email FROM auth.users WHERE id = auth.uid()));

DROP POLICY IF EXISTS "marketing_admin_all" ON public.marketing_campaigns;
CREATE POLICY "marketing_admin_all" ON public.marketing_campaigns
  FOR ALL
  USING (public.is_staff_or_admin() AND tenant_id = public.get_current_tenant_id())
  WITH CHECK (public.is_staff_or_admin() AND tenant_id = public.get_current_tenant_id());

DROP POLICY IF EXISTS "mod_sub_admin_all" ON public.module_submissions;
CREATE POLICY "mod_sub_admin_all" ON public.module_submissions
  FOR ALL
  USING (public.is_staff_or_admin() AND tenant_id = public.get_current_tenant_id())
  WITH CHECK (public.is_staff_or_admin() AND tenant_id = public.get_current_tenant_id());

DROP POLICY IF EXISTS "mod_sub_public_insert" ON public.module_submissions;
CREATE POLICY "mod_sub_public_insert" ON public.module_submissions
  FOR INSERT
  WITH CHECK (TRUE);

-- ============================================================================
-- 8. Support Tickets & Telegram Messages Policies
-- ============================================================================
DROP POLICY IF EXISTS "support_tickets_admin_all" ON public.support_tickets;
CREATE POLICY "support_tickets_admin_all" ON public.support_tickets
  FOR ALL
  USING (public.is_staff_or_admin() AND tenant_id = public.get_current_tenant_id())
  WITH CHECK (public.is_staff_or_admin() AND tenant_id = public.get_current_tenant_id());

DROP POLICY IF EXISTS "support_tickets_public_insert" ON public.support_tickets;
CREATE POLICY "support_tickets_public_insert" ON public.support_tickets
  FOR INSERT
  WITH CHECK (TRUE);

DROP POLICY IF EXISTS "support_tickets_self_read" ON public.support_tickets;
CREATE POLICY "support_tickets_self_read" ON public.support_tickets
  FOR SELECT
  USING (email = (SELECT email FROM auth.users WHERE id = auth.uid()));

DROP POLICY IF EXISTS "support_messages_admin_all" ON public.support_messages;
CREATE POLICY "support_messages_admin_all" ON public.support_messages
  FOR ALL
  USING (public.is_staff_or_admin() AND tenant_id = public.get_current_tenant_id())
  WITH CHECK (public.is_staff_or_admin() AND tenant_id = public.get_current_tenant_id());

DROP POLICY IF EXISTS "support_messages_public_insert" ON public.support_messages;
CREATE POLICY "support_messages_public_insert" ON public.support_messages
  FOR INSERT
  WITH CHECK (TRUE);

-- ============================================================================
-- 9. System Settings & Audit Logs Policies
-- ============================================================================
DROP POLICY IF EXISTS "system_settings_read" ON public.system_settings;
CREATE POLICY "system_settings_read" ON public.system_settings
  FOR SELECT
  USING (TRUE);

DROP POLICY IF EXISTS "system_settings_admin_write" ON public.system_settings;
CREATE POLICY "system_settings_admin_write" ON public.system_settings
  FOR ALL
  USING (public.is_admin() AND tenant_id = public.get_current_tenant_id())
  WITH CHECK (public.is_admin() AND tenant_id = public.get_current_tenant_id());

DROP POLICY IF EXISTS "system_audit_admin_read" ON audit.system_audit_logs;
CREATE POLICY "system_audit_admin_read" ON audit.system_audit_logs
  FOR SELECT
  USING (public.is_admin() AND tenant_id = public.get_current_tenant_id());
