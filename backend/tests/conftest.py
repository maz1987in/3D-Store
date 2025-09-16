import os, sys, pytest
# Ensure project root and backend directory are on path so 'app' can be imported
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import create_app, get_db
from app.models.authz import Base, Permission  # ensure Permission model referenced
# Import all model modules to ensure tables are registered before create_all
import app.models.product  # noqa: F401
import app.models.order  # noqa: F401
import app.models.print_job  # noqa: F401
import app.models.accounting_transaction  # noqa: F401
import app.models.catalog_item  # noqa: F401
import app.models.purchase_order  # noqa: F401
import app.models.vendor  # noqa: F401
import app.models.repair_ticket  # noqa: F401

@pytest.fixture(scope='session', autouse=True)
def app_instance():
    os.environ['DATABASE_URL'] = 'sqlite+pysqlite:///:memory:'
    app = create_app()
    # After app and blueprints are registered, ensure all tables exist
    with app.app_context():
        engine = get_db().get_bind()
        Base.metadata.create_all(engine)
    yield app

@pytest.fixture()
def client(app_instance):
    return app_instance.test_client()
