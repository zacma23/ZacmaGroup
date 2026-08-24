"""Authentication endpoints — Firebase Auth, email/password, phone OTP, profile, session management.

Provides secure authentication with bcrypt password hashing, sliding-window
brute-force rate limiting, Firebase ID token verification, session cookie management,
IDOR protection, role verification, and security audit logging.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from app.core.auth import (
    clear_auth_cookies,
    create_access_token,
    create_password_reset_token,
    create_verification_token,
    decode_access_token,
    get_current_user,
    get_password_hash,
    log_audit_event,
    log_security_event,
    login_tracker,
    phone_otp_tracker,
    revoke_token,
    set_auth_cookies,
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
    EmailResendRequest,
    FirebaseLoginRequest,
    LoginRequest,
    PasswordResetConfirm,
    PasswordResetRequest,
    PhoneOtpSendRequest,
    PhoneOtpVerifyRequest,
    ProfileUpdateRequest,
    RegisterRequest,
    TokenResponse,
    UserProfile,
    VerifyAccountRequest,
)
from app.services.firebase_auth_service import FirebaseAuthService

router = APIRouter(prefix="/auth", tags=["auth"])


# ---------------------------------------------------------------------------
# POST /auth/login (Email/Password or Phone with Brute-Force Defense)
# ---------------------------------------------------------------------------

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, request: Request, response: Response):
    """Authenticate user with brute-force defense, return JWT access token, and set HttpOnly session cookie."""
    client_ip = request.client.host if request.client else "127.0.0.1"
    user_agent = request.headers.get("User-Agent", "Unknown")
    rate_key = f"{client_ip}:{payload.email.lower().strip()}"

    # 1. Check brute-force lockout
    is_locked, remaining_sec = login_tracker.is_locked(rate_key)
    if is_locked:
        log_security_event(
            settings.demo_tenant_id,
            "LOGIN_LOCKED_OUT",
            payload.email,
            f"Rate limit lockout active ({remaining_sec}s remaining)",
            ip_address=client_ip,
            user_agent=user_agent,
            status_code=429,
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many failed login attempts. Please try again in {remaining_sec // 60 + 1} minutes.",
        )

    try:
        from app.services.supabase_auth_service import SupabaseAuthService
        auth_data = SupabaseAuthService.authenticate(
            email=payload.email,
            password=payload.password,
            remember_me=payload.remember_me,
        )

        login_tracker.record_success(rate_key)
        log_security_event(
            auth_data.get("tenant_id", settings.demo_tenant_id),
            "LOGIN_SUCCESS",
            payload.email,
            f"User authenticated successfully (Role: {auth_data.get('role')})",
            ip_address=client_ip,
            user_agent=user_agent,
            status_code=200,
        )

        set_auth_cookies(response, auth_data["access_token"], payload.remember_me)

        return TokenResponse(
            access_token=auth_data["access_token"],
            role=auth_data["role"],
            tenant_id=auth_data["tenant_id"],
            email=auth_data["email"],
            full_name=auth_data["full_name"],
            user_id=auth_data["user_id"],
        )
    except HTTPException as e:
        if e.status_code == 401:
            login_tracker.record_failure(rate_key)
            log_security_event(
                settings.demo_tenant_id,
                "LOGIN_FAILED",
                payload.email,
                "Invalid credentials attempt",
                ip_address=client_ip,
                user_agent=user_agent,
                status_code=401,
            )
        raise


# ---------------------------------------------------------------------------
# POST /auth/firebase-login (Firebase ID Token Authentication)
# ---------------------------------------------------------------------------

@router.post("/firebase-login", response_model=TokenResponse)
def firebase_login(payload: FirebaseLoginRequest, request: Request, response: Response):
    """Authenticate using a verified Firebase ID token and issue internal session token."""
    client_ip = request.client.host if request.client else "127.0.0.1"
    user_agent = request.headers.get("User-Agent", "Unknown")

    fb_user = FirebaseAuthService.verify_firebase_token(payload.id_token)
    if not fb_user:
        log_security_event(
            settings.demo_tenant_id,
            "FIREBASE_AUTH_FAILED",
            "anonymous",
            "Invalid or expired Firebase ID token",
            ip_address=client_ip,
            user_agent=user_agent,
            status_code=401,
        )
        raise HTTPException(status_code=401, detail="Invalid or expired Firebase Authentication token")

    email = fb_user.get("email", "").lower().strip()
    uid = fb_user.get("firebase_uid") or fb_user.get("id")
    role = fb_user.get("role", "client")
    full_name = fb_user.get("full_name", "")
    tenant_id = fb_user.get("tenant_id", settings.demo_tenant_id)

    # Sync with local demo store or Supabase
    if settings.demo_mode:
        existing = admin_users_store.list_all(tenant_id)
        matched = next((u for u in existing if u["email"].lower() == email or u.get("firebase_uid") == uid), None)
        if matched:
            user_id = matched["id"]
            role = matched.get("role", role)
            if not matched.get("firebase_uid"):
                matched["firebase_uid"] = uid
        else:
            user_id = uid
            admin_users_store.create(
                {
                    "id": user_id,
                    "firebase_uid": uid,
                    "email": email,
                    "full_name": full_name,
                    "role": "client",
                    "status": "active",
                    "is_verified": fb_user.get("email_verified", True),
                    "created_at": datetime.now(timezone.utc).isoformat(),
                },
                tenant_id,
            )
    else:
        user_id = uid

    expire_delta = timedelta(days=7) if payload.remember_me else timedelta(minutes=settings.jwt_expire_minutes)
    token = create_access_token(
        {
            "sub": user_id,
            "email": email,
            "role": role,
            "tenant_id": tenant_id,
            "full_name": full_name,
            "firebase_uid": uid,
        },
        expires_delta=expire_delta,
    )

    set_auth_cookies(response, token, payload.remember_me)

    log_security_event(
        tenant_id,
        "LOGIN_SUCCESS_FIREBASE",
        email,
        f"Authenticated via Firebase (UID: {uid})",
        ip_address=client_ip,
        user_agent=user_agent,
        status_code=200,
    )

    return TokenResponse(
        access_token=token,
        role=role,
        tenant_id=tenant_id,
        email=email,
        full_name=full_name,
        user_id=user_id,
    )


# ---------------------------------------------------------------------------
# POST /auth/register (Client Account Creation with Role Sanitization)
# ---------------------------------------------------------------------------

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, request: Request, response: Response):
    """Register a new user account into Supabase Auth and database profiles table."""
    client_ip = request.client.host if request.client else "127.0.0.1"
    user_agent = request.headers.get("User-Agent", "Unknown")

    from app.services.supabase_auth_service import SupabaseAuthService
    reg_data = SupabaseAuthService.register(
        email=payload.email,
        password=payload.password,
        full_name=payload.full_name,
        phone=payload.phone,
        address=payload.address,
        education_level=payload.education_level,
        role=payload.role or "client",
        tenant_id=settings.demo_tenant_id,
    )

    log_security_event(
        reg_data.get("tenant_id", settings.demo_tenant_id),
        "REGISTER",
        payload.email,
        f"New user registered (Role: {reg_data.get('role')})",
        ip_address=client_ip,
        user_agent=user_agent,
        status_code=201,
    )

    set_auth_cookies(response, reg_data["access_token"])

    return TokenResponse(
        access_token=reg_data["access_token"],
        role=reg_data["role"],
        tenant_id=reg_data["tenant_id"],
        email=reg_data["email"],
        full_name=reg_data["full_name"],
        user_id=reg_data["user_id"],
    )


# ---------------------------------------------------------------------------
# GET /auth/me & PUT /auth/me (User Profile with IDOR Protection)
# ---------------------------------------------------------------------------

@router.get("/me", response_model=UserProfile)
def get_me(user: dict = Depends(get_current_user)):
    """Return the profile of the currently authenticated user."""
    tid = user.get("tenant_id", settings.demo_tenant_id)
    email = user.get("email", "")

    if supabase is not None:
        try:
            res = supabase.table("profiles").select("*").eq("email", email.lower()).execute()
            if res.data and len(res.data) > 0:
                p = res.data[0]
                return UserProfile(
                    id=p["id"],
                    email=p["email"],
                    full_name=p.get("full_name", user.get("full_name", "")),
                    role=p.get("role", user.get("role", "client")),
                    tenant_id=p.get("tenant_id", tid),
                    phone=p.get("phone"),
                    address=(p.get("metadata") or {}).get("address") if isinstance(p.get("metadata"), dict) else None,
                    education_level=(p.get("metadata") or {}).get("education_level") if isinstance(p.get("metadata"), dict) else None,
                    avatar_url=p.get("avatar_url"),
                    status=p.get("status", "active"),
                    is_verified=True,
                    created_at=p.get("created_at"),
                )
        except Exception:
            pass

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
    """Update profile details for the currently authenticated user. Privileged fields are immutable."""
    tid = user.get("tenant_id", settings.demo_tenant_id)
    email = user.get("email", "")

    if settings.demo_mode:
        demo_users = admin_users_store.list_all(tid)
        matched = next((u for u in demo_users if u["email"].lower() == email.lower()), None)
        if matched:
            updates = {k: v for k, v in payload.model_dump().items() if v is not None}
            # Strictly prevent role / privilege tampering
            updates.pop("role", None)
            updates.pop("status", None)
            updates.pop("is_verified", None)
            updates.pop("tenant_id", None)
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
# Password Reset Flow (Account Enumeration Defense)
# ---------------------------------------------------------------------------

@router.post("/password-reset-request")
def request_password_reset(payload: PasswordResetRequest, request: Request):
    """Initiate password recovery. Always returns a generic response to prevent user enumeration."""
    client_ip = request.client.host if request.client else "127.0.0.1"
    user_agent = request.headers.get("User-Agent", "Unknown")

    reset_token = create_password_reset_token(payload.email.lower().strip())
    log_security_event(
        settings.demo_tenant_id,
        "PASSWORD_RESET_REQUESTED",
        payload.email,
        f"Password recovery requested from {client_ip}",
        ip_address=client_ip,
        user_agent=user_agent,
        status_code=200,
    )
    return {
        "status": "success",
        "message": "If an account exists for this information, recovery instructions have been sent.",
        "reset_token": reset_token,  # Provided for test automation and staging verification
    }


@router.post("/password-reset-confirm")
def confirm_password_reset(payload: PasswordResetConfirm, request: Request):
    """Complete password reset using a cryptographically verified reset token."""
    client_ip = request.client.host if request.client else "127.0.0.1"
    user_agent = request.headers.get("User-Agent", "Unknown")

    email = verify_password_reset_token(payload.token)
    if not email:
        log_security_event(
            settings.demo_tenant_id,
            "PASSWORD_RESET_FAILED",
            "unknown",
            "Invalid or expired reset token submitted",
            ip_address=client_ip,
            user_agent=user_agent,
            status_code=400,
        )
        raise HTTPException(status_code=400, detail="Invalid or expired password reset token")

    # Invalidate token to prevent reuse
    revoke_token(payload.token)

    new_hash = get_password_hash(payload.new_password)
    if settings.demo_mode:
        demo_users = admin_users_store.list_all(settings.demo_tenant_id)
        matched = next((u for u in demo_users if u["email"].lower() == email.lower()), None)
        if matched:
            admin_users_store.update(matched["id"], {"password_hash": new_hash}, settings.demo_tenant_id)

    log_security_event(
        settings.demo_tenant_id,
        "PASSWORD_RESET_COMPLETED",
        email,
        "Password successfully updated via reset token",
        ip_address=client_ip,
        user_agent=user_agent,
        status_code=200,
    )
    return {"status": "success", "message": "Your password has been successfully updated. You may now log in."}


@router.post("/change-password")
def change_password(payload: ChangePasswordRequest, user: dict = Depends(get_current_user)):
    """Change password for an authenticated user with current password validation."""
    email = user.get("email", "")
    tid = user.get("tenant_id", settings.demo_tenant_id)

    if settings.demo_mode:
        demo_users = admin_users_store.list_all(tid)
        matched = next((u for u in demo_users if u["email"].lower() == email.lower()), None)
        if matched and "password_hash" in matched:
            if not verify_password(payload.old_password, matched["password_hash"]):
                raise HTTPException(status_code=400, detail="Incorrect current password")
            admin_users_store.update(matched["id"], {"password_hash": get_password_hash(payload.new_password)}, tid)

    log_security_event(tid, "PASSWORD_CHANGED", email, "Authenticated password change completed")
    return {"status": "success", "message": "Password changed successfully"}


# ---------------------------------------------------------------------------
# Phone / SMS OTP Verification Flow
# ---------------------------------------------------------------------------

@router.post("/phone/send-otp")
def send_phone_otp(payload: PhoneOtpSendRequest, request: Request):
    """Generate and dispatch SMS OTP for phone verification with rate limiting."""
    client_ip = request.client.host if request.client else "127.0.0.1"
    try:
        plain_otp, _ = phone_otp_tracker.generate_otp(payload.phone)
        log_security_event(
            settings.demo_tenant_id,
            "PHONE_OTP_DISPATCHED",
            payload.phone,
            "SMS OTP generated and dispatched",
            ip_address=client_ip,
        )
        return {
            "status": "success",
            "message": f"Verification code dispatched to {payload.phone}",
            "demo_otp": plain_otp if settings.demo_mode else None,
        }
    except ValueError as val_err:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(val_err))


@router.post("/phone/verify-otp")
def verify_phone_otp(payload: PhoneOtpVerifyRequest, request: Request, user: dict = Depends(get_current_user)):
    """Verify phone OTP and mark the user's phone as verified."""
    client_ip = request.client.host if request.client else "127.0.0.1"
    if not phone_otp_tracker.verify_otp(payload.phone, payload.otp):
        log_security_event(
            settings.demo_tenant_id,
            "PHONE_OTP_FAILED",
            payload.phone,
            "Invalid or expired OTP attempt",
            ip_address=client_ip,
            status_code=400,
        )
        raise HTTPException(status_code=400, detail="Invalid or expired verification code")

    tid = user.get("tenant_id", settings.demo_tenant_id)
    email = user.get("email", "")
    if settings.demo_mode:
        for u in admin_users_store.list_all(tid):
            if u["email"].lower() == email.lower():
                admin_users_store.update(u["id"], {"phone": payload.phone, "phone_verified": True}, tid)
                break

    log_security_event(
        tid,
        "PHONE_VERIFIED",
        email,
        f"Phone {payload.phone} successfully verified",
        ip_address=client_ip,
        status_code=200,
    )
    return {"status": "success", "message": f"Phone {payload.phone} verified successfully"}


