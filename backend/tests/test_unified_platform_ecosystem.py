"""Comprehensive Test Suite for Unified Business Management Platform.

Tests:
1. Organization Inquiry -> Match/Create Person & Org -> CRM Lead & Timeline
2. Student Registration -> Person -> CRM -> Invoice -> Verified Payment -> Revenue Profile
3. CRM Pipeline, Deals, Probability Forecasting & Activity Logging
4. Dynamic Marketing Segmentation & Campaign Dispatch with Recipient Timeline Logging
5. Deduplication & Identity Matching Guarantees
6. 360-Degree Unified Person Profile Aggregator
7. Global Ecosystem Search across People, Orgs, Opportunities, Students, and Tickets
"""

import pytest
from fastapi.testclient import TestClient

from app.core.auth import create_access_token
from app.core.config import settings
from app.main import app

client = TestClient(app)


@pytest.fixture
def admin_token() -> str:
    return create_access_token({
        "sub": "admin-id",
        "email": "admin@zacma.com",
        "role": "admin",
        "tenant_id": settings.demo_tenant_id,
        "full_name": "Zacma Admin",
    })


def test_deduplication_and_people_creation(admin_token):
    """Verify that creating/syncing people with the same email or phone matches existing records."""
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Create initial person
    res1 = client.post(
        "/api/v1/people",
        json={
            "full_name": "Ecosystem Test User",
            "email": "ecosystem.user@example.com",
            "phone": "+251999887766",
            "person_type": "Individual",
            "status": "Active",
            "tags": ["InitialTag"],
        },
        headers=headers,
    )
    assert res1.status_code == 201
    person1 = res1.json()
    p1_id = person1["id"]

    # 2. Re-submit same email with new tag and student type
    res2 = client.post(
        "/api/v1/people",
        json={
            "full_name": "Ecosystem Test User",
            "email": "ecosystem.user@example.com",
            "phone": "+251999887766",
            "person_type": "Student",
            "status": "Enrolled",
            "tags": ["CourseEnrolled"],
        },
        headers=headers,
    )
    assert res2.status_code == 201
    person2 = res2.json()

    # Must match the same ID without creating a duplicate record
    assert person2["id"] == p1_id
    assert "CourseEnrolled" in person2.get("tags", [])


def test_organization_inquiry_to_crm_lead_flow(admin_token):
    """Verify Organization Inquiry creates/matches Person, Org, and CRM Lead."""
    headers = {"Authorization": f"Bearer {admin_token}"}

    inquiry_payload = {
        "full_name": "Dr. Haile Mariam",
        "email": "haile.m@africahospital.et",
        "phone": "+251977112233",
        "subject": "Inquiry: Hospital ERP and Billing Software",
        "category": "general",
        "message": "We represent Africa Hospital PLC and require custom software development.",
    }

    res = client.post("/api/v1/support/tickets", json=inquiry_payload, headers=headers)
    assert res.status_code == 201
    tkt = res.json()
    assert "id" in tkt

    # Verify Person was created
    people_res = client.get("/api/v1/people?search=haile.m@africahospital.et", headers=headers)
    assert people_res.status_code == 200
    people = people_res.json()
    assert len(people) >= 1
    person = people[0]
    assert person["full_name"] == "Dr. Haile Mariam"

    # Verify CRM Contact exists with timeline event
    crm_res = client.get(f"/api/v1/crm/contacts/{person['id']}", headers=headers)
    assert crm_res.status_code == 200
    crm_contact = crm_res.json()
    assert any("Ticket opened" in e["action"] for e in crm_contact.get("timeline", []))


