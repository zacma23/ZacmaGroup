from fastapi import APIRouter, Depends

from app.core.tenancy import get_tenant_id

router = APIRouter(prefix="/training", tags=["training"])


@router.get("/courses")
def list_courses(tenant_id: str = Depends(get_tenant_id)):
    return {"tenant_id": tenant_id, "courses": []}
