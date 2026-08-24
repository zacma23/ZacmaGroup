"""HTTP middleware stack for the ZACMA Platform API.

AuthMiddleware — extracts and validates JWT Bearer tokens, populates
``request.state.user`` for downstream route handlers.

AuditLoggingMiddleware — logs every request with tenant/user context and
processing time.
"""

import logging
import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.auth import decode_access_token, is_token_revoked
from app.core.config import settings

logger = logging.getLogger("zacma.api")

# Paths that should never require authentication
PUBLIC_PATHS = {"/health", "/docs", "/openapi.json", "/redoc"}


class AuthMiddleware(BaseHTTPMiddleware):
    """Extract Bearer JWT or HttpOnly session cookie, validate revocation, and populate request.state.user."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Always initialise user state so downstream code never gets AttributeError
        request.state.user = None

        token = None
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1].strip()
        elif request.cookies.get(settings.session_cookie_name):
            token = request.cookies.get(settings.session_cookie_name)
        elif request.cookies.get("zacma_session"):
            token = request.cookies.get("zacma_session")

        if token and not is_token_revoked(token):
            payload = decode_access_token(token)
            if payload:
                request.state.user = payload
            else:
                # Fallback to Firebase Authentication ID token verification
                try:
                    from app.services.firebase_auth_service import FirebaseAuthService
                    fb_user = FirebaseAuthService.verify_firebase_token(token)
                    if fb_user:
                        request.state.user = fb_user
                except Exception as fb_err:
                    logger.debug("Firebase auth fallback check skipped: %s", fb_err)

        response = await call_next(request)

        # Apply security headers & cache-control for protected endpoints
        path = request.url.path
        if not any(path.startswith(p) for p in PUBLIC_PATHS):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response.headers["Pragma"] = "no-cache"
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"

        return response


class AuditLoggingMiddleware(BaseHTTPMiddleware):
    """Log method, path, status, tenant, user, and processing time for every request."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        response = await call_next(request)

        process_time = time.time() - start_time

        user_id = "anonymous"
        tenant_id = "none"
        user = getattr(request.state, "user", None)
        if isinstance(user, dict):
            user_id = user.get("sub", "unknown")
            tenant_id = user.get("tenant_id", "unknown")

        logger.info(
            "%s %s - status: %s - tenant: %s - user: %s - time: %.4fs",
            request.method,
            request.url.path,
            response.status_code,
            tenant_id,
            user_id,
            process_time,
        )

        return response
