from fastapi import APIRouter, Depends

from app.core.tenancy import get_tenant_id

router = APIRouter(prefix="/marketing", tags=["marketing"])


@router.get("/campaigns")
def list_campaigns(tenant_id: str = Depends(get_tenant_id)):
    return {"tenant_id": tenant_id, "campaigns": []}
