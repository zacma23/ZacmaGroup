"""Core authentication utilities and FastAPI dependencies.

Provides password hashing (bcrypt), JWT creation/decoding, brute-force rate limiting,
password reset token handling, and audit event logging.
"""

from collections import defaultdict
from datetime import datetime, timedelta, timezone
import time
from typing import Any, Optional

from fastapi import HTTPException, Request, status
from passlib.context import CryptContext
from jose import JWTError, jwt

from app.core.config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ---------------------------------------------------------------------------
# Brute-force Login Protection & Rate Limiting
# ---------------------------------------------------------------------------

class LoginAttemptTracker:
    """Sliding-window in-memory tracker for failed login attempts."""

    def __init__(self, max_attempts: int = 5, window_seconds: int = 300, lockout_seconds: int = 600):
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        self.lockout_seconds = lockout_seconds
        self._attempts: dict[str, list[float]] = defaultdict(list)
        self._lockouts: dict[str, float] = {}

    def is_locked(self, identifier: str) -> tuple[bool, int]:
        now = time.time()
        # Check explicit lockout
        if identifier in self._lockouts:
            remaining = int(self._lockouts[identifier] - now)
            if remaining > 0:
                return True, remaining
            del self._lockouts[identifier]

        # Clean old attempts
        self._attempts[identifier] = [t for t in self._attempts[identifier] if now - t < self.window_seconds]
        if len(self._attempts[identifier]) >= self.max_attempts:
            self._lockouts[identifier] = now + self.lockout_seconds
            return True, self.lockout_seconds

        return False, 0

    def record_failure(self, identifier: str):
        now = time.time()
        self._attempts[identifier].append(now)
        if len(self._attempts[identifier]) >= self.max_attempts:
            self._lockouts[identifier] = now + self.lockout_seconds

    def record_success(self, identifier: str):
        self._attempts.pop(identifier, None)
        self._lockouts.pop(identifier, None)


login_tracker = LoginAttemptTracker()


import bcrypt

# ---------------------------------------------------------------------------
# Password Management
# ---------------------------------------------------------------------------

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a stored hash."""
    if not hashed_password:
        return False
    try:
        if hashed_password.startswith("$2b$") or hashed_password.startswith("$2a$"):
            return bcrypt.checkpw(
                plain_password.encode("utf-8")[:72],
                hashed_password.encode("utf-8"),
            )
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8")[:72], salt).decode("utf-8")



# ---------------------------------------------------------------------------
# JWT Access Tokens
# ---------------------------------------------------------------------------

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "jti": secrets.token_hex(16),
    })
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt


def decode_access_token(token: str) -> dict[str, Any] | None:
    """Decode and validate a JWT token. Returns the payload dict or None."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
        if payload.get("sub"):
            return payload
    except JWTError:
        pass

    # Validate against Supabase Authentication & Database Profiles if available
    try:
        from app.services.supabase_auth_service import SupabaseAuthService
        sb_user = SupabaseAuthService.verify_supabase_token(token)
        if sb_user:
            return sb_user
    except Exception:
        pass

    return None

# ---------------------------------------------------------------------------
# Phone / SMS OTP Verification Tracker (Secure Hashing, Expiry, Rate Limiting)
# ---------------------------------------------------------------------------

import hashlib
import secrets


class PhoneOtpTracker:
    """Secure in-memory OTP verification tracker with rate limiting and salted hashing."""

    def __init__(self, expiry_seconds: int = 300, max_attempts: int = 3):
        self.expiry_seconds = expiry_seconds
        self.max_attempts = max_attempts
        self._otps: dict[str, dict[str, Any]] = {}

    def _hash_otp(self, phone: str, otp: str, salt: str) -> str:
        return hashlib.sha256(f"{phone}:{otp}:{salt}:{settings.secret_key}".encode("utf-8")).hexdigest()

    def generate_otp(self, phone: str) -> tuple[str, str]:
        """Generate a 6-digit numeric OTP and return (plain_otp, salt). Only returns plain for sending."""
        now = time.time()
        # Clean expired
        if phone in self._otps and now > self._otps[phone]["expires_at"]:
            del self._otps[phone]

        # Rate check
        if phone in self._otps:
            last_req = self._otps[phone].get("created_at", 0)
            if now - last_req < 30:  # 30 seconds cooldown
                raise ValueError("Please wait 30 seconds before requesting a new OTP.")

        plain_otp = f"{secrets.randbelow(900000) + 100000}"
        salt = secrets.token_hex(8)
        hashed = self._hash_otp(phone, plain_otp, salt)

        self._otps[phone] = {
            "hash": hashed,
            "salt": salt,
            "created_at": now,
            "expires_at": now + self.expiry_seconds,
            "attempts": 0,
        }
        return plain_otp, salt

    def verify_otp(self, phone: str, submitted_otp: str) -> bool:
        """Verify submitted OTP against salted hash. Never stores or logs plaintext."""
        now = time.time()
        record = self._otps.get(phone)
        if not record:
            return False

        if now > record["expires_at"]:
            del self._otps[phone]
            return False

        record["attempts"] += 1
        if record["attempts"] > self.max_attempts:
            del self._otps[phone]
            return False

        expected_hash = record["hash"]
        actual_hash = self._hash_otp(phone, submitted_otp.strip(), record["salt"])

        if secrets.compare_digest(expected_hash, actual_hash):
            del self._otps[phone]
            return True
        return False


