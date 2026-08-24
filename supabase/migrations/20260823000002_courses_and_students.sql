-- ============================================================================
-- Migration: 20260823000002_courses_and_students.sql
-- Description: Course categories, flexible dynamic courses, student directory,
--              registrations lifecycle, attendance tracking, and initial course seed data.
-- ============================================================================

-- ============================================================================
-- Table: public.course_categories
-- Allows administrators to add/edit categories dynamically
-- ============================================================================
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

CREATE INDEX IF NOT EXISTS idx_course_categories_tenant ON public.course_categories(tenant_id);

DROP TRIGGER IF EXISTS trg_course_categories_updated_at ON public.course_categories;
CREATE TRIGGER trg_course_categories_updated_at
  BEFORE UPDATE ON public.course_categories
  FOR EACH ROW
  EXECUTE FUNCTION public.set_current_timestamp_updated_at();

-- ============================================================================
-- Table: public.courses
-- Flexible course catalog manageable by admins without altering DB schema
-- ============================================================================
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

CREATE INDEX IF NOT EXISTS idx_courses_tenant ON public.courses(tenant_id);
CREATE INDEX IF NOT EXISTS idx_courses_category ON public.courses(category_id);
CREATE INDEX IF NOT EXISTS idx_courses_is_active ON public.courses(is_active);

DROP TRIGGER IF EXISTS trg_courses_updated_at ON public.courses;
CREATE TRIGGER trg_courses_updated_at
  BEFORE UPDATE ON public.courses
  FOR EACH ROW
  EXECUTE FUNCTION public.set_current_timestamp_updated_at();

-- ============================================================================
-- Table: public.students
-- Master student directory with email uniqueness per tenant to prevent duplicates
-- ============================================================================
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

CREATE INDEX IF NOT EXISTS idx_students_tenant_id ON public.students(tenant_id);
CREATE INDEX IF NOT EXISTS idx_students_user_id ON public.students(user_id);
CREATE INDEX IF NOT EXISTS idx_students_email ON public.students(email);
CREATE INDEX IF NOT EXISTS idx_students_phone ON public.students(phone);

DROP TRIGGER IF EXISTS trg_students_updated_at ON public.students;
CREATE TRIGGER trg_students_updated_at
  BEFORE UPDATE ON public.students
  FOR EACH ROW
  EXECUTE FUNCTION public.set_current_timestamp_updated_at();

-- ============================================================================
-- Table: public.student_registrations
-- Student enrollment records with workflow and payment tracking
-- ============================================================================
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

CREATE INDEX IF NOT EXISTS idx_student_reg_tenant ON public.student_registrations(tenant_id);
CREATE INDEX IF NOT EXISTS idx_student_reg_student ON public.student_registrations(student_id);
CREATE INDEX IF NOT EXISTS idx_student_reg_course ON public.student_registrations(course_id);
CREATE INDEX IF NOT EXISTS idx_student_reg_ref_code ON public.student_registrations(reference_code);
CREATE INDEX IF NOT EXISTS idx_student_reg_status ON public.student_registrations(application_status);

DROP TRIGGER IF EXISTS trg_student_registrations_updated_at ON public.student_registrations;
CREATE TRIGGER trg_student_registrations_updated_at
  BEFORE UPDATE ON public.student_registrations
  FOR EACH ROW
  EXECUTE FUNCTION public.set_current_timestamp_updated_at();

-- ============================================================================
-- Table: public.student_attendance
-- Attendance tracking per registration
-- ============================================================================
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

CREATE INDEX IF NOT EXISTS idx_attendance_reg ON public.student_attendance(registration_id);
CREATE INDEX IF NOT EXISTS idx_attendance_date ON public.student_attendance(session_date);

-- ============================================================================
-- Seed Data: Course Categories & Standard Practical Courses
-- Safe and idempotent (ON CONFLICT DO NOTHING)
-- ============================================================================
DO $$
DECLARE
  v_tid UUID := '00000000-0000-0000-0000-000000000001';
  v_cat_it UUID;
  v_cat_media UUID;
  v_cat_maint UUID;
  v_cat_biz UUID;
BEGIN
  -- 1. Categories
  INSERT INTO public.course_categories (id, tenant_id, code, name, description, display_order)
  VALUES
    ('c0000000-0000-0000-0000-000000000001', v_tid, 'IT_PROG', 'Software & IT Engineering', 'Programming, Web & AI tracks', 1),
    ('c0000000-0000-0000-0000-000000000002', v_tid, 'CREATIVE', 'Creative & Digital Media', 'Graphics, motion and video editing', 2),
    ('c0000000-0000-0000-0000-000000000003', v_tid, 'HARDWARE', 'Hardware & Electronics', 'Mobile & computer hardware maintenance', 3),
    ('c0000000-0000-0000-0000-000000000004', v_tid, 'BUSINESS', 'Business & Accounting', 'Finance, accounting and commerce software', 4)
  ON CONFLICT (tenant_id, code) DO NOTHING;

  -- 2. Courses
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
