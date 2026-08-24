"""Automated Test Suite for Software Development, Our Platforms, and Zacma Business-Aware AI."""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.ai_assistant_service import AiAssistantService
from app.services.ai_service_generator import AiServiceGenerator

client = TestClient(app)


def test_software_capabilities_endpoint():
    """Verify GET /api/v1/software/capabilities returns complete catalog."""
    res = client.get("/api/v1/software/capabilities")
    assert res.status_code == 200
    data = res.json()
    assert "categories" in data
    assert len(data["categories"]) >= 6
    assert "tech_stacks" in data
    assert "supported_platforms" in data
    assert any("erp" in c["id"].lower() for c in data["categories"])
    assert any("school" in c["id"].lower() for c in data["categories"])


def test_software_project_submission_and_invoicing():
    """Verify client submitting software project auto-generates reference code and invoice."""
    payload = {
        "project_name": "Automated Clinic EHR & Patient Mobile App",
        "client_name": "Addis Health Services",
        "email": "contact@addishealth.com",
        "phone": "+251911998877",
        "industry": "Healthcare & Telemedicine",
        "platforms": ["Android", "iOS", "Web", "Cloud"],
        "project_description": "Electronic health record system with patient portal and TeleBirr checkout for appointment bookings.",
        "required_features": ["Patient Portal", "Telemedicine Video", "TeleBirr Integration"],
        "budget": 75000.0,
        "advance_payment_method": "CBE",
        "advance_amount": 18750.0,
    }

    res = client.post("/api/v1/software/projects", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["reference_code"].startswith("ZAC-DEV-")
    assert data["project_name"] == payload["project_name"]
    assert data["status"] == "Pending"
    assert data["linked_crm_contact_id"] is not None
    assert data["linked_invoice_id"] is not None

    ref_code = data["reference_code"]

    # Verify retrieval by reference code
    res_get = client.get(f"/api/v1/software/projects/{ref_code}")
    assert res_get.status_code == 200
    assert res_get.json()["id"] == data["id"]


def test_ai_service_generator_software_architecture():
    """Verify AI Service Generator creates comprehensive software architecture blueprint."""
    request_data = {
        "project_name": "E-Commerce Supermarket & Delivery App",
        "client_name": "Shoppers Mart Ethiopia",
        "reference_code": "ZAC-DEV-9988",
        "platforms": ["Web", "Android", "iOS"],
        "industry": "Retail & Logistics",
    }

    output = AiServiceGenerator.generate_for_service("software", request_data)
    assert output["deliverable_type"] == "Software Architecture Specification & Project Roadmap"
    assert "ZACMA SOFTWARE ENGINEERING ARCHITECTURE SPECIFICATION" in output["architecture_specification"]
    assert len(output["sprint_roadmap"]) >= 5
    assert len(output["recommended_tech_stack"]) >= 4
    assert output["status"] == "ReadyForAdminReview"


def test_zacma_business_aware_ai_knowledge_retrieval():
    """Verify AI assistant answers real Zacma business questions with trusted data."""
    # 1. School Management / MySchool
    ans1 = AiAssistantService.consult_zacma_ai("I need a school management system for admissions and grading. What do you recommend?")
    assert "MySchool" in ans1["reply"]
    assert "https://myschool.zacmaa.net/" in ans1["reply"]
    assert ans1["recommendation"] is not None
    assert "myschool.zacmaa.net" in ans1["recommendation"]["url"]

    # 2. ERP System
    ans2 = AiAssistantService.consult_zacma_ai("Can Zacma build an ERP system for multi-branch warehouse inventory?")
    assert "Zacma ERP" in ans2["reply"]
    assert "https://erp.zacmaa.net/" in ans2["reply"]

    # 3. E-Commerce
    ans3 = AiAssistantService.consult_zacma_ai("I want an e-commerce store with TeleBirr integration.")
    assert "E-Commerce" in ans3["reply"]
    assert "https://ecommerce.zacmaa.net/" in ans3["reply"]

    # 4. Freelancer
    ans4 = AiAssistantService.consult_zacma_ai("What is the Freelancer platform?")
    assert "Freelancer" in ans4["reply"]
    assert "https://freelancer.zacmaa.net/" in ans4["reply"]

    # 5. Platforms overview
    ans5 = AiAssistantService.consult_zacma_ai("What platforms does Zacma Group have?")
    assert "erp.zacmaa.net" in ans5["reply"]
    assert "myschool.zacmaa.net" in ans5["reply"]
    assert "ecommerce.zacmaa.net" in ans5["reply"]
    assert "freelancer.zacmaa.net" in ans5["reply"]

    # 6. Payment & Official Receiving Account
    ans6 = AiAssistantService.consult_zacma_ai("How do I upload my payment receipt and what are the payment methods?")
    assert "Chapa" in ans6["reply"] or "CBE" in ans6["reply"]
    assert "/portal" in ans6["reply"]


def test_support_chatbot_endpoint_routes_to_ai_knowledge():
    """Verify POST /api/v1/support/chat responds using the business-aware AI engine."""
    payload = {"message": "What software development services do you offer?"}
    res = client.post("/api/v1/support/chat", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "Software" in data["reply"] or "software" in data["reply"].lower()
    assert len(data["suggested_actions"]) > 0
    assert any("/software" in a["url"] for a in data["suggested_actions"])
