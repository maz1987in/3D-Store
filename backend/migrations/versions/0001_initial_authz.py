"""initial authz tables

Revision ID: 0001_initial_authz
Revises: 
Create Date: 2025-09-14
"""
from __future__ import annotations
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = '0001_initial_authz'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Use batch for SQLite compatibility for unique constraints
    op.create_table('permissions',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('code', sa.String(length=64), nullable=False, unique=True),
        sa.Column('service', sa.String(length=32), nullable=False),
        sa.Column('action', sa.String(length=32), nullable=False),
        sa.Column('description_i18n', sa.JSON(), nullable=True)
    )
    op.create_index('ix_permissions_code', 'permissions', ['code'])
    op.create_index('ix_permissions_service', 'permissions', ['service'])

    op.create_table('roles',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=64), nullable=False, unique=True),
        sa.Column('is_system', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('description_i18n', sa.JSON(), nullable=True)
    )

    op.create_table('groups',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=64), nullable=False, unique=True),
        sa.Column('description_i18n', sa.JSON(), nullable=True),
        sa.Column('branch_scope', sa.JSON(), nullable=True)
    )

    op.create_table('users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('email', sa.String(length=128), nullable=False, unique=True),
        sa.Column('phone', sa.String(length=32)),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.Column('locale', sa.String(length=8), nullable=False, server_default='en'),
        sa.Column('tz', sa.String(length=64), nullable=False, server_default='Asia/Muscat')
    )
    op.create_index('ix_users_email', 'users', ['email'])

    op.create_table('role_permissions',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('role_id', sa.Integer(), sa.ForeignKey('roles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('permission_id', sa.Integer(), sa.ForeignKey('permissions.id', ondelete='CASCADE'), nullable=False)
    )
    # unique constraint handled via batch for sqlite
    with op.batch_alter_table('role_permissions') as batch_op:
        batch_op.create_unique_constraint('uq_role_permission', ['role_id', 'permission_id'])

    op.create_table('group_roles',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('group_id', sa.Integer(), sa.ForeignKey('groups.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role_id', sa.Integer(), sa.ForeignKey('roles.id', ondelete='CASCADE'), nullable=False)
    )
    with op.batch_alter_table('group_roles') as batch_op:
        batch_op.create_unique_constraint('uq_group_role', ['group_id', 'role_id'])

    op.create_table('user_groups',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('group_id', sa.Integer(), sa.ForeignKey('groups.id', ondelete='CASCADE'), nullable=False)
    )
    with op.batch_alter_table('user_groups') as batch_op:
        batch_op.create_unique_constraint('uq_user_group', ['user_id', 'group_id'])

    op.create_table('user_roles',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role_id', sa.Integer(), sa.ForeignKey('roles.id', ondelete='CASCADE'), nullable=False)
    )
    with op.batch_alter_table('user_roles') as batch_op:
        batch_op.create_unique_constraint('uq_user_role', ['user_id', 'role_id'])

    op.create_table('audit_logs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('actor_user_id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(length=64), nullable=False),
        sa.Column('entity', sa.String(length=64)),
        sa.Column('entity_id', sa.String(length=64)),
        sa.Column('perms_snapshot', sa.JSON(), nullable=True),
        sa.Column('meta', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'))
    )
    op.create_index('ix_audit_actor', 'audit_logs', ['actor_user_id'])
    op.create_index('ix_audit_action', 'audit_logs', ['action'])


def downgrade():
    for tbl in ['audit_logs','user_roles','user_groups','group_roles','role_permissions','users','groups','roles','permissions']:
        op.drop_table(tbl)
