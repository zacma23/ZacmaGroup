"""Tenant context helpers.

Authentication providers set ``request.state.user`` before protected routes
run. The only fallback is the explicitly enabled local demo tenant; a caller
cannot select another tenant through a request header or payload.
"""

from collections.abc import Mapping

from fastapi import HTTPException, Request, status

from app.core.config import settings


def get_tenant_id(request: Request) -> str:
    """Return the tenant established by authentication or local demo mode."""
    user = getattr(request.state, "user", None)
    if isinstance(user, Mapping):
        tenant_id = user.get("tenant_id")
        if isinstance(tenant_id, str) and tenant_id.strip():
            return tenant_id

    if settings.demo_mode:
        return settings.demo_tenant_id

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication is required to establish a tenant context.",
    )
