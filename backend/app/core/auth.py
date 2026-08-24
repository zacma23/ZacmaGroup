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
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt


def decode_access_token(token: str) -> dict[str, Any] | None:
    """Decode and validate a JWT token. Returns the payload dict or None."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
        if not payload.get("sub"):
            return None
        return payload
    except JWTError:
        return None


# ---------------------------------------------------------------------------
# Password Reset & Verification Tokens
# ---------------------------------------------------------------------------

def create_password_reset_token(email: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    payload = {"sub": email, "type": "password_reset", "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def verify_password_reset_token(token: str) -> str | None:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
        if payload.get("type") != "password_reset":
            return None
        return payload.get("sub")
    except JWTError:
        return None


def create_verification_token(email: str, verify_type: str = "email_verify") -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=24)
    payload = {"sub": email, "type": verify_type, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def verify_verification_token(token: str, verify_type: str = "email_verify") -> str | None:
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
# Audit Logger Helper
# ---------------------------------------------------------------------------

def log_audit_event(
    tenant_id: str,
    action: str,
    resource: str,
    details: str,
    user_email: str = "system",
    ip_address: Optional[str] = None,
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
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
        tenant_id,
    )
