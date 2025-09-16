"""add indexes and updated_at fields

Revision ID: 0002_prod_order_idx
Revises: 0001_initial_authz
Create Date: 2025-09-14
"""
from __future__ import annotations
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = '0002_prod_order_idx'
down_revision = '0001_initial_authz'
branch_labels = None
depends_on = None

def upgrade():
    bind = op.get_bind()
    insp = inspect(bind)

    if not insp.has_table('products'):
        op.create_table('products',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('name', sa.String(length=128), nullable=False),
            sa.Column('sku', sa.String(length=64), nullable=False, unique=True),
            sa.Column('branch_id', sa.Integer(), nullable=False),
            sa.Column('quantity', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('description_i18n', sa.JSON(), nullable=True),
            sa.Column('created_by', sa.Integer(), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'))
        )
    # Add updated_at if table pre-existed without it
    if 'products' in insp.get_table_names():
        cols = [c['name'] for c in insp.get_columns('products')]
        if 'updated_at' not in cols:
            op.add_column('products', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')))
    # Indexes (create if missing)
    existing_indexes = {ix['name'] for ix in insp.get_indexes('products')}
    if 'ix_products_name' not in existing_indexes:
        op.create_index('ix_products_name', 'products', ['name'])
    if 'ix_products_sku' not in existing_indexes:
        op.create_index('ix_products_sku', 'products', ['sku'])
    if 'ix_products_branch' not in existing_indexes:
        op.create_index('ix_products_branch', 'products', ['branch_id'])

    if not insp.has_table('orders'):
        op.create_table('orders',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('branch_id', sa.Integer(), nullable=False),
            sa.Column('customer_name', sa.String(length=128), nullable=False),
            sa.Column('total_cents', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('status', sa.String(length=32), nullable=False, server_default='NEW'),
            sa.Column('created_by', sa.Integer(), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'))
        )
    if 'orders' in insp.get_table_names():
        cols = [c['name'] for c in insp.get_columns('orders')]
        if 'updated_at' not in cols:
            op.add_column('orders', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')))
    existing_indexes = {ix['name'] for ix in insp.get_indexes('orders')} if insp.has_table('orders') else set()
    if 'ix_orders_branch' not in existing_indexes:
        op.create_index('ix_orders_branch', 'orders', ['branch_id'])
    if 'ix_orders_customer_name' not in existing_indexes:
        op.create_index('ix_orders_customer_name', 'orders', ['customer_name'])

def downgrade():
    # Best effort: drop indexes & columns we added (keep base tables if they pre-existed)
    bind = op.get_bind()
    insp = inspect(bind)
    if insp.has_table('orders'):
        for ix in ['ix_orders_customer_name','ix_orders_branch']:
            try:
                op.drop_index(ix, table_name='orders')
            except Exception:
                pass
        try:
            op.drop_column('orders', 'updated_at')
        except Exception:
            pass
    if insp.has_table('products'):
        for ix in ['ix_products_name','ix_products_sku','ix_products_branch']:
            try:
                op.drop_index(ix, table_name='products')
            except Exception:
                pass
        try:
            op.drop_column('products', 'updated_at')
        except Exception:
            pass