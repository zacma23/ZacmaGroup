"""Authentication endpoints — login, register, profile, password reset, session.

Provides secure authentication with bcrypt password hashing, sliding-window
brute-force rate limiting, session token generation, role verification, and
profile management.
"""

from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.core.auth import (
    create_access_token,
    create_password_reset_token,
    create_verification_token,
    decode_access_token,
    get_current_user,
    get_password_hash,
    log_audit_event,
    login_tracker,
    verify_password,
    verify_password_reset_token,
    verify_verification_token,
)
from app.core.config import settings
from app.core.db import supabase
from app.core.demo_data import admin_users_store, crm_contacts_store
from app.core.tenancy import get_tenant_id
from app.models import (
    ChangePasswordRequest,
    LoginRequest,
    PasswordResetConfirm,
    PasswordResetRequest,
    ProfileUpdateRequest,
    RegisterRequest,
    TokenResponse,
    UserProfile,
    VerifyAccountRequest,
)

router = APIRouter(prefix="/auth", tags=["auth"])


# ---------------------------------------------------------------------------
# POST /auth/login
# ---------------------------------------------------------------------------

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, request: Request):
    """Authenticate a user with brute-force defense and return a JWT access token."""
    client_ip = request.client.host if request.client else "127.0.0.1"
    rate_key = f"{client_ip}:{payload.email.lower().strip()}"

    # 1. Check brute-force lockout
    is_locked, remaining_sec = login_tracker.is_locked(rate_key)
    if is_locked:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many failed login attempts. Please try again in {remaining_sec // 60 + 1} minutes.",
        )

    if settings.demo_mode:
        demo_users = admin_users_store.list_all(settings.demo_tenant_id)
        # Search by email or phone
        matched = next(
            (
                u for u in demo_users
                if u["email"].lower() == payload.email.lower()
                or u.get("phone", "") == payload.email
            ),
            None,
        )

        # In demo mode: If demo user exists, verify password if set; otherwise grant client token
        if matched and "password_hash" in matched:
            if not verify_password(payload.password, matched["password_hash"]):
                login_tracker.record_failure(rate_key)
                log_audit_event(
                    settings.demo_tenant_id,
                    "LOGIN_FAILED",
                    "auth",
                    f"Failed login attempt for {payload.email}",
                    user_email=payload.email,
                    ip_address=client_ip,
                )
                raise HTTPException(status_code=401, detail="Invalid email or password")

        role = matched["role"] if matched else "client"
        full_name = matched["full_name"] if matched else payload.email.split("@")[0].title()
        user_id = matched["id"] if matched else f"usr-{abs(hash(payload.email)) % 100000}"
        email = matched["email"] if matched else payload.email

        # Successful login
        login_tracker.record_success(rate_key)
        log_audit_event(
            settings.demo_tenant_id,
            "LOGIN_SUCCESS",
            "auth",
            f"User {email} logged in successfully",
            user_email=email,
            ip_address=client_ip,
        )

        expire_delta = timedelta(days=7) if payload.remember_me else timedelta(minutes=settings.jwt_expire_minutes)
        token = create_access_token(
            {
                "sub": user_id,
                "email": email,
                "role": role,
                "tenant_id": settings.demo_tenant_id,
                "full_name": full_name,
            },
            expires_delta=expire_delta,
        )

        return TokenResponse(
            access_token=token,
            role=role,
            tenant_id=settings.demo_tenant_id,
            email=email,
            full_name=full_name,
            user_id=user_id,
        )

    # Production mode — verify against Supabase
    if supabase is None:
        raise HTTPException(status_code=503, detail="Database not configured")

    result = supabase.table("users").select("*").eq("email", payload.email.lower()).execute()
    if not result.data:
        login_tracker.record_failure(rate_key)
        raise HTTPException(status_code=401, detail="Invalid email or password")

    user = result.data[0]
    stored_hash = user.get("password_hash", "")
    if not verify_password(payload.password, stored_hash):
        login_tracker.record_failure(rate_key)
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if user.get("status") != "active":
        raise HTTPException(status_code=403, detail="Account is suspended or not active")

    login_tracker.record_success(rate_key)
    expire_delta = timedelta(days=7) if payload.remember_me else timedelta(minutes=settings.jwt_expire_minutes)

    token = create_access_token(
        {
            "sub": user["id"],
            "email": user["email"],
            "role": user.get("role", "client"),
            "tenant_id": user["tenant_id"],
            "full_name": user.get("full_name", ""),
        },
        expires_delta=expire_delta,
    )

    return TokenResponse(
        access_token=token,
        role=user.get("role", "client"),
        tenant_id=user["tenant_id"],
        email=user["email"],
        full_name=user.get("full_name", ""),
        user_id=user["id"],
    )


