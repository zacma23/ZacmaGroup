import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.auth import create_access_token
from app.core.config import settings

client = TestClient(app)

@pytest.fixture
def admin_token():
    return create_access_token({
        "sub": "admin-id",
        "email": "admin@zacma.com",
        "role": "admin",
        "tenant_id": settings.demo_tenant_id,
        "full_name": "Zacma Admin"
    })

def test_student_registration_full_flow(admin_token):
    # 1. Submit Registration
    reg_payload = {
        "full_name": "Kidus Hailu",
        "address": "Bole, Addis Ababa",
        "phone": "+251911998877",
        "email": "kidus.h@test.com",
        "education_level": "Bachelor's Degree",
        "course": "Programming",
        "payment_method": "TeleBirr",
        "interests": "Python, APIs, Cloud Backend"
    }
    create_res = client.post("/api/v1/students/registrations", json=reg_payload)
    assert create_res.status_code == 201
    reg = create_res.json()
    reg_id = reg["id"]

    # Verify AI recommendation generated
    assert "Recommended Course" in reg["ai_course_recommendation"]

    # Verify CRM Contact auto-synced
    assert reg["linked_crm_contact_id"] is not None

    # Verify Invoice auto-generated
    assert reg["linked_invoice_id"] is not None

    # 2. Check Linked Invoice generated with payment method
    inv_id = reg["linked_invoice_id"]
    inv_res = client.get(f"/api/v1/payments/invoices/{inv_id}")
    assert inv_res.status_code == 200
    inv = inv_res.json()
    assert inv["receiving_account"] is not None
    assert inv["payment_method"] == "TeleBirr"

    # 3. Mark Attendance
    att_res = client.post(
        f"/api/v1/students/registrations/{reg_id}/attendance",
        json={"session_date": "2026-08-23", "session_title": "Python Syntax", "present": True, "notes": "Great participation"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert att_res.status_code == 200
    assert len(att_res.json()["attendance"]) == 1

    # 4. Admin Approve
    app_res = client.post(
        f"/api/v1/students/registrations/{reg_id}/approve",
        json={"comment": "Tuition verified"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert app_res.status_code == 200
    assert app_res.json()["status"] == "success"

    # Verify status changed to Approved
    get_res = client.get(f"/api/v1/students/registrations/{reg_id}")
    assert get_res.json()["status"] == "Approved"


def test_training_course_structure_endpoint():
    """Verify 15 courses and Maintenance -> Hardware Specialty hierarchy."""
    res = client.get("/api/v1/training/structure")
    assert res.status_code == 200
    courses = res.json()
    assert len(courses) == 15

    # Find Maintenance course
    maint = next((c for c in courses if c["id"] == "maintenance"), None)
    assert maint is not None
    assert maint["name"] == "Maintenance"
    assert len(maint["specialties"]) == 1

    hardware = maint["specialties"][0]
    assert hardware["id"] == "hardware_specialty"
    assert hardware["name"] == "Hardware Specialty"

    # Verify 3 Schedules
    schedule_labels = [s["label"] for s in hardware["schedules"]]
    assert "Monday + Wednesday + Thursday" in schedule_labels
    assert "Tuesday + Thursday + Saturday" in schedule_labels
    assert "Saturday + Sunday" in schedule_labels

    # Verify 6 Time Slots
    assert "03:00 – 05:00" in hardware["time_slots"]
    assert "05:00 – 07:00" in hardware["time_slots"]
    assert "07:00 – 09:00" in hardware["time_slots"]
    assert "09:00 – 11:00" in hardware["time_slots"]
    assert "11:00 – 01:00" in hardware["time_slots"]
    assert "12:00 – 02:00" in hardware["time_slots"]


def test_maintenance_hardware_specialty_registration_flow(admin_token):
    """Test full registration for Maintenance -> Hardware Specialty."""
    payload = {
        "full_name": "Tadesse Woldemariam",
        "address": "Kazanchis, Addis Ababa",
        "phone": "+251944556677",
        "email": "tadesse.w@test.com",
        "education_level": "Diploma / TVET",
        "course": "Maintenance",
        "specialty": "Hardware Specialty",
        "schedule": "Monday + Wednesday + Thursday",
        "time_slot": "03:00 – 05:00",
        "payment_method": "CBE",
    }
    res = client.post("/api/v1/students/registrations", json=payload)
    assert res.status_code == 201
    student = res.json()

    assert student["course"] == "Maintenance"
    assert student["specialty"] == "Hardware Specialty"
    assert student["schedule"] == "Monday + Wednesday + Thursday"
    assert student["time_slot"] == "03:00 – 05:00"
    assert student["status"] == "Pending"

    # Admin updates schedule and time slot
    reg_id = student["id"]
    update_res = client.put(
        f"/api/v1/students/registrations/{reg_id}",
        json={
            "schedule": "Tuesday + Thursday + Saturday",
            "time_slot": "05:00 – 07:00",
            "status": "Approved",
        },
    )
    assert update_res.status_code == 200
    updated = update_res.json()
    assert updated["schedule"] == "Tuesday + Thursday + Saturday"
    assert updated["time_slot"] == "05:00 – 07:00"
    assert updated["status"] == "Approved"


def test_ai_maintenance_and_hardware_specialty_consultation():
    """Verify AI answers maintenance and hardware specialty queries accurately."""
    from app.services.ai_assistant_service import AiAssistantService

    # 1. Maintenance course query
    res1 = AiAssistantService.consult_zacma_ai("What maintenance courses do you offer?")
    assert "Maintenance" in res1["reply"]
    assert "Hardware Specialty" in res1["reply"]
    assert "Monday + Wednesday + Thursday" in res1["reply"]

    # 2. Hardware specialty schedule query
    res2 = AiAssistantService.consult_zacma_ai("What schedule is available for Hardware Specialty?")
    assert "03:00 – 05:00" in res2["reply"]
    assert "Saturday + Sunday" in res2["reply"]
    assert "Tuesday + Thursday + Saturday" in res2["reply"]

