from flask import Flask
from werkzeug.exceptions import HTTPException
from flask_jwt_extended import JWTManager
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker, scoped_session
from dotenv import load_dotenv
from typing import Optional, Dict, Any
import os

load_dotenv()

db_engine = None
SessionLocal = None
jwt = JWTManager()


def create_app(config: Optional[Dict[str, Any]] = None):
    global db_engine, SessionLocal
    app = Flask(__name__)

    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-secret')
    app.config['DATABASE_URL'] = os.getenv('DATABASE_URL', 'sqlite:///dev.db')

    if config:
        # allow tests or callers to override default config values
        app.config.update(config)

    # Database
    db_url = app.config['DATABASE_URL']
    if db_url.endswith(':memory:'):
        # Ensure a single shared in-memory SQLite database across all sessions
        db_engine = create_engine(
            db_url,
            echo=False,
            future=True,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    else:
        db_engine = create_engine(db_url, echo=False, future=True)
    SessionLocal = scoped_session(sessionmaker(bind=db_engine, expire_on_commit=False, autoflush=False))

    jwt.init_app(app)

    # Register blueprints (placeholder)
    from .routes.iam import iam_bp  # type: ignore  # remains valid after monorepo restructuring
    from .routes.inventory import inv_bp  # inventory service
    from .routes.sales import sales_bp  # sales service
    from .routes.print import print_bp  # print service
    from .routes.accounting import acc_bp  # accounting service
    from .routes.catalog import cat_bp  # catalog service
    from .routes.purchase_orders import po_bp  # purchase orders service
    from .routes.repairs import rpr_bp  # repairs service
    from .routes.reports import rpt_bp  # reports service
    from .routes.vendors import vendors_bp  # vendors service
    app.register_blueprint(iam_bp, url_prefix='/iam')
    app.register_blueprint(inv_bp, url_prefix='/inventory')
    app.register_blueprint(sales_bp, url_prefix='/sales')
    app.register_blueprint(print_bp, url_prefix='/print')
    app.register_blueprint(acc_bp, url_prefix='/accounting')
    app.register_blueprint(cat_bp, url_prefix='/catalog')
    app.register_blueprint(po_bp, url_prefix='/po')
    app.register_blueprint(rpr_bp, url_prefix='/repairs')
    app.register_blueprint(rpt_bp, url_prefix='/reports')
    app.register_blueprint(vendors_bp, url_prefix='/po')  # vendors under /po namespace (purchase related)

    @app.route('/healthz')
    def health():
        return {'status': 'ok'}

    # Unified error handler producing standardized JSON shape
    @app.errorhandler(Exception)
    def handle_errors(e):  # type: ignore
        if isinstance(e, HTTPException):
            payload = {
                'error': {
                    'status': e.code,
                    'title': e.name,
                    'detail': e.description,
                }
            }
            return payload, e.code
        # Unhandled exception
        app.logger.exception('Unhandled exception')
        return {
            'error': {
                'status': 500,
                'title': 'Internal Server Error',
                'detail': 'Unexpected error'
            }
        }, 500

    # OpenAPI spec route (minimal)
    from .openapi import build_openapi_spec

    @app.route('/openapi.json')
    def openapi_spec():
        return build_openapi_spec()

    @app.route('/docs')
    def docs_index():
        # Lightweight HTML referencing Redoc CDN (no local install) for quick browsing
        return (
            "<!DOCTYPE html><html><head><title>API Docs</title>"
            "<link rel=\"stylesheet\" href=\"https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.css\" />"
            "</head><body><redoc spec-url='/openapi.json'></redoc>"
            "<script src='https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js'></script>"
            "</body></html>"
        )

    return app


def get_db():
    return SessionLocal()
