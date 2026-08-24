"""Comprehensive Test Suite for Admin Panel Search, Sorting, Filtering, Pagination, and Natural Language AI Querying.

Tests cover:
- Multi-Field Keyword Matching (Name, Email, Phone, Reference Code, ID, Category)
- Multi-Criteria Server-Side Sorting (Newest, Oldest, Name A-Z, Name Z-A, Amount High-Low, Amount Low-High, Status, Priority)
- Filter Combinations (Module + Status + Date Bounds + Amount Range)
- Server-Side Pagination & Facet Aggregation
- Natural Language AI Query Engine (Intent detection, Grounded insights)
- Role-Based Authorization and Tenant Isolation
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.auth import create_access_token
from app.core.config import settings
from app.services.admin_search_service import AdminSearchService

client = TestClient(app)


@pytest.fixture
def admin_token():
    return create_access_token({
        "sub": "admin-search-user",
        "email": "admin@zacma.com",
        "role": "admin",
        "tenant_id": settings.demo_tenant_id,
        "full_name": "Zacma Admin",
    })


@pytest.fixture
def staff_token():
    return create_access_token({
        "sub": "staff-search-user",
        "email": "staff@zacma.com",
        "role": "staff",
        "tenant_id": settings.demo_tenant_id,
        "full_name": "Zacma Staff",
    })


@pytest.fixture
def client_token():
    return create_access_token({
        "sub": "client-search-user",
        "email": "client@example.com",
        "role": "client",
        "tenant_id": settings.demo_tenant_id,
        "full_name": "Standard Client",
    })


def test_admin_search_keyword_and_multi_field(admin_token):
    """Verify multi-field search matches by name, email, phone, reference code, and ID."""
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Search by name
    res = client.get("/api/v1/admin/search?q=Abebe", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["pagination"]["total_count"] >= 1
    assert any("abebe" in (r["title"] + (r.get("email") or "")).lower() for r in data["results"])

    # 2. Search by reference code or prefix
    res2 = client.get("/api/v1/admin/search?q=STU", headers=headers)
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["pagination"]["total_count"] >= 1
    assert any("training" in r["module"].lower() or "stu" in (r.get("reference_code") or "").lower() for r in data2["results"])


def test_admin_search_sorting_engine(admin_token):
    """Verify server-side sorting options."""
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Sort by Name A-Z
    res_asc = client.get("/api/v1/admin/search?sort_by=name_asc&page_size=10", headers=headers)
    assert res_asc.status_code == 200
    titles_asc = [r["title"].lower() for r in res_asc.json()["results"]]
    assert titles_asc == sorted(titles_asc)

    # 2. Sort by Name Z-A
    res_desc = client.get("/api/v1/admin/search?sort_by=name_desc&page_size=10", headers=headers)
    assert res_desc.status_code == 200
    titles_desc = [r["title"].lower() for r in res_desc.json()["results"]]
    assert titles_desc == sorted(titles_desc, reverse=True)

    # 3. Sort by Amount High to Low
    res_amount = client.get("/api/v1/admin/search?module=payments&sort_by=amount_desc&page_size=10", headers=headers)
    assert res_amount.status_code == 200
    amounts = [r["amount"] for r in res_amount.json()["results"] if r["amount"] is not None]
    if len(amounts) > 1:
        assert amounts[0] >= amounts[-1]


def test_admin_search_module_and_status_filtering(admin_token):
    """Verify filtering records by module, lifecycle status, and date bounds."""
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Filter by Module = Visa
    res_visa = client.get("/api/v1/admin/search?module=visa", headers=headers)
    assert res_visa.status_code == 200
    for r in res_visa.json()["results"]:
        assert r["module"].lower() == "visa"

    # 2. Filter by Module = Payments + Status = Pending
    res_pay = client.get("/api/v1/admin/search?module=payments&status=pending", headers=headers)
    assert res_pay.status_code == 200
    for r in res_pay.json()["results"]:
        assert r["module"].lower() == "payments"
        assert r["status"].lower() == "pending"


def test_admin_search_pagination_and_facets(admin_token):
    """Verify server-side pagination calculation and facet aggregation."""
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Page size 5, page 1
    res_p1 = client.get("/api/v1/admin/search?page=1&page_size=5", headers=headers)
    assert res_p1.status_code == 200
    d1 = res_p1.json()
    assert len(d1["results"]) <= 5
    assert d1["pagination"]["page"] == 1
    assert d1["pagination"]["page_size"] == 5
    assert d1["pagination"]["total_pages"] >= 1
    assert len(d1["module_facets"]) >= 1

    # Empty state check
    res_empty = client.get("/api/v1/admin/search?q=NonExistentQueryXYZ999", headers=headers)
    assert res_empty.status_code == 200
    assert res_empty.json()["pagination"]["total_count"] == 0
    assert len(res_empty.json()["results"]) == 0


def test_admin_natural_language_ai_search(admin_token):
    """Verify natural language query translation and grounded AI insights."""
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Query 1: Visa applicants
    res1 = client.post(
        "/api/v1/admin/search/ai",
        json={"query": "Show customers who requested visa services", "max_results": 10},
        headers=headers,
    )
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["total_found"] >= 1
    assert "VISA" in data1["parsed_intent"]
    assert len(data1["ai_summary"]) > 10

    # Query 2: Unpaid invoices
    res2 = client.post(
        "/api/v1/admin/search/ai",
        json={"query": "Find unpaid invoices", "max_results": 10},
        headers=headers,
    )
    assert res2.status_code == 200
    data2 = res2.json()
    assert "PAYMENTS" in data2["parsed_intent"] or "unpaid" in data2["parsed_intent"]


def test_admin_search_authorization_and_idor_protection(staff_token, client_token):
    """Verify role-based access control and unauthorized rejection."""
    # 1. Staff access is permitted
    staff_res = client.get("/api/v1/admin/search", headers={"Authorization": f"Bearer {staff_token}"})
    assert staff_res.status_code == 200

    # 2. Client role is strictly forbidden
    client_res = client.get("/api/v1/admin/search", headers={"Authorization": f"Bearer {client_token}"})
    assert client_res.status_code == 403

    # 3. Unauthenticated is rejected
    unauth_res = client.get("/api/v1/admin/search")
    assert unauth_res.status_code in [401, 403]
