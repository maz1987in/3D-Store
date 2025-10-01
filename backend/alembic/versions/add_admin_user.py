"""Add admin user

Revision ID: add_admin_user
Revises: add_performance_indexes
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash

# revision identifiers, used by Alembic.
revision = 'add_admin_user'
down_revision = 'add_performance_indexes'
branch_labels = None
depends_on = None


def upgrade():
    """Add admin user using pure SQLAlchemy models (database-agnostic)."""
    
    # Define table structures using SQLAlchemy
    roles_table = sa.table('roles',
        sa.column('id', postgresql.UUID(as_uuid=True)),
        sa.column('name', sa.String(50)),
        sa.column('description', sa.String(255))
    )
    
    users_table = sa.table('users',
        sa.column('id', postgresql.UUID(as_uuid=True)),
        sa.column('username', sa.String(50)),
        sa.column('email', sa.String(100)),
        sa.column('phone', sa.String(20)),
        sa.column('name', sa.String(100)),
        sa.column('user_type', sa.String(20)),
        sa.column('language', sa.String(10)),
        sa.column('password', sa.String(255)),
        sa.column('is_active', sa.Boolean),
        sa.column('is_agree', sa.Boolean),
        sa.column('agree_date', sa.DateTime),
        sa.column('mobile_confirmed_at', sa.DateTime),
        sa.column('email_confirmed_at', sa.DateTime),
        sa.column('create_date', sa.DateTime),
        sa.column('modified_date', sa.DateTime),
        sa.column('user_details', sa.JSON)
    )
    
    user_roles_table = sa.table('user_roles',
        sa.column('id', postgresql.UUID(as_uuid=True)),
        sa.column('user_id', postgresql.UUID(as_uuid=True)),
        sa.column('role_id', postgresql.UUID(as_uuid=True))
    )
    
    # Generate UUIDs
    admin_role_id = uuid.uuid4()
    admin_user_id = uuid.uuid4()
    user_role_id = uuid.uuid4()
    
    # Create admin role (with conflict handling)
    op.execute(
        roles_table.insert().values(
            id=admin_role_id,
            name='admin',
            description='Administrator role with full system access'
        ).on_conflict_do_nothing()
    )
    
    # If role already exists, get its ID
    result = op.get_bind().execute(
        sa.select(roles_table.c.id).where(roles_table.c.name == 'admin')
    ).fetchone()
    if result:
        admin_role_id = result[0]
    
    # Create admin user (with conflict handling)
    op.execute(
        users_table.insert().values(
            id=admin_user_id,
            username='admin',
            email='admin@store3d.com',
            phone='+1234567890',
            name='System Administrator',
            user_type='admin',
            language='ENGLISH',
            password=generate_password_hash('admin123'),
            is_active=True,
            is_agree=True,
            agree_date=datetime.now(timezone.utc),
            mobile_confirmed_at=datetime.now(timezone.utc),
            email_confirmed_at=datetime.now(timezone.utc),
            create_date=datetime.now(timezone.utc),
            modified_date=datetime.now(timezone.utc),
            user_details={
                'first_name': 'System',
                'last_name': 'Administrator',
                'department': 'IT',
                'position': 'System Administrator',
                'created_by': 'system'
            }
        ).on_conflict_do_nothing()
    )
    
    # If user already exists, get its ID
    result = op.get_bind().execute(
        sa.select(users_table.c.id).where(users_table.c.username == 'admin')
    ).fetchone()
    if result:
        admin_user_id = result[0]
    
    # Create user-role association (with conflict handling)
    op.execute(
        user_roles_table.insert().values(
            id=user_role_id,
            user_id=admin_user_id,
            role_id=admin_role_id
        ).on_conflict_do_nothing()
    )


def downgrade():
    """Remove admin user using SQLAlchemy models."""
    
    # Define table structures using SQLAlchemy
    roles_table = sa.table('roles',
        sa.column('id', postgresql.UUID(as_uuid=True)),
        sa.column('name', sa.String(50)),
        sa.column('description', sa.String(255))
    )
    
    users_table = sa.table('users',
        sa.column('id', postgresql.UUID(as_uuid=True)),
        sa.column('username', sa.String(50)),
        sa.column('email', sa.String(100)),
        sa.column('phone', sa.String(20)),
        sa.column('name', sa.String(100)),
        sa.column('user_type', sa.String(20)),
        sa.column('language', sa.String(10)),
        sa.column('password', sa.String(255)),
        sa.column('is_active', sa.Boolean),
        sa.column('is_agree', sa.Boolean),
        sa.column('agree_date', sa.DateTime),
        sa.column('mobile_confirmed_at', sa.DateTime),
        sa.column('email_confirmed_at', sa.DateTime),
        sa.column('create_date', sa.DateTime),
        sa.column('modified_date', sa.DateTime),
        sa.column('user_details', sa.JSON)
    )
    
    user_roles_table = sa.table('user_roles',
        sa.column('id', postgresql.UUID(as_uuid=True)),
        sa.column('user_id', postgresql.UUID(as_uuid=True)),
        sa.column('role_id', postgresql.UUID(as_uuid=True))
    )
    
    # Remove user-role associations first
    op.execute(
        user_roles_table.delete().where(
            user_roles_table.c.user_id.in_(
                sa.select(users_table.c.id).where(users_table.c.username == 'admin')
            )
        )
    )
    
    # Remove admin user
    op.execute(
        users_table.delete().where(users_table.c.username == 'admin')
    )
    
    # Remove admin role
    op.execute(
        roles_table.delete().where(roles_table.c.name == 'admin')
    )