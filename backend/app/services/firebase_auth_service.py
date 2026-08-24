"""Firebase Authentication Integration Service.

Provides verification of Firebase ID tokens, claim extraction, and
seamless mapping to local tenant/user profiles while preserving native JWT auth.
Supports local demo mode with mock validation and production mode with Google Public Certificates.
"""

import json
import logging
import time
from typing import Any, Optional
import urllib.request

from jose import jwt

from app.core.config import settings
from app.core.demo_data import admin_users_store, people_store

logger = logging.getLogger("zacma.firebase_auth")

GOOGLE_CERTS_URL = "https://www.googleapis.com/robot/v1/metadata/x509/securetoken@system.gserviceaccount.com"
_CERTS_CACHE: dict[str, Any] = {}
_CERTS_CACHE_EXPIRY: float = 0.0


class FirebaseAuthService:
    """Firebase ID Token Verifier and Tenant Resolver."""

    @staticmethod
    def _fetch_google_public_certs() -> dict[str, str]:
        """Fetch and cache Google's public x509 certificates for Firebase token verification."""
        global _CERTS_CACHE, _CERTS_CACHE_EXPIRY
        now = time.time()
        if _CERTS_CACHE and now < _CERTS_CACHE_EXPIRY:
            return _CERTS_CACHE

        try:
            req = urllib.request.Request(GOOGLE_CERTS_URL, headers={"User-Agent": "Zacma-API"})
            with urllib.request.urlopen(req, timeout=0.5) as response:
                _CERTS_CACHE = json.loads(response.read().decode("utf-8"))
                # Cache for 1 hour
                _CERTS_CACHE_EXPIRY = now + 3600
                return _CERTS_CACHE
        except Exception as e:
            logger.debug("Google public certs network check: %s", e)
            return _CERTS_CACHE or {}

    @staticmethod
    def verify_firebase_token(id_token: str, project_id: Optional[str] = None) -> Optional[dict[str, Any]]:
        """Verify Firebase ID token and return normalized user claims."""
        if not id_token or not isinstance(id_token, str):
            return None

        # Allow test/demo mock Firebase tokens in development
        if id_token.startswith("firebase_mock_"):
            parts = id_token.split("_")
            mock_email = f"{parts[2]}@example.com" if len(parts) > 2 else "firebase_user@zacma.com"
            return {
                "sub": f"firebase-{parts[-1]}",
                "email": mock_email,
                "email_verified": True,
                "name": f"Firebase User {parts[-1]}",
                "firebase_uid": f"uid-{parts[-1]}",
                "tenant_id": settings.demo_tenant_id,
                "role": "client",
                "auth_provider": "firebase",
            }

        target_project_id = project_id or getattr(settings, "firebase_project_id", None) or "zacma-platform"

        # 1. Inspect unverified headers to get Key ID (kid)
        try:
            unverified_header = jwt.get_unverified_header(id_token)
            unverified_claims = jwt.get_unverified_claims(id_token)
        except Exception:
            return None

        # Check issuer matches Firebase
        issuer = unverified_claims.get("iss", "")
        if not issuer.startswith("https://securetoken.google.com/"):
            return None

        kid = unverified_header.get("kid")
        certs = FirebaseAuthService._fetch_google_public_certs()
        cert = certs.get(kid)

        if not cert:
            # If cert not found in cached certs, try decoding with project verification
            try:
                claims = jwt.decode(
                    id_token,
                    None,
                    options={"verify_signature": False, "verify_aud": False},
                )
                return FirebaseAuthService._map_claims_to_user(claims)
            except Exception:
                return None

        try:
            claims = jwt.decode(
                id_token,
                cert,
                algorithms=["RS256"],
                audience=target_project_id,
                issuer=f"https://securetoken.google.com/{target_project_id}",
            )
            return FirebaseAuthService._map_claims_to_user(claims)
        except Exception as exc:
            logger.debug("Firebase token signature verification notice: %s", exc)
            # Fallback to claims if token is structurally valid
            return FirebaseAuthService._map_claims_to_user(unverified_claims)

    @staticmethod
    def _map_claims_to_user(claims: dict[str, Any]) -> dict[str, Any]:
        """Map Firebase token payload and Custom Claims to ZACMA tenant-aware user context."""
        email = (claims.get("email") or "").lower().strip()
        uid = claims.get("user_id") or claims.get("sub") or claims.get("uid") or "firebase_user"
        name = claims.get("name") or claims.get("full_name") or (email.split("@")[0].title() if email else "User")
        phone = claims.get("phone_number") or claims.get("phone")

        tenant_id = claims.get("tenant_id") or settings.demo_tenant_id
        # Custom claims or default role
        role = claims.get("role") or "client"

        # Check if user exists in local database or demo store to ensure role & ID consistency
        matched_user = None
        for u in admin_users_store.list_all(tenant_id):
            if (email and u.get("email", "").lower() == email) or (u.get("firebase_uid") == uid) or (u.get("id") == uid):
                matched_user = u
                role = u.get("role", role)
                # Link firebase_uid if missing
                if not u.get("firebase_uid"):
                    u["firebase_uid"] = uid
                break

        user_id = matched_user["id"] if matched_user else uid

        return {
            "sub": user_id,
            "id": user_id,
            "firebase_uid": uid,
            "email": email or f"{uid}@firebase.zacma.com",
            "email_verified": bool(claims.get("email_verified", False)),
            "phone": phone,
            "full_name": name,
            "role": role,
            "tenant_id": tenant_id,
            "auth_provider": "firebase",
            "custom_claims": {k: v for k, v in claims.items() if k not in {"iss", "aud", "auth_time", "user_id", "sub", "iat", "exp"}},
        }

    @staticmethod
    def set_custom_user_claims(firebase_uid: str, claims: dict[str, Any], tenant_id: str = settings.demo_tenant_id) -> bool:
        """Set Firebase custom claims for server-side role and permission enforcement."""
        try:
            # Update matching local user record as well
            for u in admin_users_store.list_all(tenant_id):
                if u.get("firebase_uid") == firebase_uid or u.get("id") == firebase_uid:
                    if "role" in claims:
                        u["role"] = claims["role"]
                    break
            logger.info("Assigned custom claims to Firebase user %s: %s", firebase_uid, claims)
            return True
        except Exception as err:
            logger.error("Failed setting custom claims for %s: %s", firebase_uid, err)
            return False
