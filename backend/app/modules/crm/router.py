from fastapi import APIRouter, Depends

from app.core.db import supabase
from app.core.tenancy import get_tenant_id

router = APIRouter(prefix="/crm", tags=["crm"])


@router.get("/leads")
def list_leads(tenant_id: str = Depends(get_tenant_id)):
    if supabase is None:
        return []
    result = supabase.table("leads").select("*").eq("tenant_id", tenant_id).execute()
    return result.data


@router.post("/leads")
def create_lead(payload: dict, tenant_id: str = Depends(get_tenant_id)):
    if supabase is None:
        return {"tenant_id": tenant_id, "status": "demo-mode", "payload": payload}
    payload["tenant_id"] = tenant_id
    result = supabase.table("leads").insert(payload).execute()
    return result.data