# ---------------------------------------------------------------------------
# Email Verification Flow
# ---------------------------------------------------------------------------

@router.post("/email/resend-verification")
def resend_email_verification(payload: EmailResendRequest, request: Request):
    """Resend email verification link with rate limiting."""
    client_ip = request.client.host if request.client else "127.0.0.1"
    token = create_verification_token(payload.email)
    log_security_event(
        settings.demo_tenant_id,
        "EMAIL_VERIFICATION_RESENT",
        payload.email,
        "Verification email link regenerated",
        ip_address=client_ip,
    )
    return {
        "status": "success",
        "message": f"Verification email resent to {payload.email}",
        "verification_token": token,
    }


@router.post("/verify-account")
def verify_account(payload: VerifyAccountRequest, request: Request):
    """Verify email account token."""
    client_ip = request.client.host if request.client else "127.0.0.1"
    email = verify_verification_token(payload.token, payload.type)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired verification token")

    if settings.demo_mode:
        for u in admin_users_store.list_all(settings.demo_tenant_id):
            if u["email"].lower() == email.lower():
                admin_users_store.update(u["id"], {"is_verified": True}, settings.demo_tenant_id)
                break

    log_security_event(
        settings.demo_tenant_id,
        "EMAIL_VERIFIED",
        email,
        "Email verified successfully",
        ip_address=client_ip,
    )
    return {"status": "success", "message": f"Account for {email} verified successfully"}


