"""Role-based access control dependencies for FastAPI routes.

Provides three dependency factories:

* ``require_authenticated`` — any valid JWT user
* ``require_role(allowed_roles)`` — user must have one of the listed roles
* ``require_permission(resource, action)`` — basic RBAC permission check

All dependencies return the user dict on success or raise HTTPException.
Superadmin role always passes all checks.
"""

from typing import Any, Callable

from fastapi import HTTPException, Request, status


# ---------------------------------------------------------------------------
# Role hierarchy and permission map
# ---------------------------------------------------------------------------

ROLE_PERMISSIONS: dict[str, set[str]] = {
    "superadmin": {"*"},  # wildcard — all permissions
    "admin": {
        "users.view", "users.create", "users.update", "users.delete",
        "clients.view", "clients.create", "clients.update", "clients.delete",
        "applications.view", "applications.create", "applications.update", "applications.approve", "applications.delete",
        "documents.view", "documents.upload", "documents.delete",
        "payments.view", "payments.create", "payments.update", "payments.refund", "payments.manage_providers",
        "reports.view", "reports.export",
        "settings.view", "settings.update",
        "hrm.view", "hrm.manage", "crm.manage", "marketing.manage",
    },
    "finance": {
        "payments.view", "payments.create", "payments.update", "payments.refund",
        "invoices.view", "invoices.create", "invoices.update",
        "reports.view", "reports.export",
        "hrm.payroll",
    },
    "hrm": {
        "employees.view", "employees.create", "employees.update",
        "leaves.view", "leaves.approve",
        "attendance.view", "attendance.log",
        "hrm.payroll",
        "reports.view",
    },
    "manager": {
        "users.view",
        "clients.view", "clients.create", "clients.update",
        "applications.view", "applications.create", "applications.update", "applications.approve",
        "documents.view", "documents.upload",
        "leaves.view", "leaves.approve",
        "reports.view",
    },
    "staff": {
        "users.view",
        "clients.view", "clients.create", "clients.update",
        "applications.view", "applications.create", "applications.update",
        "documents.view", "documents.upload",
        "payments.view", "payments.create",
        "reports.view",
    },
    "client": {
        "applications.view", "applications.create",
        "documents.view", "documents.upload",
        "payments.view",
    },
    "customer": {
        "applications.view", "applications.create",
        "documents.view", "documents.upload",
        "payments.view",
    },
    "student": {
        "applications.view", "applications.create",
        "documents.view", "documents.upload",
        "payments.view",
    },
}


# ---------------------------------------------------------------------------
# Dependencies & IDOR Helpers
# ---------------------------------------------------------------------------

def _extract_user(request: Request) -> dict[str, Any]:
    """Internal helper: get user from request state or raise 401."""
    user = getattr(request.state, "user", None)
    if not user or not isinstance(user, dict):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def require_authenticated(request: Request) -> dict[str, Any]:
    """Dependency: require any authenticated user."""
    return _extract_user(request)


def normalize_role(role: str) -> str:
    """Normalize role string aliases."""
    r = (role or "").strip().lower()
    if r in {"customer", "client", "user"}:
        return "client"
    if r in {"super_admin", "superadmin"}:
        return "superadmin"
    return r


def require_role(allowed_roles: list[str]) -> Callable:
    """Dependency factory: require user to have one of the specified roles."""
    normalized_allowed = {normalize_role(r) for r in allowed_roles}
    # If client is allowed, customer is also allowed
    if "client" in normalized_allowed:
        normalized_allowed.add("customer")

    def role_checker(request: Request) -> dict[str, Any]:
        user = _extract_user(request)
        user_role = normalize_role(user.get("role", ""))
        if user_role == "superadmin" or user_role in normalized_allowed or user.get("role") in allowed_roles:
            return user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions for this resource",
        )

    return role_checker


def verify_resource_ownership(
    user: dict[str, Any],
    resource: dict[str, Any],
    owner_fields: list[str] = ["user_id", "email", "client_id", "customer_email", "student_email", "created_by"],
    exempt_roles: list[str] = ["superadmin", "admin", "staff", "finance", "hrm", "manager"],
) -> bool:
    """Check whether the authenticated user owns the resource or has an administrative exempt role."""
    user_role = normalize_role(user.get("role", ""))
    exempt_set = {normalize_role(r) for r in exempt_roles}

    if user_role == "superadmin" or user_role in exempt_set:
        return True

    user_email = (user.get("email") or "").lower().strip()
    user_id = str(user.get("id") or user.get("sub") or user.get("firebase_uid") or "").strip()

    for field in owner_fields:
        val = resource.get(field)
        if val is None:
            continue
        val_str = str(val).strip()
        if user_id and val_str == user_id:
            return True
        if user_email and val_str.lower() == user_email:
            return True

    return False


def require_permission(resource: str, action: str) -> Callable:
    """Dependency factory: require user to have a specific resource.action permission."""
    permission_key = f"{resource}.{action}"

    def permission_checker(request: Request) -> dict[str, Any]:
        user = _extract_user(request)
        role = normalize_role(user.get("role", "client"))
        allowed = ROLE_PERMISSIONS.get(role, set())

        if "*" in allowed or permission_key in allowed:
            return user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission denied: {permission_key}",
        )

    return permission_checker
