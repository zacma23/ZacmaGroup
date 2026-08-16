from fastapi import APIRouter, Depends

from app.core.tenancy import get_tenant_id

router = APIRouter(prefix="/visa", tags=["visa"])


@router.get("/applications")
def list_applications(tenant_id: str = Depends(get_tenant_id)):
    return {"tenant_id": tenant_id, "applications": []}
