"""Optional Supabase client setup.

The client stays disabled until an actual service key is configured. That keeps
the local demo functional and prevents accidental requests to a default
endpoint with placeholder credentials.
"""

from typing import Any

from supabase import Client, create_client

from app.core.config import settings


def _has_service_key(value: str) -> bool:
    return bool(value and value.strip() not in {"replace-me", "changeme"})


def create_supabase_client() -> Client | None:
    if not _has_service_key(settings.supabase_service_key):
        return None
    return create_client(settings.supabase_url, settings.supabase_service_key)


supabase: Client | None = create_supabase_client()


def database_status() -> dict[str, Any]:
    return {
        "configured": supabase is not None,
        "provider": "supabase",
    }
