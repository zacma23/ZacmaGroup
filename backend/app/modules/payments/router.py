from fastapi import APIRouter, Depends

from app.core.tenancy import get_tenant_id

router = APIRouter(prefix="/payments", tags=["payments"])


@router.get("/invoices")
def list_invoices(tenant_id: str = Depends(get_tenant_id)):
    return {"tenant_id": tenant_id, "invoices": []}
