"""Add admin user

Revision ID: add_admin_user
Revises: add_performance_indexes
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils
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
        sa.column('id', sqlalchemy_utils.types.uuid.UUIDType(binary=False)),
        sa.column('name', sa.String(50)),
        sa.column('description', sa.String(255))
    )
    
    users_table = sa.table('users',
        sa.column('id', sqlalchemy_utils.types.uuid.UUIDType(binary=False)),
        sa.column('username', sa.String(255)),
        sa.column('email', sa.String(255)),
        sa.column('phone', sa.String(255)),
        sa.column('name', sa.String(255)),
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
        sa.column('id', sqlalchemy_utils.types.uuid.UUIDType(binary=False)),
        sa.column('user_id', sqlalchemy_utils.types.uuid.UUIDType(binary=False)),
        sa.column('role_id', sqlalchemy_utils.types.uuid.UUIDType(binary=False))
    )
    
    # Get database connection
    conn = op.get_bind()
    
    # Generate UUIDs
    admin_role_id = uuid.uuid4()
    admin_user_id = uuid.uuid4()
    user_role_id = uuid.uuid4()
    
    # Check if admin role already exists
    result = conn.execute(
        sa.select(roles_table.c.id).where(roles_table.c.name == 'admin')
    ).fetchone()
    
    if result:
        # Role exists, use existing ID
        admin_role_id = result[0]
    else:
        # Create admin role
        conn.execute(
            roles_table.insert().values(
                id=admin_role_id,
                name='admin',
                description='Administrator role with full system access'
            )
        )
    
    # Check if admin user already exists
    result = conn.execute(
        sa.select(users_table.c.id).where(users_table.c.username == 'admin')
    ).fetchone()
    
    if result:
        # User exists, use existing ID
        admin_user_id = result[0]
    else:
        # Create admin user
        conn.execute(
            users_table.insert().values(
                id=admin_user_id,
                username='admin',
                email='admin@store3d.com',
                phone='+1234567890',
                name='System Administrator',
                user_type='ADMIN',
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
            )
        )
    
    # Check if user-role association already exists
    result = conn.execute(
        sa.select(user_roles_table.c.id).where(
            sa.and_(
                user_roles_table.c.user_id == admin_user_id,
                user_roles_table.c.role_id == admin_role_id
            )
        )
    ).fetchone()
    
    if not result:
        # Create user-role association
        conn.execute(
            user_roles_table.insert().values(
                id=user_role_id,
                user_id=admin_user_id,
                role_id=admin_role_id
            )
        )


def downgrade():
    """Remove admin user using SQLAlchemy models."""
    
    # Define table structures using SQLAlchemy
    roles_table = sa.table('roles',
        sa.column('id', sqlalchemy_utils.types.uuid.UUIDType(binary=False)),
        sa.column('name', sa.String(50)),
        sa.column('description', sa.String(255))
    )
    
    users_table = sa.table('users',
        sa.column('id', sqlalchemy_utils.types.uuid.UUIDType(binary=False)),
        sa.column('username', sa.String(255)),
        sa.column('email', sa.String(255)),
        sa.column('phone', sa.String(255)),
        sa.column('name', sa.String(255)),
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
        sa.column('id', sqlalchemy_utils.types.uuid.UUIDType(binary=False)),
        sa.column('user_id', sqlalchemy_utils.types.uuid.UUIDType(binary=False)),
        sa.column('role_id', sqlalchemy_utils.types.uuid.UUIDType(binary=False))
    )
    
    # Get database connection
    conn = op.get_bind()
    
    # Remove user-role associations first
    conn.execute(
        user_roles_table.delete().where(
            user_roles_table.c.user_id.in_(
                sa.select(users_table.c.id).where(users_table.c.username == 'admin')
            )
        )
    )
    
    # Remove admin user
    conn.execute(
        users_table.delete().where(users_table.c.username == 'admin')
    )
    
    # Remove admin role
    conn.execute(
        roles_table.delete().where(roles_table.c.name == 'admin')
    )