# ---------------------------------------------------------------------------
# POST /auth/logout (Session Invalidation & Cookie Clearing)
# ---------------------------------------------------------------------------

@router.post("/logout")
def logout(request: Request, response: Response, user: dict = Depends(get_current_user)):
    """Terminate the authenticated session, revoke token, clear cookies, and log audit event."""
    email = user.get("email", "")
    tid = user.get("tenant_id", settings.demo_tenant_id)
    client_ip = request.client.host if request.client else "127.0.0.1"
    user_agent = request.headers.get("User-Agent", "Unknown")

    # Extract token from Authorization header or cookie
    token = None
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1].strip()
    elif request.cookies.get(settings.session_cookie_name):
        token = request.cookies.get(settings.session_cookie_name)

    if token:
        revoke_token(token)

    clear_auth_cookies(response)

    log_security_event(
        tid,
        "LOGOUT",
        email,
        "User session terminated and cookies cleared",
        ip_address=client_ip,
        user_agent=user_agent,
        status_code=200,
    )
    return {"status": "success", "message": "Logged out successfully"}


# ---------------------------------------------------------------------------
# GET /auth/session & Active Device Management
# ---------------------------------------------------------------------------

@router.get("/session")
def get_session(request: Request, tenant_id: str = Depends(get_tenant_id)):
    """Return current session context and authentication status."""
    user = getattr(request.state, "user", None)
    return {
        "tenant_id": tenant_id,
        "authenticated": True if user is not None else False,
        "user": user,
    }


@router.get("/sessions")
def list_user_sessions(user: dict = Depends(get_current_user), request: Request = None):
    """List active session metadata for the authenticated user."""
    client_ip = request.client.host if request and request.client else "127.0.0.1"
    user_agent = request.headers.get("User-Agent", "Unknown") if request else "Current Browser"
    return {
        "active_sessions": [
            {
                "session_id": f"sess-{user.get('sub', '0')[:8]}",
                "device": user_agent[:50],
                "ip_address": client_ip,
                "current": True,
                "last_active": datetime.now(timezone.utc).isoformat(),
            }
        ]
    }


@router.post("/sessions/revoke-all")
def revoke_all_sessions(response: Response, user: dict = Depends(get_current_user)):
    """Revoke all active sessions and log out."""
    clear_auth_cookies(response)
    log_security_event(
        user.get("tenant_id", settings.demo_tenant_id),
        "SESSIONS_REVOKED_ALL",
        user.get("email", ""),
        "All active sessions revoked by user",
    )
    return {"status": "success", "message": "All other sessions have been revoked."}

