from app.core.db import supabase
from ai.rag.ingest import retrieve


def create_lead(tenant_id: str, name: str, email: str, source: str = "ai_agent"):
    return supabase.table("leads").insert({
        "tenant_id": tenant_id,
        "name": name,
        "email": email,
        "source": source,
        "status": "new",
    }).execute().data


def check_payment_status(tenant_id: str, customer_id: str):
    return supabase.table("payments").select("*").eq("tenant_id", tenant_id).eq("customer_id", customer_id).execute().data


def search_documents(tenant_id: str, query: str, collection: str):
    return retrieve(query=query, collection=collection, tenant_id=tenant_id, k=4)


TOOL_REGISTRY = {
    "create_lead": create_lead,
    "check_payment_status": check_payment_status,
    "search_documents": search_documents,
}
