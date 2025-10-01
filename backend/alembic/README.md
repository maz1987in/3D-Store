Generic single-database configuration.

## for DB migrations
https://alembic.sqlalchemy.org/en/latest/tutorial.html


# Create Auto Migration:

cd /Users/mazin/Documents/GitHub/3D-Store/backend && source venv/bin/activate && alembic revision --autogenerate -m "create Initial table"

# Create a Migration Script

alembic revision -m "create account table"

---------------
def upgrade():
    op.create_table(
        'account',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('description', sa.Unicode(200)),
    )

def downgrade():
    op.drop_table('account')
-----------------

for adding column
alembic revision -m "Add a column"
---------------
def upgrade():
    op.add_column('account', sa.Column('last_transaction_date', sa.DateTime))

def downgrade():
    op.drop_column('account', 'last_transaction_date')
---------------




# Running Migration
alembic upgrade head