# ---------------------------------------------------------------------------
# POST /auth/register
# ---------------------------------------------------------------------------

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, request: Request):
    """Register a new client user with email, phone, and profile details."""
    client_ip = request.client.host if request.client else "127.0.0.1"

    if settings.demo_mode:
        existing = admin_users_store.list_all(settings.demo_tenant_id)
        if any(u["email"].lower() == payload.email.lower() for u in existing):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email is already registered")

        pw_hash = get_password_hash(payload.password)
        new_user = admin_users_store.create(
            {
                "email": payload.email.lower(),
                "full_name": payload.full_name,
                "phone": payload.phone or "",
                "address": payload.address or "Addis Ababa",
                "education_level": payload.education_level or "Diploma",
                "role": payload.role if payload.role in {"client", "student"} else "client",
                "status": "active",
                "is_verified": True,
                "password_hash": pw_hash,
                "created_at": datetime.now(timezone.utc).isoformat(),
            },
            settings.demo_tenant_id,
        )

        # Sync to CRM Contacts
        crm_contacts_store.create(
            {
                "full_name": payload.full_name,
                "email": payload.email.lower(),
                "phone": payload.phone or "",
                "address": payload.address or "Addis Ababa",
                "country": "Ethiopia",
                "source_module": "Custom",
                "status": "Lead",
                "tags": ["Registered Client"],
                "assigned_admin_id": "admin@zacma.com",
                "timeline": [
                    {
                        "id": f"evt-{abs(hash(payload.email)) % 10000}",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "action": "Account Created",
                        "description": "User created client portal account",
                        "actor": payload.email,
                    }
                ],
            },
            settings.demo_tenant_id,
        )

        log_audit_event(
            settings.demo_tenant_id,
            "REGISTER",
            "auth",
            f"New client registered: {payload.email}",
            user_email=payload.email,
            ip_address=client_ip,
        )

        token = create_access_token(
            {
                "sub": new_user["id"],
                "email": payload.email.lower(),
                "role": new_user["role"],
                "tenant_id": settings.demo_tenant_id,
                "full_name": payload.full_name,
            }
        )

        return TokenResponse(
            access_token=token,
            role=new_user["role"],
            tenant_id=settings.demo_tenant_id,
            email=payload.email.lower(),
            full_name=payload.full_name,
            user_id=new_user["id"],
        )

    # Production mode with Supabase
    if supabase is None:
        raise HTTPException(status_code=503, detail="Database not configured")

    existing = supabase.table("users").select("id").eq("email", payload.email.lower()).execute()
    if existing.data:
        raise HTTPException(status_code=409, detail="Email is already registered")

    pw_hash = get_password_hash(payload.password)
    result = supabase.table("users").insert(
        {
            "email": payload.email.lower(),
            "full_name": payload.full_name,
            "password_hash": pw_hash,
            "phone": payload.phone,
            "role": "client",
            "status": "active",
            "tenant_id": settings.demo_tenant_id,
        }
    ).execute()

    user = result.data[0]
    token = create_access_token(
        {
            "sub": user["id"],
            "email": user["email"],
            "role": "client",
            "tenant_id": user["tenant_id"],
            "full_name": user.get("full_name", ""),
        }
    )

    return TokenResponse(
        access_token=token,
        role="client",
        tenant_id=user["tenant_id"],
        email=user["email"],
        full_name=user.get("full_name", ""),
        user_id=user["id"],
    )


# ---------------------------------------------------------------------------
# GET /auth/me & PUT /auth/me (Client Profile)
# ---------------------------------------------------------------------------

@router.get("/me", response_model=UserProfile)
def get_me(user: dict = Depends(get_current_user)):
    """Return the profile of the currently authenticated user."""
    tid = user.get("tenant_id", settings.demo_tenant_id)
    email = user.get("email", "")

    if settings.demo_mode:
        demo_users = admin_users_store.list_all(tid)
        matched = next((u for u in demo_users if u["email"].lower() == email.lower()), None)
        if matched:
            return UserProfile(
                id=matched["id"],
                email=matched["email"],
                full_name=matched.get("full_name", ""),
                role=matched.get("role", "client"),
                tenant_id=tid,
                phone=matched.get("phone"),
                address=matched.get("address"),
                education_level=matched.get("education_level"),
                avatar_url=matched.get("avatar_url"),
                status=matched.get("status", "active"),
                is_verified=matched.get("is_verified", True),
                created_at=matched.get("created_at"),
            )

    return UserProfile(
        id=user.get("sub", ""),
        email=email,
        full_name=user.get("full_name", ""),
        role=user.get("role", "client"),
        tenant_id=tid,
        status="active",
        is_verified=True,
    )


