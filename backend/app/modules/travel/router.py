from fastapi import APIRouter, Depends

from app.core.tenancy import get_tenant_id

router = APIRouter(prefix="/travel", tags=["travel"])


@router.get("/bookings")
def list_bookings(tenant_id: str = Depends(get_tenant_id)):
    return {"tenant_id": tenant_id, "bookings": []}
