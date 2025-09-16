"""add updated_at to permissions

Revision ID: 0004_permission_updated_at
Revises: 0003_authz_updated_at
Create Date: 2025-09-15
"""
from __future__ import annotations
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = '0004_permission_updated_at'
down_revision = '0003_authz_updated_at'
branch_labels = None
depends_on = None

def upgrade():
    bind = op.get_bind(); insp = inspect(bind)
    if insp.has_table('permissions'):
        cols = [c['name'] for c in insp.get_columns('permissions')]
        if 'updated_at' not in cols:
            op.add_column('permissions', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')))

def downgrade():
    bind = op.get_bind(); insp = inspect(bind)
    if insp.has_table('permissions'):
        try:
            op.drop_column('permissions', 'updated_at')
        except Exception:
            pass