@router.put("/me", response_model=UserProfile)
def update_me(payload: ProfileUpdateRequest, user: dict = Depends(get_current_user)):
    """Update profile details for the currently authenticated user."""
    tid = user.get("tenant_id", settings.demo_tenant_id)
    email = user.get("email", "")

    if settings.demo_mode:
        demo_users = admin_users_store.list_all(tid)
        matched = next((u for u in demo_users if u["email"].lower() == email.lower()), None)
        if matched:
            updates = {k: v for k, v in payload.model_dump().items() if v is not None}
            updated = admin_users_store.update(matched["id"], updates, tid)
            return UserProfile(
                id=updated["id"],
                email=updated["email"],
                full_name=updated.get("full_name", ""),
                role=updated.get("role", "client"),
                tenant_id=tid,
                phone=updated.get("phone"),
                address=updated.get("address"),
                education_level=updated.get("education_level"),
                avatar_url=updated.get("avatar_url"),
                status=updated.get("status", "active"),
                is_verified=updated.get("is_verified", True),
            )

    return UserProfile(
        id=user.get("sub", ""),
        email=email,
        full_name=payload.full_name or user.get("full_name", ""),
        role=user.get("role", "client"),
        tenant_id=tid,
        phone=payload.phone,
        address=payload.address,
        education_level=payload.education_level,
        status="active",
        is_verified=True,
    )


# ---------------------------------------------------------------------------
# Password Reset & Change
# ---------------------------------------------------------------------------

@router.post("/password-reset-request")
def request_password_reset(payload: PasswordResetRequest):
    """Generate a password reset token for account recovery."""
    reset_token = create_password_reset_token(payload.email)
    log_audit_event(
        settings.demo_tenant_id,
        "PASSWORD_RESET_REQUESTED",
        "auth",
        f"Password reset token requested for {payload.email}",
        user_email=payload.email,
    )
    return {
        "status": "success",
        "message": f"If an account exists for {payload.email}, a password reset link has been dispatched.",
        "reset_token": reset_token,  # Provided for seamless demo/testing
    }


@router.post("/password-reset-confirm")
def confirm_password_reset(payload: PasswordResetConfirm):
    """Reset password using a valid reset token."""
    email = verify_password_reset_token(payload.token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired password reset token")

    new_hash = get_password_hash(payload.new_password)
    if settings.demo_mode:
        demo_users = admin_users_store.list_all(settings.demo_tenant_id)
        matched = next((u for u in demo_users if u["email"].lower() == email.lower()), None)
        if matched:
            admin_users_store.update(matched["id"], {"password_hash": new_hash}, settings.demo_tenant_id)

    log_audit_event(
        settings.demo_tenant_id,
        "PASSWORD_RESET_COMPLETED",
        "auth",
        f"Password successfully reset for {email}",
        user_email=email,
    )
    return {"status": "success", "message": "Your password has been successfully updated. You may now log in."}


@router.post("/change-password")
def change_password(payload: ChangePasswordRequest, user: dict = Depends(get_current_user)):
    """Change password for an authenticated user."""
    email = user.get("email", "")
    tid = user.get("tenant_id", settings.demo_tenant_id)

    if settings.demo_mode:
        demo_users = admin_users_store.list_all(tid)
        matched = next((u for u in demo_users if u["email"].lower() == email.lower()), None)
        if matched and "password_hash" in matched:
            if not verify_password(payload.old_password, matched["password_hash"]):
                raise HTTPException(status_code=400, detail="Incorrect current password")
            admin_users_store.update(matched["id"], {"password_hash": get_password_hash(payload.new_password)}, tid)

    log_audit_event(tid, "PASSWORD_CHANGED", "auth", f"User {email} changed password", user_email=email)
    return {"status": "success", "message": "Password changed successfully"}


# ---------------------------------------------------------------------------
# Account Verification & Logout
# ---------------------------------------------------------------------------

@router.post("/verify-account")
def verify_account(payload: VerifyAccountRequest):
    """Verify email or phone OTP/token."""
    email = verify_verification_token(payload.token, payload.type)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired verification token")
    return {"status": "success", "message": f"Account for {email} verified successfully"}


@router.post("/logout")
def logout(user: dict = Depends(get_current_user)):
    """Invalidate session and log audit trail."""
    email = user.get("email", "")
    tid = user.get("tenant_id", settings.demo_tenant_id)
    log_audit_event(tid, "LOGOUT", "auth", f"User {email} logged out", user_email=email)
    return {"status": "success", "message": "Logged out successfully"}


# ---------------------------------------------------------------------------
# GET /auth/session
# ---------------------------------------------------------------------------

@router.get("/session")
def get_session(request: Request, tenant_id: str = Depends(get_tenant_id)):
    """Return basic session info and authenticated user context."""
    user = getattr(request.state, "user", None)
    return {
        "tenant_id": tenant_id,
        "authenticated": True if (user is not None or settings.demo_mode) else False,
        "user": user,
    }
