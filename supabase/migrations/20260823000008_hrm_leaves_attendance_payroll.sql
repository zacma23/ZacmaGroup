-- ===========================================================================
-- MIGRATION 000008: HRM ADVANCED MODULE (Leaves, Attendance, Payroll)
-- ===========================================================================

-- 1. Employee Leaves Table
CREATE TABLE IF NOT EXISTS employee_leaves (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id TEXT NOT NULL,
    employee_id TEXT NOT NULL,
    employee_name TEXT,
    leave_type TEXT NOT NULL DEFAULT 'Annual',
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    reason TEXT,
    status TEXT NOT NULL DEFAULT 'pending', -- pending, approved, rejected
    admin_comment TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 2. Employee Attendance Table
CREATE TABLE IF NOT EXISTS employee_attendance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id TEXT NOT NULL,
    employee_id TEXT NOT NULL,
    employee_name TEXT,
    date DATE NOT NULL,
    status TEXT NOT NULL DEFAULT 'Present', -- Present, Absent, Late, HalfDay
    check_in TEXT,
    check_out TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 3. Employee Payroll Table
CREATE TABLE IF NOT EXISTS employee_payroll (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id TEXT NOT NULL,
    employee_id TEXT NOT NULL,
    employee_name TEXT NOT NULL,
    month TEXT NOT NULL, -- YYYY-MM
    gross_salary NUMERIC(12, 2) NOT NULL,
    tax_deduction NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    pension_deduction NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    net_salary NUMERIC(12, 2) NOT NULL,
    currency TEXT NOT NULL DEFAULT 'ETB',
    status TEXT NOT NULL DEFAULT 'paid',
    disbursed_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for fast tenant lookup
CREATE INDEX IF NOT EXISTS idx_employee_leaves_tenant ON employee_leaves(tenant_id);
CREATE INDEX IF NOT EXISTS idx_employee_attendance_tenant ON employee_attendance(tenant_id);
CREATE INDEX IF NOT EXISTS idx_employee_payroll_tenant ON employee_payroll(tenant_id);

-- Enable Row-Level Security (RLS)
ALTER TABLE employee_leaves ENABLE ROW LEVEL SECURITY;
ALTER TABLE employee_attendance ENABLE ROW LEVEL SECURITY;
ALTER TABLE employee_payroll ENABLE ROW LEVEL SECURITY;

-- Tenant Isolation Policies
CREATE POLICY "tenant_isolation_employee_leaves" ON employee_leaves
    USING (tenant_id = current_setting('app.current_tenant', true) OR tenant_id = 'zacma-demo');

CREATE POLICY "tenant_isolation_employee_attendance" ON employee_attendance
    USING (tenant_id = current_setting('app.current_tenant', true) OR tenant_id = 'zacma-demo');

CREATE POLICY "tenant_isolation_employee_payroll" ON employee_payroll
    USING (tenant_id = current_setting('app.current_tenant', true) OR tenant_id = 'zacma-demo');
