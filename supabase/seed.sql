-- ============================================================================
-- ZACMA TECHNOLOGY GROUP — SUPABASE INITIAL SEED DATA
-- Idempotent initial seed data for course catalog, categories, and settings.
-- ============================================================================

DO $$
DECLARE
  v_tid UUID := '00000000-0000-0000-0000-000000000001';
BEGIN
  -- 1. Tenants
  INSERT INTO public.tenants (id, name, slug, plan, status)
  VALUES (v_tid, 'Zacma Default Tenant', 'zacma-demo', 'enterprise', 'active')
  ON CONFLICT (slug) DO NOTHING;

  -- 2. System Settings
  INSERT INTO public.system_settings (tenant_id, default_receiving_account, default_payment_methods, courses_list, visa_types_list, education_levels_list)
  VALUES (
    v_tid,
    '1000140145797',
    ARRAY['TeleBirr', 'CBE', 'Awash', 'Abyssinia', 'Chapa']::TEXT[],
    ARRAY['Graphics Design', 'Video Editing', 'Web Design', 'Programming', 'AI', 'Accounting', 'Maintenance']::TEXT[],
    ARRAY['Tourist', 'Work', 'Study', 'Business']::TEXT[],
    ARRAY['High School', 'Diploma', 'Bachelor''s Degree', 'Master''s Degree', 'Other']::TEXT[]
  )
  ON CONFLICT (tenant_id) DO NOTHING;

  -- 3. Course Categories
  INSERT INTO public.course_categories (id, tenant_id, code, name, description, display_order)
  VALUES
    ('c0000000-0000-0000-0000-000000000001', v_tid, 'IT_PROG', 'Software & IT Engineering', 'Programming, Web & AI tracks', 1),
    ('c0000000-0000-0000-0000-000000000002', v_tid, 'CREATIVE', 'Creative & Digital Media', 'Graphics, motion and video editing', 2),
    ('c0000000-0000-0000-0000-000000000003', v_tid, 'HARDWARE', 'Hardware & Electronics', 'Mobile & computer hardware maintenance', 3),
    ('c0000000-0000-0000-0000-000000000004', v_tid, 'BUSINESS', 'Business & Accounting', 'Finance, accounting and commerce software', 4)
  ON CONFLICT (tenant_id, code) DO NOTHING;

  -- 4. Initial Courses
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

  -- 5. Notification Templates
  INSERT INTO public.notification_templates (tenant_id, template_key, subject, body_template, description)
  VALUES
    (
      v_tid,
      'invoice_created',
      'Invoice Issued — {reference_code} for {description}',
      'Dear {customer_name},\n\nYour invoice for {description} in the amount of {amount} {currency} has been generated.\n\nOfficial Receiving Account (CBE): 1000140145797\n\nBest regards,\nZacma Operations Team',
      'Notification sent upon invoice generation.'
    ),
    (
      v_tid,
      'payment_confirmed',
      'Payment Confirmed — Invoice {reference_code}',
      'Dear {customer_name},\n\nWe have confirmed your payment of {amount} {currency} for {description}.\n\nYour application is now under processing.\n\nBest regards,\nZacma Operations',
      'Notification sent upon payment verification.'
    ),
    (
      v_tid,
      'registration_approved',
      'Application Approved — Zacma Technology Group',
      'Dear {full_name},\n\nYour application ({item_title}) has been APPROVED.\n\nThank you for choosing Zacma!',
      'Notification sent upon final approval.'
    )
  ON CONFLICT (tenant_id, template_key) DO NOTHING;

  -- 6. Root Administrator Account Profile Seed
  -- Idempotent administrator profile setup with role 'admin'
  INSERT INTO public.profiles (id, tenant_id, email, full_name, role, status, metadata)
  VALUES (
    '00000000-0000-0000-0000-000000000002',
    v_tid,
    'zacma@admin',
    'Zacma Administrator',
    'admin',
    'active',
    '{"is_root_admin": true}'::jsonb
  )
  ON CONFLICT (id) DO UPDATE SET
    role = 'admin',
    status = 'active',
    updated_at = now();
END $$;
