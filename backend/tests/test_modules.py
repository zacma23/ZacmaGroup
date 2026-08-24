import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_hrm_employees_crud():
    # List
    res = client.get("/api/v1/hrm/employees")
    assert res.status_code == 200
    assert isinstance(res.json(), list)

    # Create
    new_emp = {
        "full_name": "Test Employee",
        "email": "testemp@zacma.com",
        "department": "engineering",
        "role": "developer",
        "status": "active"
    }
    create_res = client.post("/api/v1/hrm/employees", json=new_emp)
    assert create_res.status_code == 201
    emp_id = create_res.json()["id"]

    # Get
    get_res = client.get(f"/api/v1/hrm/employees/{emp_id}")
    assert get_res.status_code == 200
    assert get_res.json()["full_name"] == "Test Employee"

    # Update
    update_res = client.put(f"/api/v1/hrm/employees/{emp_id}", json={"department": "operations"})
    assert update_res.status_code == 200
    assert update_res.json()["department"] == "operations"

    # Delete
    del_res = client.delete(f"/api/v1/hrm/employees/{emp_id}")
    assert del_res.status_code == 204

def test_visa_applications_crud():
    # List
    res = client.get("/api/v1/visa/applications")
    assert res.status_code == 200

    # Create
    new_app = {
        "applicant_name": "Test Visa Applicant",
        "passport_number": "P123456",
        "nationality": "Canadian",
        "visa_type": "tourist",
        "destination_country": "Japan",
        "status": "draft"
    }
    create_res = client.post("/api/v1/visa/applications", json=new_app)
    assert create_res.status_code == 201
    app_id = create_res.json()["id"]

    # Get & Update
    assert client.get(f"/api/v1/visa/applications/{app_id}").status_code == 200
    upd_res = client.put(f"/api/v1/visa/applications/{app_id}", json={"status": "submitted"})
    assert upd_res.status_code == 200
    assert upd_res.json()["status"] == "submitted"

    # Delete
    assert client.delete(f"/api/v1/visa/applications/{app_id}").status_code == 204

def test_payments_invoices_crud():
    # List
    res = client.get("/api/v1/payments/invoices")
    assert res.status_code == 200

    # Create
    new_inv = {
        "customer_name": "Test Invoice Client",
        "amount": 2500.0,
        "currency": "USD",
        "description": "Consulting Services",
        "status": "sent"
    }
    create_res = client.post("/api/v1/payments/invoices", json=new_inv)
    assert create_res.status_code == 201
    inv_id = create_res.json()["id"]

    # Get & Update
    assert client.get(f"/api/v1/payments/invoices/{inv_id}").status_code == 200
    upd = client.put(f"/api/v1/payments/invoices/{inv_id}", json={"status": "paid"})
    assert upd.status_code == 200
    assert upd.json()["status"] == "paid"

    # Delete
    assert client.delete(f"/api/v1/payments/invoices/{inv_id}").status_code == 204

def test_training_courses_crud():
    # List
    res = client.get("/api/v1/training/courses")
    assert res.status_code == 200

    # Create
    new_course = {
        "title": "Cloud Architecture 101",
        "description": "AWS and GCP fundamentals",
        "instructor": "Jane Cloud",
        "capacity": 25,
        "status": "active"
    }
    create_res = client.post("/api/v1/training/courses", json=new_course)
    assert create_res.status_code == 201
    course_id = create_res.json()["id"]

    # Get & Update & Delete
    assert client.get(f"/api/v1/training/courses/{course_id}").status_code == 200
    assert client.put(f"/api/v1/training/courses/{course_id}", json={"capacity": 35}).status_code == 200
    assert client.delete(f"/api/v1/training/courses/{course_id}").status_code == 204

def test_travel_bookings_crud():
    # List
    res = client.get("/api/v1/travel/bookings")
    assert res.status_code == 200

    # Create
    new_booking = {
        "traveler_name": "Test Traveler",
        "destination": "London",
        "booking_type": "flight",
        "status": "pending"
    }
    create_res = client.post("/api/v1/travel/bookings", json=new_booking)
    assert create_res.status_code == 201
    bk_id = create_res.json()["id"]

    # Get & Update & Delete
    assert client.get(f"/api/v1/travel/bookings/{bk_id}").status_code == 200
    assert client.put(f"/api/v1/travel/bookings/{bk_id}", json={"status": "confirmed"}).status_code == 200
    assert client.delete(f"/api/v1/travel/bookings/{bk_id}").status_code == 204

def test_marketing_campaigns_crud():
    # List
    res = client.get("/api/v1/marketing/campaigns")
    assert res.status_code == 200

    # Create
    new_camp = {
        "name": "Summer Launch Campaign",
        "channel": "email",
        "budget": 5000.0,
        "status": "draft"
    }
    create_res = client.post("/api/v1/marketing/campaigns", json=new_camp)
    assert create_res.status_code == 201
    camp_id = create_res.json()["id"]

    # Get & Update & Delete
    assert client.get(f"/api/v1/marketing/campaigns/{camp_id}").status_code == 200
    assert client.put(f"/api/v1/marketing/campaigns/{camp_id}", json={"status": "active"}).status_code == 200
    assert client.delete(f"/api/v1/marketing/campaigns/{camp_id}").status_code == 204

def test_dashboard_overview():
    res = client.get("/api/v1/dashboard/overview")
    assert res.status_code == 200
    data = res.json()
    assert "metrics" in data
    assert "modules" in data
    assert "services" in data
