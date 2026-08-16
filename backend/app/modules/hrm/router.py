from fastapi import APIRouter, Depends

from app.core.tenancy import get_tenant_id

router = APIRouter(prefix="/hrm", tags=["hrm"])


@router.get("/employees")
def list_employees(tenant_id: str = Depends(get_tenant_id)):
    return {"tenant_id": tenant_id, "employees": []}
