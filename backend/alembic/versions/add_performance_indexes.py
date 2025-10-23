"""Add performance indexes

Revision ID: add_performance_indexes  
Revises: 2dea99c6ac9d
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_performance_indexes'
down_revision = '2dea99c6ac9d'
branch_labels = None
depends_on = None


def upgrade():
    """
    Performance indexes migration (legacy).
    
    Note: These indexes were manually added. Going forward, add indexes to your 
    SQLAlchemy models using index=True and use 'alembic revision --autogenerate'.
    
    This migration is kept for backward compatibility with existing databases.
    """
    pass  # Indexes already exist in the database


def downgrade():
    """Remove performance indexes."""
    pass  # Keep indexes on downgrade for safety