phone_otp_tracker = PhoneOtpTracker()


# ---------------------------------------------------------------------------
# Session Cookie Utilities
# ---------------------------------------------------------------------------

from fastapi import Response


def set_auth_cookies(response: Response, token: str, remember_me: bool = False):
    """Set secure HttpOnly authentication cookie on response."""
    max_age = 7 * 24 * 3600 if remember_me else settings.jwt_expire_minutes * 60
    response.set_cookie(
        key=settings.session_cookie_name,
        value=token,
        max_age=max_age,
        expires=max_age,
        path="/",
        secure=settings.session_cookie_secure,
        httponly=settings.session_cookie_httponly,
        samesite=settings.session_cookie_samesite,
    )


def clear_auth_cookies(response: Response):
    """Clear session authentication cookies."""
    response.delete_cookie(
        key=settings.session_cookie_name,
        path="/",
        secure=settings.session_cookie_secure,
        httponly=settings.session_cookie_httponly,
        samesite=settings.session_cookie_samesite,
    )
    # Also delete legacy helper cookies if present
    response.delete_cookie(key="zacma_user_role", path="/")
    response.delete_cookie(key="zacma_user_email", path="/")


# ---------------------------------------------------------------------------
# Token Revocation & Session Registry
# ---------------------------------------------------------------------------

_REVOKED_TOKENS: set[str] = set()


def revoke_token(token: str):
    """Add a JWT token or session ID to the revoked tokens set."""
    if token:
        _REVOKED_TOKENS.add(token)


def is_token_revoked(token: str) -> bool:
    """Check whether a token has been explicitly revoked upon logout."""
    return token in _REVOKED_TOKENS


# ---------------------------------------------------------------------------
# Password Reset & Verification Tokens
# ---------------------------------------------------------------------------

def create_password_reset_token(email: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    payload = {"sub": email, "type": "password_reset", "exp": expire, "jti": secrets.token_hex(8)}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def verify_password_reset_token(token: str) -> str | None:
    if is_token_revoked(token):
        return None
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
        if payload.get("type") != "password_reset":
            return None
        return payload.get("sub")
    except JWTError:
        return None


def create_verification_token(email: str, verify_type: str = "email_verify") -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=24)
    payload = {"sub": email, "type": verify_type, "exp": expire, "jti": secrets.token_hex(8)}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def verify_verification_token(token: str, verify_type: str = "email_verify") -> str | None:
    if is_token_revoked(token):
        return None
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
        if payload.get("type") != verify_type:
            return None
        return payload.get("sub")
    except JWTError:
        return None


# ---------------------------------------------------------------------------
# Current User Dependency
# ---------------------------------------------------------------------------

def get_current_user(request: Request) -> dict[str, Any]:
    """FastAPI dependency: require an authenticated user."""
    user = getattr(request.state, "user", None)
    if not user or not isinstance(user, dict):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


# ---------------------------------------------------------------------------
# Audit & Security Event Logger Helper
# ---------------------------------------------------------------------------

def log_audit_event(
    tenant_id: str,
    action: str,
    resource: str,
    details: str,
    user_email: str = "system",
    ip_address: Optional[str] = None,
    status_str: str = "SUCCESS",
):
    """Record an audit trail event into the demo store or database."""
    from app.core.demo_data import audit_logs_store
    audit_logs_store.create(
        {
            "action": action,
            "resource": resource,
            "details": details,
            "user_email": user_email,
            "ip_address": ip_address or "127.0.0.1",
            "status": status_str,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
        tenant_id,
    )


def log_security_event(
    tenant_id: str,
    event_type: str,
    actor: str,
    details: str,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    status_code: int = 200,
):
    """Structured security monitoring logger for compliance and audit defense."""
    log_audit_event(
        tenant_id=tenant_id,
        action=event_type,
        resource="auth/security",
        details=f"{details} (agent: {user_agent or 'unknown'})",
        user_email=actor,
        ip_address=ip_address,
        status_str="SUCCESS" if status_code < 400 else "FAILURE",
    )
