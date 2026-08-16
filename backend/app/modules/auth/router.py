from fastapi import APIRouter, Depends

from app.core.tenancy import get_tenant_id

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/session")
def get_session(tenant_id: str = Depends(get_tenant_id)):
    return {"tenant_id": tenant_id, "authenticated": True}
