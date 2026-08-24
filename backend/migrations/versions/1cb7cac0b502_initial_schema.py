"""initial_schema

Revision ID: 1cb7cac0b502
Revises: 
Create Date: 2026-08-23 09:34:15.818899

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1cb7cac0b502'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


import os
from pathlib import Path

def upgrade() -> None:
    """Upgrade schema."""
    # Run the original proposal SQL
    repo_root = Path(__file__).resolve().parents[3]
    sql_file = repo_root / "0001_create_rag_schema.sql"
    with open(sql_file, "r") as f:
        sql = f.read()
    
    op.execute(sa.text(sql))
    
    # Add RBAC tables
    op.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS public.roles (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name TEXT UNIQUE NOT NULL,
            description TEXT
        );

        CREATE TABLE IF NOT EXISTS public.permissions (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            resource TEXT NOT NULL,
            action TEXT NOT NULL,
            UNIQUE (resource, action)
        );

        CREATE TABLE IF NOT EXISTS public.role_permissions (
            role_id UUID REFERENCES public.roles(id) ON DELETE CASCADE,
            permission_id UUID REFERENCES public.permissions(id) ON DELETE CASCADE,
            PRIMARY KEY (role_id, permission_id)
        );

        CREATE TABLE IF NOT EXISTS public.user_roles (
            user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
            role_id UUID REFERENCES public.roles(id) ON DELETE CASCADE,
            PRIMARY KEY (user_id, role_id)
        );
    """))


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(sa.text("DROP TABLE IF EXISTS public.user_roles CASCADE;"))
    op.execute(sa.text("DROP TABLE IF EXISTS public.role_permissions CASCADE;"))
    op.execute(sa.text("DROP TABLE IF EXISTS public.permissions CASCADE;"))
    op.execute(sa.text("DROP TABLE IF EXISTS public.roles CASCADE;"))
    
    op.execute(sa.text("DROP SCHEMA IF EXISTS admin CASCADE;"))
    op.execute(sa.text("DROP SCHEMA IF EXISTS ai CASCADE;"))
    op.execute(sa.text("DROP SCHEMA IF EXISTS audit CASCADE;"))
    op.execute(sa.text("DROP SCHEMA IF EXISTS rag CASCADE;"))
    op.execute(sa.text("DROP TABLE IF EXISTS public.users CASCADE;"))
    op.execute(sa.text("DROP TABLE IF EXISTS public.tenants CASCADE;"))
