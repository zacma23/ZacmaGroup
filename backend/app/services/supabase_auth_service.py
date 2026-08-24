"""Supabase Authentication and Database Role-Based Access Control (RBAC) Service.

Provides server-side Supabase authentication, JWT validation, database-backed role verification
(via public.profiles), and transparent fallback to demo data mode when Supabase is not configured.
"""

from datetime import datetime, timezone, timedelta
import logging
from typing import Any, Optional
from fastapi import HTTPException, status
from jose import jwt, JWTError

from app.core.config import settings
from app.core.db import supabase
from app.core.demo_data import admin_users_store, people_store
from app.core.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
)

logger = logging.getLogger("zacma.supabase_auth")


class SupabaseAuthService:
    """Service handling Supabase Authentication and database role verification."""

    @classmethod
    def is_configured(cls) -> bool:
        """Return True if Supabase client is initialized and operational."""
        return supabase is not None

    @classmethod
    def ensure_admin_account(cls) -> None:
        """Ensure the root administrator account exists with role 'admin' in Supabase/database."""
        if not cls.is_configured():
            return

        admin_email = settings.admin_username.lower().strip()
        admin_pass = settings.admin_password
        tenant_id = settings.demo_tenant_id

        try:
            # Check if profile exists in public.profiles
            res = supabase.table("profiles").select("*").eq("email", admin_email).execute()
            if res.data and len(res.data) > 0:
                profile = res.data[0]
                if profile.get("role") != "admin":
                    supabase.table("profiles").update({"role": "admin", "status": "active"}).eq("id", profile["id"]).execute()
                return

            # Check if user exists in auth.users via admin API
            try:
                auth_user = supabase.auth.admin.create_user({
                    "email": admin_email,
                    "password": admin_pass,
                    "email_confirm": True,
                    "user_metadata": {
                        "full_name": "Zacma Administrator",
                        "role": "admin",
                        "tenant_id": tenant_id,
                    }
                })
                user_id = auth_user.user.id if auth_user and hasattr(auth_user, "user") else "00000000-0000-0000-0000-000000000002"
            except Exception:
                user_id = "00000000-0000-0000-0000-000000000002"

            # Insert profile in public.profiles table
            supabase.table("profiles").upsert({
                "id": user_id,
                "tenant_id": tenant_id,
                "email": admin_email,
                "full_name": "Zacma Administrator",
                "role": "admin",
                "status": "active",
            }).execute()
            logger.info("Provisioned root administrator profile (%s) in Supabase", admin_email)
        except Exception as e:
            logger.debug("ensure_admin_account notice: %s", e)

    @classmethod
    def authenticate(
        cls,
        email: str,
        password: str,
        remember_me: bool = False,
    ) -> dict[str, Any]:
        """Authenticate user with Supabase Auth or database verification, returning claims and tokens."""
        clean_email = email.strip().lower()
        admin_user = settings.admin_username.strip().lower()

        # 1. Administrator Authentication (with database-backed role verification)
        if clean_email == admin_user:
            if not password or (password != settings.admin_password and not verify_password(password, settings.admin_password)):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password",
                )

            user_id = "usr-admin-root"
            role = "admin"
            full_name = "Zacma Administrator"
            tenant_id = settings.demo_tenant_id

            if cls.is_configured():
                try:
                    res = supabase.table("profiles").select("*").eq("email", admin_user).execute()
                    if res.data:
                        profile = res.data[0]
                        user_id = profile.get("id", user_id)
                        role = profile.get("role", "admin")
                        full_name = profile.get("full_name", full_name)
                        tenant_id = profile.get("tenant_id", tenant_id)
                except Exception as e:
                    logger.debug("Database profile lookup error for admin: %s", e)

            expire_delta = timedelta(days=7) if remember_me else timedelta(minutes=settings.jwt_expire_minutes)
            token = create_access_token(
                {
                    "sub": user_id,
                    "email": admin_user,
                    "role": role,
                    "tenant_id": tenant_id,
                    "full_name": full_name,
                    "firebase_uid": "uid-admin-root",
                },
                expires_delta=expire_delta,
            )

            return {
                "access_token": token,
                "role": role,
                "tenant_id": tenant_id,
                "email": admin_user,
                "full_name": full_name,
                "user_id": user_id,
            }

        # 2. Registered Users Authentication via Supabase Auth & Database Profiles
        if cls.is_configured():
            try:
                # Attempt GoTrue password authentication
                auth_res = supabase.auth.sign_in_with_password({
                    "email": clean_email,
                    "password": password,
                })
                auth_user = auth_res.user if hasattr(auth_res, "user") else None
                if auth_user:
                    user_id = auth_user.id
                    # Retrieve database-verified profile from public.profiles
                    profile = None
                    try:
                        p_res = supabase.table("profiles").select("*").eq("id", user_id).execute()
                        if p_res.data:
                            profile = p_res.data[0]
                    except Exception:
                        pass

                    if not profile:
                        try:
                            p_res = supabase.table("users").select("*").eq("id", user_id).execute()
                            if p_res.data:
                                profile = p_res.data[0]
                        except Exception:
                            pass

                    role = profile.get("role", "client") if profile else "client"
                    full_name = profile.get("full_name", "") if profile else (auth_user.user_metadata or {}).get("full_name", clean_email.split("@")[0].title())
                    tenant_id = profile.get("tenant_id", settings.demo_tenant_id) if profile else settings.demo_tenant_id
                    user_status = profile.get("status", "active") if profile else "active"

                    if user_status != "active":
                        raise HTTPException(status_code=403, detail="Account is suspended or inactive")

                    expire_delta = timedelta(days=7) if remember_me else timedelta(minutes=settings.jwt_expire_minutes)
                    token = getattr(auth_res.session, "access_token", None) or create_access_token(
                        {
                            "sub": user_id,
                            "email": clean_email,
                            "role": role,
                            "tenant_id": tenant_id,
                            "full_name": full_name,
                        },
                        expires_delta=expire_delta,
                    )

                    return {
                        "access_token": token,
                        "role": role,
                        "tenant_id": tenant_id,
                        "email": clean_email,
                        "full_name": full_name,
                        "user_id": user_id,
                    }
            except HTTPException:
                raise
            except Exception as auth_err:
                logger.debug("Supabase GoTrue sign_in fallback check: %s", auth_err)

            # Fallback: check stored password hash in database table (profiles/users)
            try:
                tbl_res = supabase.table("users").select("*").eq("email", clean_email).execute()
                if tbl_res.data:
                    user = tbl_res.data[0]
                    stored_hash = user.get("password_hash", "")
                    if stored_hash and verify_password(password, stored_hash):
                        if user.get("status") != "active":
                            raise HTTPException(status_code=403, detail="Account is suspended or inactive")

                        expire_delta = timedelta(days=7) if remember_me else timedelta(minutes=settings.jwt_expire_minutes)
                        token = create_access_token(
                            {
                                "sub": user["id"],
                                "email": user["email"],
                                "role": user.get("role", "client"),
                                "tenant_id": user.get("tenant_id", settings.demo_tenant_id),
                                "full_name": user.get("full_name", ""),
                            },
                            expires_delta=expire_delta,
                        )
                        return {
                            "access_token": token,
                            "role": user.get("role", "client"),
                            "tenant_id": user.get("tenant_id", settings.demo_tenant_id),
                            "email": user["email"],
                            "full_name": user.get("full_name", ""),
                            "user_id": user["id"],
                        }
            except HTTPException:
                raise
            except Exception as db_err:
                logger.debug("Database table auth check: %s", db_err)

            raise HTTPException(status_code=401, detail="Invalid email or password")

        # 3. Fallback to Demo Data Store (Development Mode)
        demo_users = admin_users_store.list_all(settings.demo_tenant_id)
        matched = next(
            (
                u for u in demo_users
                if u["email"].lower() == clean_email
                or u.get("phone", "") == clean_email
                or u.get("firebase_uid", "") == clean_email
            ),
            None,
        )

        if matched and "password_hash" in matched:
            if not verify_password(password, matched["password_hash"]):
                raise HTTPException(status_code=401, detail="Invalid email or password")

        role = matched["role"] if matched else "client"
        full_name = matched["full_name"] if matched else clean_email.split("@")[0].title()
        user_id = matched["id"] if matched else f"usr-{abs(hash(clean_email)) % 100000}"
        email_val = matched["email"] if matched else clean_email
        firebase_uid = matched.get("firebase_uid") if matched else f"uid-{abs(hash(clean_email)) % 100000}"

        expire_delta = timedelta(days=7) if remember_me else timedelta(minutes=settings.jwt_expire_minutes)
        token = create_access_token(
            {
                "sub": user_id,
                "email": email_val,
                "role": role,
                "tenant_id": settings.demo_tenant_id,
                "full_name": full_name,
                "firebase_uid": firebase_uid,
            },
            expires_delta=expire_delta,
        )

        return {
            "access_token": token,
            "role": role,
            "tenant_id": settings.demo_tenant_id,
            "email": email_val,
            "full_name": full_name,
            "user_id": user_id,
        }

    @classmethod
    def register(
        cls,
        email: str,
        password: str,
        full_name: str,
        phone: Optional[str] = None,
        address: Optional[str] = None,
        education_level: Optional[str] = None,
        role: str = "client",
        tenant_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """Register a new user account into Supabase Auth and database profiles table."""
        clean_email = email.strip().lower()
        target_tenant_id = tenant_id or settings.demo_tenant_id

        # Privilege escalation defense: ensure newly registered accounts cannot claim admin roles
        assigned_role = "client" if role not in ["client", "student"] else role

        if cls.is_configured():
            # Check existing in Supabase
            try:
                existing = supabase.table("profiles").select("id").eq("email", clean_email).execute()
                if existing.data and len(existing.data) > 0:
                    raise HTTPException(status_code=409, detail="Email is already registered")
            except HTTPException:
                raise
            except Exception:
                pass

            user_id = f"usr-{abs(hash(clean_email)) % 1000000}"
            # Attempt to create in Supabase Auth
            try:
                auth_res = supabase.auth.sign_up({
                    "email": clean_email,
                    "password": password,
                    "options": {
                        "data": {
                            "full_name": full_name,
                            "phone": phone,
                            "role": assigned_role,
                            "tenant_id": target_tenant_id,
                        }
                    }
                })
                if auth_res and hasattr(auth_res, "user") and auth_res.user:
                    user_id = auth_res.user.id
            except Exception as err:
                logger.debug("Supabase sign_up exception: %s", err)

            # Insert/upsert profile in public.profiles table
            pw_hash = get_password_hash(password)
            try:
                supabase.table("profiles").upsert({
                    "id": user_id,
                    "tenant_id": target_tenant_id,
                    "email": clean_email,
                    "full_name": full_name,
                    "phone": phone,
                    "role": assigned_role,
                    "status": "active",
                    "metadata": {
                        "address": address,
                        "education_level": education_level,
                    },
                }).execute()
            except Exception as p_err:
                logger.debug("Supabase profiles table upsert: %s", p_err)
                # Fallback to users table
                try:
                    supabase.table("users").insert({
                        "id": user_id,
                        "tenant_id": target_tenant_id,
                        "email": clean_email,
                        "full_name": full_name,
                        "phone": phone,
                        "password_hash": pw_hash,
                        "role": assigned_role,
                        "status": "active",
                    }).execute()
                except Exception:
                    pass

            token = create_access_token(
                {
                    "sub": user_id,
                    "email": clean_email,
                    "role": assigned_role,
                    "tenant_id": target_tenant_id,
                    "full_name": full_name,
                }
            )

            return {
                "access_token": token,
                "role": assigned_role,
                "tenant_id": target_tenant_id,
                "email": clean_email,
                "full_name": full_name,
                "user_id": user_id,
            }

        # Fallback to Demo Data Store
        existing = admin_users_store.list_all(target_tenant_id)
        if any(u["email"].lower() == clean_email for u in existing):
            raise HTTPException(status_code=409, detail="Email is already registered")

        pw_hash = get_password_hash(password)
        firebase_uid = f"uid-{abs(hash(clean_email)) % 100000}"
        new_user = {
            "id": f"usr-{abs(hash(clean_email)) % 100000}",
            "tenant_id": target_tenant_id,
            "email": clean_email,
            "full_name": full_name,
            "phone": phone,
            "address": address,
            "education_level": education_level,
            "role": assigned_role,
            "password_hash": pw_hash,
            "firebase_uid": firebase_uid,
            "status": "active",
            "is_verified": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        admin_users_store.create(new_user, target_tenant_id)

        # Register in CRM People Store
        people_store.create(
            {
                "id": f"contact-{abs(hash(clean_email)) % 100000}",
                "tenant_id": target_tenant_id,
                "name": full_name,
                "email": clean_email,
                "phone": phone or "",
                "role": assigned_role,
                "status": "Active",
                "type": "Client",
                "address": address or "",
                "education": education_level or "Diploma",
                "created_at": datetime.now(timezone.utc).isoformat(),
            },
            target_tenant_id,
        )

        token = create_access_token(
            {
                "sub": new_user["id"],
                "email": clean_email,
                "role": assigned_role,
                "tenant_id": target_tenant_id,
                "full_name": full_name,
                "firebase_uid": firebase_uid,
            }
        )

        return {
            "access_token": token,
            "role": assigned_role,
            "tenant_id": target_tenant_id,
            "email": clean_email,
            "full_name": full_name,
            "user_id": new_user["id"],
        }

    @classmethod
    def verify_supabase_token(cls, token: str) -> Optional[dict[str, Any]]:
        """Validate Supabase JWT and return authenticated claims with database-verified role."""
        if not token or not isinstance(token, str):
            return None

        # 1. Check if token can be validated via Supabase GoTrue Auth
        if cls.is_configured():
            try:
                res = supabase.auth.get_user(token)
                if res and hasattr(res, "user") and res.user:
                    user = res.user
                    user_id = user.id
                    email = user.email

                    # Query database public.profiles for role verification
                    role = "client"
                    full_name = ""
                    tenant_id = settings.demo_tenant_id
                    status_val = "active"

                    try:
                        p_res = supabase.table("profiles").select("*").eq("id", user_id).execute()
                        if p_res.data:
                            p = p_res.data[0]
                            role = p.get("role", role)
                            full_name = p.get("full_name", full_name)
                            tenant_id = p.get("tenant_id", tenant_id)
                            status_val = p.get("status", status_val)
                    except Exception:
                        pass

                    if status_val != "active":
                        return None

                    return {
                        "sub": user_id,
                        "email": email,
                        "role": role,
                        "tenant_id": tenant_id,
                        "full_name": full_name,
                        "auth_provider": "supabase",
                    }
            except Exception as e:
                logger.debug("Supabase get_user token check: %s", e)

        # 2. Check decoding if Supabase JWT secret is configured
        supabase_secret = getattr(settings, "supabase_jwt_secret", "") or settings.secret_key
        try:
            payload = jwt.decode(token, supabase_secret, algorithms=["HS256"])
            sub = payload.get("sub")
            if sub:
                email = payload.get("email", "")
                role = payload.get("role", "authenticated")
                # Normalize Supabase default 'authenticated' role to profile role
                if role in ["authenticated", "anon"]:
                    role = payload.get("user_metadata", {}).get("role", "client")

                return {
                    "sub": sub,
                    "email": email,
                    "role": role,
                    "tenant_id": payload.get("tenant_id", settings.demo_tenant_id),
                    "full_name": payload.get("user_metadata", {}).get("full_name", ""),
                    "auth_provider": "supabase",
                }
        except JWTError:
            pass

        return None
