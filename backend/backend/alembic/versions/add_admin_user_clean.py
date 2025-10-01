"""Add admin user

Revision ID: add_admin_user_clean
Revises: add_performance_indexes
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import text
import uuid
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash

# revision identifiers, used by Alembic.
revision = 'add_admin_user_clean'
down_revision = 'add_performance_indexes'
branch_labels = None
depends_on = None


def upgrade():
    """Add admin user using SQLAlchemy models."""
    
    # Import models
    from app.users.model import User, Role, UserRoles
    from app.common.enum import UserTypeEnum, LanguageEnum
    
    # Get database connection
    connection = op.get_bind()
    
    # Create admin role
    admin_role = Role(
        id=uuid.uuid4(),
        name='admin',
        description='Administrator role with full system access'
    )
    
    # Insert admin role (with conflict handling)
    try:
        connection.execute(
            text("INSERT INTO roles (id, name, description) VALUES (:id, :name, :description)"),
            {
                'id': str(admin_role.id),
                'name': admin_role.name,
                'description': admin_role.description
            }
        )
    except Exception:
        # Role already exists, get the existing one
        result = connection.execute(
            text("SELECT id FROM roles WHERE name = 'admin'")
        ).fetchone()
        admin_role.id = result[0]
    
    # Create admin user
    admin_user = User(
        id=uuid.uuid4(),
        username='admin',
        email='admin@store3d.com',
        phone='+1234567890',
        name='System Administrator',
        user_type=UserTypeEnum.ADMIN,
        language=LanguageEnum.ENGLISH,
        password=generate_password_hash('admin123'),
        active=True,
        agree=True,
        agree_date=datetime.now(timezone.utc),
        mobile_confirmed_at=datetime.now(timezone.utc),
        email_confirmed_at=datetime.now(timezone.utc),
        user_details={
            'first_name': 'System',
            'last_name': 'Administrator',
            'department': 'IT',
            'position': 'System Administrator',
            'created_by': 'system'
        }
    )
    
    # Insert admin user (with conflict handling)
    try:
        connection.execute(
            text("""
                INSERT INTO users (
                    id, username, email, phone, name, user_type, language, 
                    password, is_active, is_agree, agree_date, 
                    mobile_confirmed_at, email_confirmed_at, create_date, modified_date,
                    user_details
                ) VALUES (
                    :id, :username, :email, :phone, :name, :user_type, :language,
                    :password, :is_active, :is_agree, :agree_date,
                    :mobile_confirmed_at, :email_confirmed_at, :create_date, :modified_date,
                    :user_details
                )
            """),
            {
                'id': str(admin_user.id),
                'username': admin_user.username,
                'email': admin_user.email,
                'phone': admin_user.phone,
                'name': admin_user.name,
                'user_type': admin_user.user_type.value,
                'language': admin_user.language.value,
                'password': admin_user.password,
                'is_active': admin_user.active,
                'is_agree': admin_user.agree,
                'agree_date': admin_user.agree_date,
                'mobile_confirmed_at': admin_user.mobile_confirmed_at,
                'email_confirmed_at': admin_user.email_confirmed_at,
                'create_date': admin_user.create_date,
                'modified_date': admin_user.modified_date,
                'user_details': str(admin_user.user_details).replace("'", '"')
            }
        )
    except Exception:
        # User already exists, get the existing one
        result = connection.execute(
            text("SELECT id FROM users WHERE username = 'admin'")
        ).fetchone()
        admin_user.id = result[0]
    
    # Create user-role association
    user_role = UserRoles(
        id=uuid.uuid4(),
        user_id=admin_user.id,
        role_id=admin_role.id
    )
    
    # Insert user-role association (with conflict handling)
    try:
        connection.execute(
            text("INSERT INTO user_roles (id, user_id, role_id) VALUES (:id, :user_id, :role_id)"),
            {
                'id': str(user_role.id),
                'user_id': str(user_role.user_id),
                'role_id': str(user_role.role_id)
            }
        )
    except Exception:
        # Association already exists, skip
        pass


def downgrade():
    """Remove admin user."""
    
    # Get database connection
    connection = op.get_bind()
    
    # Remove admin user
    connection.execute(text("DELETE FROM users WHERE username = 'admin'"))
    
    # Remove admin role
    connection.execute(text("DELETE FROM roles WHERE name = 'admin'"))
