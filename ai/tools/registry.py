"""Tool implementations for AI agents.

Each tool is a plain function that AI agents can invoke. Tools that require
database access gracefully handle the case where Supabase is not configured
(demo mode) by returning descriptive messages instead of crashing.
"""

from app.core.db import supabase
from ai.rag.ingest import retrieve


def create_lead(tenant_id: str, name: str, email: str, source: str = "ai_agent"):
    """Create a new CRM lead for the given tenant."""
    if supabase is None:
        return {"status": "demo-mode", "message": f"Would create lead: {name} ({email}) for tenant {tenant_id}"}
    return supabase.table("leads").insert({
        "tenant_id": tenant_id,
        "name": name,
        "email": email,
        "source": source,
        "status": "new",
    }).execute().data


def check_payment_status(tenant_id: str, customer_id: str):
    """Check payment status for a customer."""
    if supabase is None:
        return {"status": "demo-mode", "message": f"Would check payments for customer {customer_id} in tenant {tenant_id}"}
    return supabase.table("payments").select("*").eq("tenant_id", tenant_id).eq("customer_id", customer_id).execute().data


def search_documents(tenant_id: str, query: str, collection: str):
    """Search documents in the vector database for the given tenant."""
    try:
        return retrieve(query=query, collection=collection, tenant_id=tenant_id, k=4)
    except Exception as e:
        return [f"Document search unavailable: {e}"]


TOOL_REGISTRY = {
    "create_lead": create_lead,
    "check_payment_status": check_payment_status,
    "search_documents": search_documents,
}
