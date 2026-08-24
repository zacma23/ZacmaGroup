"""Automated tests for HRM module: Employees, Leaves, Attendance, and Payroll."""

import pytest
from fastapi.testclient import TestClient

from app.core.auth import create_access_token
from app.core.config import settings
from app.main import app

client = TestClient(app)


@pytest.fixture
def admin_token() -> str:
    return create_access_token({
        "sub": "admin-user",
        "email": "admin@zacma.com",
        "role": "admin",
        "tenant_id": settings.demo_tenant_id,
        "full_name": "Zacma Admin",
    })


def test_hrm_employee_crud():
    """Verify employee creation, retrieval, and updating."""
    # 1. Create employee
    new_emp = {
        "full_name": "Dawit Bekele",
        "email": "dawit.bekele@zacma.com",
        "department": "Engineering",
        "role": "Senior Full-Stack Engineer",
        "status": "active",
    }
    create_res = client.post("/api/v1/hrm/employees", json=new_emp)
    assert create_res.status_code == 201
    emp_data = create_res.json()
    assert emp_data["full_name"] == "Dawit Bekele"
    emp_id = emp_data["id"]

    # 2. Get employee
    get_res = client.get(f"/api/v1/hrm/employees/{emp_id}")
    assert get_res.status_code == 200
    assert get_res.json()["department"] == "Engineering"


def test_hrm_leave_management(admin_token):
    """Verify leave request submission, listing, and admin review."""
    # 1. Get an existing active employee
    emp_list = client.get("/api/v1/hrm/employees").json()
    assert len(emp_list) > 0
    emp_id = emp_list[0]["id"]

    # 2. Submit leave request
    leave_payload = {
        "employee_id": emp_id,
        "leave_type": "Annual",
        "start_date": "2026-10-01",
        "end_date": "2026-10-05",
        "reason": "Personal time off",
    }
    sub_res = client.post("/api/v1/hrm/leaves", json=leave_payload)
    assert sub_res.status_code == 201
    leave_data = sub_res.json()
    assert leave_data["status"] == "pending"
    leave_id = leave_data["id"]

    # 3. Admin review/approve
    headers = {"Authorization": f"Bearer {admin_token}"}
    review_res = client.put(
        f"/api/v1/hrm/leaves/{leave_id}",
        json={"status": "approved", "admin_comment": "Approved by Director"},
        headers=headers,
    )
    assert review_res.status_code == 200
    assert review_res.json()["status"] == "approved"


def test_hrm_attendance_and_payroll_run(admin_token):
    """Verify attendance logging and monthly payroll disbursement run."""
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Get an existing active employee
    emp_list = client.get("/api/v1/hrm/employees").json()
    assert len(emp_list) > 0
    emp = emp_list[0]
    emp_id = emp["id"]

    # 2. Log attendance
    att_payload = {
        "employee_id": emp_id,
        "date": "2026-08-24",
        "status": "Present",
        "check_in": "08:25",
        "check_out": "17:35",
        "notes": "Completed sprint review",
    }
    att_res = client.post("/api/v1/hrm/attendance", json=att_payload)
    assert att_res.status_code == 201
    assert att_res.json()["status"] == "Present"

    # 3. Run monthly payroll
    payroll_payload = {
        "month": "2026-08",
        "base_salaries_override": {emp_id: 50000.0},
    }
    pay_res = client.post("/api/v1/hrm/payroll/run", json=payroll_payload, headers=headers)
    assert pay_res.status_code == 201
    records = pay_res.json()
    assert len(records) >= 1
    emp_rec = next((r for r in records if r["employee_id"] == emp_id), None)
    assert emp_rec is not None
    assert emp_rec["gross_salary"] == 50000.0
    assert emp_rec["net_salary"] == round(50000.0 - (50000.0 * 0.15) - (50000.0 * 0.07), 2)
