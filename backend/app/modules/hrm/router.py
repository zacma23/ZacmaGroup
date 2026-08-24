"""HRM module — Employee management, Leave requests, Attendance & Payroll endpoints."""

from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.db import supabase
from app.core.demo_data import (
    attendance_store,
    employees_store,
    leaves_store,
    payroll_store,
)
from app.core.permissions import require_role
from app.core.tenancy import get_tenant_id
from app.models import (
    AttendanceRecordCreate,
    AttendanceRecordResponse,
    EmployeeCreate,
    EmployeeResponse,
    EmployeeUpdate,
    LeaveRequestCreate,
    LeaveRequestResponse,
    LeaveRequestUpdate,
    PayrollRecordResponse,
    PayrollRunCreate,
)

router = APIRouter(prefix="/hrm", tags=["hrm"])


# ── List all employees ─────────────────────────────────────────────────────

@router.get("/employees", response_model=list[EmployeeResponse])
def list_employees(tenant_id: str = Depends(get_tenant_id)):
    """Return all employees for the current tenant."""
    if supabase is None:
        return employees_store.list_all(tenant_id)

    result = supabase.table("employees").select("*").eq("tenant_id", tenant_id).execute()
    return result.data


# ── Create an employee ─────────────────────────────────────────────────────

@router.post("/employees", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
def create_employee(payload: EmployeeCreate, tenant_id: str = Depends(get_tenant_id)):
    """Create a new employee record for the current tenant."""
    data = payload.model_dump()

    if supabase is None:
        return employees_store.create(data, tenant_id)

    data["tenant_id"] = tenant_id
    result = supabase.table("employees").insert(data).execute()
    return result.data[0] if result.data else data


# ── Get a single employee ──────────────────────────────────────────────────

@router.get("/employees/{employee_id}", response_model=EmployeeResponse)
def get_employee(employee_id: str, tenant_id: str = Depends(get_tenant_id)):
    """Retrieve a single employee by ID."""
    if supabase is None:
        record = employees_store.get(employee_id, tenant_id)
        if record is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found.")
        return record

    result = (
        supabase.table("employees")
        .select("*")
        .eq("id", employee_id)
        .eq("tenant_id", tenant_id)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found.")
    return result.data[0]


# ── Update an employee ─────────────────────────────────────────────────────

@router.put("/employees/{employee_id}", response_model=EmployeeResponse)
def update_employee(employee_id: str, payload: EmployeeUpdate, tenant_id: str = Depends(get_tenant_id)):
    """Update an existing employee record."""
    updates = payload.model_dump(exclude_unset=True)

    if supabase is None:
        record = employees_store.update(employee_id, updates, tenant_id)
        if record is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found.")
        return record

    result = (
        supabase.table("employees")
        .update(updates)
        .eq("id", employee_id)
        .eq("tenant_id", tenant_id)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found.")
    return result.data[0]


# ── Delete an employee ─────────────────────────────────────────────────────

@router.delete("/employees/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee(employee_id: str, tenant_id: str = Depends(get_tenant_id)):
    """Delete an employee record by ID."""
    if supabase is None:
        deleted = employees_store.delete(employee_id, tenant_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found.")
        return

    result = (
        supabase.table("employees")
        .delete()
        .eq("id", employee_id)
        .eq("tenant_id", tenant_id)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found.")


# ---------------------------------------------------------------------------
# Leave Management
# ---------------------------------------------------------------------------

@router.get("/leaves", response_model=list[LeaveRequestResponse])
def list_leaves(tenant_id: str = Depends(get_tenant_id)):
    """List all employee leave requests."""
    return leaves_store.list_all(tenant_id)


@router.post("/leaves", response_model=LeaveRequestResponse, status_code=status.HTTP_201_CREATED)
def submit_leave_request(payload: LeaveRequestCreate, tenant_id: str = Depends(get_tenant_id)):
    """Submit a new employee leave request."""
    emp = employees_store.get(payload.employee_id, tenant_id)
    emp_name = emp.get("full_name") if emp else "Employee"
    data = payload.model_dump()
    data["employee_name"] = emp_name
    data["status"] = "pending"
    return leaves_store.create(data, tenant_id)


@router.put("/leaves/{leave_id}", response_model=LeaveRequestResponse)
def review_leave_request(
    leave_id: str,
    payload: LeaveRequestUpdate,
    tenant_id: str = Depends(get_tenant_id),
    user: dict = Depends(require_role(["admin", "superadmin", "hrm", "manager"])),
):
    """Review, approve or reject an employee leave request."""
    updated = leaves_store.update(leave_id, payload.model_dump(exclude_unset=True), tenant_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Leave request not found")
    return updated


# ---------------------------------------------------------------------------
# Attendance Tracking
# ---------------------------------------------------------------------------

@router.get("/attendance", response_model=list[AttendanceRecordResponse])
def list_attendance(tenant_id: str = Depends(get_tenant_id)):
    """List employee attendance logs."""
    return attendance_store.list_all(tenant_id)


@router.post("/attendance", response_model=AttendanceRecordResponse, status_code=status.HTTP_201_CREATED)
def log_attendance(payload: AttendanceRecordCreate, tenant_id: str = Depends(get_tenant_id)):
    """Record employee attendance log."""
    emp = employees_store.get(payload.employee_id, tenant_id)
    emp_name = emp.get("full_name") if emp else "Employee"
    data = payload.model_dump()
    data["employee_name"] = emp_name
    return attendance_store.create(data, tenant_id)


# ---------------------------------------------------------------------------
# Payroll Processing
# ---------------------------------------------------------------------------

@router.get("/payroll", response_model=list[PayrollRecordResponse])
def list_payroll(
    month: Optional[str] = None,
    tenant_id: str = Depends(get_tenant_id),
    user: dict = Depends(require_role(["admin", "superadmin", "finance", "hrm"])),
):
    """List payroll records with optional month filter."""
    records = payroll_store.list_all(tenant_id)
    if month:
        records = [r for r in records if r.get("month") == month]
    return records


@router.post("/payroll/run", response_model=list[PayrollRecordResponse], status_code=status.HTTP_201_CREATED)
def run_monthly_payroll(
    payload: PayrollRunCreate,
    tenant_id: str = Depends(get_tenant_id),
    user: dict = Depends(require_role(["admin", "superadmin", "finance"])),
):
    """Process automated payroll run for all active employees for given month."""
    employees = [e for e in employees_store.list_all(tenant_id) if e.get("status") == "active"]
    results = []
    overrides = payload.base_salaries_override or {}

    for emp in employees:
        base_salary = overrides.get(emp["id"], 35000.0)
        tax = round(base_salary * 0.15, 2)
        pension = round(base_salary * 0.07, 2)
        net = round(base_salary - tax - pension, 2)

        rec_data = {
            "tenant_id": tenant_id,
            "employee_id": emp["id"],
            "employee_name": emp["full_name"],
            "month": payload.month,
            "gross_salary": base_salary,
            "tax_deduction": tax,
            "pension_deduction": pension,
            "net_salary": net,
            "currency": "ETB",
            "status": "paid",
            "disbursed_at": datetime.now(timezone.utc).isoformat(),
        }
        created = payroll_store.create(rec_data, tenant_id)
        results.append(created)

    return results