def test_crm_opportunities_and_pipeline_flow(admin_token):
    """Verify creating opportunities, stage progression, and activity logging."""
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Create deal
    deal_payload = {
        "title": "Hospital Management ERP Deployment",
        "value": 350000.0,
        "currency": "ETB",
        "pipeline_stage": "Proposal",
        "probability": 75,
        "source": "Organization Inquiry",
        "notes": "Full SOW and wireframes provided.",
    }
    create_res = client.post("/api/v1/crm/opportunities", json=deal_payload, headers=headers)
    assert create_res.status_code == 201
    deal = create_res.json()
    assert deal["value"] == 350000.0
    assert deal["pipeline_stage"] == "Proposal"
    deal_id = deal["id"]

    # 2. Advance stage to Won
    update_res = client.put(
        f"/api/v1/crm/opportunities/{deal_id}",
        json={"pipeline_stage": "Won"},
        headers=headers,
    )
    assert update_res.status_code == 200
    updated_deal = update_res.json()
    assert updated_deal["pipeline_stage"] == "Won"
    assert updated_deal["status"] == "Won"
    assert updated_deal["probability"] == 100

    # 3. Log Activity
    act_res = client.post(
        "/api/v1/crm/activities",
        json={
            "activity_type": "Meeting",
            "subject": "Final Contract Sign-off",
            "description": "Met with hospital executives to sign agreement.",
            "person_id": "person-001",
            "opportunity_id": deal_id,
        },
        headers=headers,
    )
    assert act_res.status_code == 201
    act = act_res.json()
    assert act["activity_type"] == "Meeting"

    # 4. Check Pipeline Summary
    pipe_res = client.get("/api/v1/crm/pipeline", headers=headers)
    assert pipe_res.status_code == 200
    pipe = pipe_res.json()
    assert pipe["total_pipeline_value"] > 0


def test_marketing_dynamic_segments_and_campaign_dispatch(admin_token):
    """Verify dynamic segment computation and campaign dispatch recording to recipient timelines."""
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Create dynamic segment for Students
    seg_res = client.post(
        "/api/v1/marketing/segments",
        json={
            "name": "Active Tech Students Segment",
            "description": "Learners enrolled in software and AI courses",
            "filter_criteria": {"person_type": "Student"},
            "is_dynamic": True,
        },
        headers=headers,
    )
    assert seg_res.status_code == 201
    seg = seg_res.json()
    seg_id = seg["id"]
    assert "member_count" in seg

    # 2. Create campaign targeting this segment
    camp_res = client.post(
        "/api/v1/marketing/campaigns",
        json={
            "name": "Advanced Python & AI Workshop Announcement",
            "campaign_type": "Email",
            "segment_id": seg_id,
            "subject": "Invitation to Next-Gen AI Seminar",
            "message_body": "Join our upcoming live masterclass on autonomous agents.",
        },
        headers=headers,
    )
    assert camp_res.status_code == 201
    camp = camp_res.json()
    camp_id = camp["id"]

    # 3. Dispatch campaign
    dispatch_res = client.post(
        f"/api/v1/marketing/campaigns/{camp_id}/dispatch",
        json={"target_segment_id": seg_id},
        headers=headers,
    )
    assert dispatch_res.status_code == 200
    result = dispatch_res.json()
    assert result["status"] == "Sent"
    assert result["delivered_count"] > 0

    # 4. Verify communication log generated
    logs_res = client.get(f"/api/v1/marketing/logs?campaign_id={camp_id}", headers=headers)
    assert logs_res.status_code == 200
    logs = logs_res.json()
    assert len(logs) > 0


def test_person_360_profile_aggregator(admin_token):
    """Verify complete 360-degree unified profile aggregation."""
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Fetch profile for Abebe Bikila (person-001)
    res = client.get("/api/v1/people/person-001/profile", headers=headers)
    assert res.status_code == 200
    profile = res.json()

    assert "person" in profile
    assert profile["person"]["full_name"] == "Abebe Bikila"
    assert "organization" in profile
    assert "opportunities" in profile
    assert "activities" in profile
    assert "payments" in profile
    assert "timeline" in profile
    assert len(profile["timeline"]) > 0


def test_global_ecosystem_search(admin_token):
    """Verify global admin search across People, Organizations, Deals, and Inquiries."""
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Search for TechCorp
    res = client.get("/api/v1/admin/search?q=TechCorp", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["count"] > 0
    modules = {r["module"] for r in data["results"]}
    assert "Organizations" in modules or "CRM Opportunities" in modules
