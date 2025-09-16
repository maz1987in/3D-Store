"""add updated_at to authz entities

Revision ID: 0003_authz_updated_at
Revises: 0002_prod_order_idx
Create Date: 2025-09-15
"""
from __future__ import annotations
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = '0003_authz_updated_at'
down_revision = '0002_prod_order_idx'
branch_labels = None
depends_on = None

def upgrade():
    bind = op.get_bind(); insp = inspect(bind)
    for table in ['roles','groups','users']:
        if insp.has_table(table):
            cols = [c['name'] for c in insp.get_columns(table)]
            if 'updated_at' not in cols:
                op.add_column(table, sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')))

def downgrade():
    bind = op.get_bind(); insp = inspect(bind)
    for table in ['roles','groups','users']:
        if insp.has_table(table):
            try:
                op.drop_column(table, 'updated_at')
            except Exception:
                pass